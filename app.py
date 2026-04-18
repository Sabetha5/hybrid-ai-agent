from fastapi import FastAPI
from pydantic import BaseModel
import os
import re
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rag import create_vector_store, retrieve_relevant_chunks

load_dotenv()

app = FastAPI()

# 🔥 Model
model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# 🔥 MCP Server
server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),
    },
    args=["firecrawl-mcp"]
)

# 🔥 Request schema
class ChatRequest(BaseModel):
    message: str
    pdf_text: str | None = None


# 🔥 Prompts
DECISION_PROMPT = """You are an intent classifier.

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


# 🔥 URL extractor
def extract_url(user_input):
    user_input = user_input.lower()

    match = re.search(r'https?://[^\s]+', user_input)
    if match:
        return match.group(0)

    match = re.search(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input)
    if match:
        return "https://" + match.group(0)

    return None


# 🔥 MAIN API
@app.post("/chat")
async def chat(req: ChatRequest):
    user_input = req.message

    try:
        # =====================================================
        # 🔥 1. PDF RAG (PRIORITY)
        # =====================================================
        if req.pdf_text:
            vectorstore = create_vector_store(req.pdf_text[:3000])
            context = retrieve_relevant_chunks(vectorstore, user_input)

            final = await model.ainvoke([
                {"role": "system", "content": FINAL_PROMPT},
                {
                    "role": "user",
                    "content": f"{context}\n\nQuestion: {user_input}"
                }
            ])

            return {"response": final.content}

        # =====================================================
        # 🔥 2. INTENT DETECTION
        # =====================================================
        decision = await model.ainvoke([
            {"role": "system", "content": DECISION_PROMPT},
            {"role": "user", "content": user_input}
        ])

        intent = decision.content.strip().upper()
        print("DEBUG INTENT:", intent)

        # =====================================================
        # 🔥 3. SCRAPE FLOW
        # =====================================================
        if "SCRAPE" in intent:
            url = extract_url(user_input)

            if not url:
                return {"response": "❌ Could not detect URL"}

            print(f"🔧 Scraping: {url}")

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool(
                        "firecrawl_scrape",
                        {"url": url}
                    )

                    raw_data = str(result)
                    trimmed_data = raw_data[:3000]

                    vectorstore = create_vector_store(trimmed_data)
                    context = retrieve_relevant_chunks(vectorstore, user_input)

                    final = await model.ainvoke([
                        {"role": "system", "content": FINAL_PROMPT},
                        {
                            "role": "user",
                            "content": f"{context}\n\nQuestion: {user_input}"
                        }
                    ])

                    return {"response": final.content}

        # =====================================================
        # 🔥 4. GENERAL
        # =====================================================
        elif "GENERAL" in intent:
            response = await model.ainvoke([
                {"role": "user", "content": user_input}
            ])

            return {"response": response.content}

        # =====================================================
        # 🔥 5. FALLBACK (SEARCH)
        # =====================================================
        else:
            response = await model.ainvoke([
                {
                    "role": "user",
                    "content": f"Answer this using general knowledge:\n{user_input}"
                }
            ])

            return {"response": response.content}

    except Exception as e:
        return {"error": str(e)}