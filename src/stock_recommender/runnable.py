from typing import List, Dict, Callable, Any
import asyncio

from google.genai import types
from fastmcp import Client

from stock_recommender.agents.agent_core.agent.base_agent import BaseAgent
from stock_recommender.utils.read_env_vars import ENV

class MainAgent(BaseAgent):
    """Main agent class for stock recommendation using Gemini API."""
    
    def __init__(self, model_name: str, api_key: str = None, mcp_urls: List[str] = None):
        """Initialize the agent with a Gemini model and optional tools."""

        super().__init__(model_name, api_key)
        self.mcp_urls = mcp_urls if mcp_urls else [ENV.mcp_urls]

    async def build_tools(self) -> None:
        # Implement tool building logic
        for mcp_url in self.mcp_urls.values():
            try:
                mcp_tool_declarations = await self.get_mcp_tools(mcp_url)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize fastmcp client: {e}")
            
            for tool in mcp_tool_declarations:
                # Define tool declaration
                tool_decl = types.Tool(
                    function_declarations=[
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                self._register_tool(tool_decl)

            print(f"Registered {len(mcp_tool_declarations)} tools from MCP server: {mcp_url}")

    async def get_mcp_tools(sef, mcp_url: str) -> List:
        """Fetch tools from the specified MCP URL."""

        async with Client(mcp_url) as client:
            tools = await client.list_tools()
            print(f"Available tools from {mcp_url}: {tools}")
        return tools

    async def run(self, query: str):
        """Run the agent on a given query."""
  
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=query,
            config=types.GenerateContentConfig(
                tools=self.tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
                temperature=0.0
            )
        )   

        if response.function_calls:
            print(f"Function calls: {response.function_calls}")
            
            for function in response.function_calls:
                async with Client(self.mcp_urls.get("YFINANCE")) as client:
                    result = await client.call_tool(
                        function.name, arguments=dict(function.args)
)               
                return result

        return response 
    

async def main():
    """Main function to run the agent."""
    
    import os

    ENV.export_google_api_key()
    
    agent = MainAgent(
        model_name="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        mcp_urls=ENV.mcp_urls
    )

    await agent.build_tools()

    response = await agent.run("Give me the gross margins for Apple (AAPL)?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())


