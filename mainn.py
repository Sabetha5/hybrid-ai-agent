import asyncio
import os
from dotenv import load_dotenv
import re
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rag import create_vector_store, retrieve_relevant_chunks

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),
    },
    args=["firecrawl-mcp"]
)

DECISION_PROMPT = DECISION_PROMPT = """You are an intent classifier.

Rules:
- If user input contains a URL (http, https, or .com/.net/.org) → return SCRAPE
- If user asks general knowledge → return GENERAL
- If user asks about recent or external info → return SEARCH

Return ONLY ONE WORD:
SCRAPE
GENERAL
SEARCH

Do not explain.
"""

FINAL_PROMPT = """Summarize the following website content:
- Keep it short
- Use bullet points
- Max 5 points
"""

def extract_url(user_input):
    user_input = user_input.lower()

    match = re.search(r'https?://[^\s]+', user_input)
    if match:
        return match.group(0)

    match = re.search(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input)
    if match:
        return "https://" + match.group(0)

    return None


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("🚀 Smart Hybrid Agent Ready")
            print("-" * 50)

            while True:
                user_input = input("\nYou: ")

                if user_input.lower() == "quit":
                    print("Goodbye 👋")
                    break

                try:
                    # 🔥 Step 1: Decide intent
                    decision = await model.ainvoke([
                        {"role": "system", "content": DECISION_PROMPT},
                        {"role": "user", "content": user_input}
                    ])

                    intent = decision.content.strip().upper()

                    print("DEBUG INTENT:", intent)

                    # 🔥 Step 2: SCRAPE
                    if "SCRAPE" in intent:
                        url = extract_url(user_input)

                        if not url:
                            print("❌ Could not detect URL")
                            continue

                        print(f"🔧 Scraping: {url}")

                        result = await session.call_tool(
                            "firecrawl_scrape",
                            {"url": url}
                        )

                        raw_data = str(result)
                        trimmed_data = raw_data[:3000]

                        vectorstore = create_vector_store(trimmed_data)
                        context = retrieve_relevant_chunks(vectorstore, user_input)

                        final = await model.ainvoke(
                            [
                            {"role": "system", "content": FINAL_PROMPT},
                            {
                                "role": "user",
                                "content": f"{context}\n\nQuestion: {user_input}"
                            }
    
                            ]
                        )

                        print("\nAgent:", final.content)

                    # 🔥 Step 3: GENERAL
                    elif intent == "GENERAL":
                        response = await model.ainvoke([
                            {"role": "user", "content": user_input}
                        ])
                        print("\nAgent:", response.content)

                    # 🔥 Step 4: SEARCH (fallback)
                    else:
                        print("🔍 Using fallback reasoning...")

                        response = await model.ainvoke([
                            {
                                "role": "user",
                                "content": f"Answer this using general knowledge:\n{user_input}"
                            }
                        ])
                        print("\nAgent:", response.content)

                except Exception as e:
                    print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())