from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY":os.getenv("FIRECRAWL_API_KEY"),
    },
    args=["firecrawl-mcp"]
)

SYSTEM_PROMPT = """You are a helpful assistant that uses tools like firecrawl.

IMPORTANT:
- Always follow tool schema strictly
- Only pass required parameters
- For firecrawl_scrape, use:
  { "url": "..." }

- Extract only key info
- Summarize immediately
- NEVER return full page content
CRITICAL:
- When using firecrawl, DO NOT return full content
- Extract only top 5 important points
- Limit output to MAX 500 words
- Summarize immediately after scraping

Think step by step and keep responses SHORT
"""

async def main():
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model,tools)

            print("Available Tools-",*[tool.name for tool in tools])
            print("-" * 60)

            while True:
                user_input = input("\nYou: ")
                if user_input == "quit":
                    print("Goodbye")
                    break
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ]


                try:
                    agent_response = await agent.ainvoke({
    "messages": messages[-5:]   
})

                    ai_message = agent_response["messages"][-1].content
                    print("\nAgent:", ai_message)
                except Exception as e:
                    print("Error:",e)

if __name__ == "__main__":
    asyncio.run(main())
