from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.genai import types

from stock_screener.utils.read_env_vars import ENV


class TechnicalAnalystAgent:
    """Agent for performing technical analysis of stocks"""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "application/json"]

    def __init__(self, mcp_url: str = ENV.mcp_urls.get("YFINANCE")):
        """Initialize the Stock Screener Agent with necessary tools."""

        self._agent = self._build_agent(mcp_url)
        self._user_id = "user_1"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService()
        )


    def _build_agent(self, mcp_url: str = ENV.mcp_urls.get("YFINANCE")) -> LlmAgent:
        """Build the main agent with the necessary tools and sub-agents."""
        
        toolset = self._get_tools(mcp_url)

        agent = LlmAgent(
            name="TechnicalAnalystAgent",
            description="Main agent for stock screening based on technical indicator.",
            instruction="""You are a financial analyst. 
            Use the tools provided to answer stock-related queries and perform technical analysis. 
            Use tabular format wherever possible.""",
            model="gemini-2.5-flash",
            tools=[toolset]
        )
        return agent
    

    def _get_tools(self, mcp_url: str = ENV.mcp_urls.get("YFINANCE")) -> MCPToolset:
        """Return the tools available in the agent."""
        
        toolset = MCPToolset(
            connection_params=StreamableHTTPServerParams(url=mcp_url),
            tool_filter=[
                "get_technical_signals",
                "screen_bullish_stocks"
            ]
        )
        return toolset
    

    async def ask(self, user_query: str, session_id: str) -> str:
        """Ask the agent a question and return the response."""
        
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id
        )
            
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={}
            )

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_query)]
        )

        last_event = None

        events_async = self._runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        )

        for event in events_async:
            last_event = event
        
        if not last_event or not last_event.content or not last_event.content.parts:
            return ""
        return "\n".join([p.text for p in last_event.content.parts if p.text])
    