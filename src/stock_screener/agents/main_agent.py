import asyncio

from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.genai import types

from stock_screener.utils.read_env_vars import ENV


ENV.export_google_api_key()

APP_NAME = "StockScreener"


async def get_agent(
        mcp_url: str = ENV.mcp_urls.get("YFINANCE")
    ) -> LlmAgent:

    toolset = MCPToolset(
        connection_params=StreamableHTTPServerParams(url=mcp_url),
        tool_filter=[
            "get_gross_margins",
            "screen_stocks",
            "get_market_cap",
            "get_ticker_financials",
            "get_stock_info"
        ]
    )

    root_agent = LlmAgent(
        name="MainAgent",
        description="Main agent for stock screening.",
        instruction="""You are a financial assistant. 
        Use the tools provided to answer stock-related queries. Use tabular format wherever possible. 
        Recommend stock when asked, and let the user know that the advice is for educational purposes only.""",
        model="gemini-2.5-flash",
        tools=[toolset],
        include_contents="default",
    )
    return root_agent   


async def run_agent():
    """Run the agent with a session."""

    session_service = InMemorySessionService()

    # Create a session
    session = await session_service.create_session(
        state={},
        app_name=APP_NAME,
        user_id="user",
    )

    # Create the agent with the tools
    agent = await get_agent()

    print("Agent created with tools")

    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    print("\n--- Simulating First User Interaction (New Session) ---")

    print("Agent: How may I help you today?")

    events_async = None

    while True:

        user_input = input("User: ")
    
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the session.")
            await runner.close()
            break

        # Format the user's input into the required Content object
        user_content = types.Content(role='user', parts=[types.Part(text=user_input)])
        
        try: 
            events_async = runner.run_async(
                session_id=session.id, 
                user_id=session.user_id,
                new_message=user_content
            )

            # Process events
            async for event in events_async:

                if event.is_final_response():
                    if event.content and event.content.parts:
                        # Assuming text response in the first part
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                        final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                        break

            print(f"Agent: {final_response_text}")

        except asyncio.CancelledError:
            print("Stream was cancelled.")

        except Exception as e:
            print(f"Unexpected error during tool streaming: {e}")



async def ask_agent(user_query: str, session, runner) -> str:
    """Ask the agent a question and return the response."""

    from google.genai import types

    events_async = None

    if user_query.lower() in ["exit", "quit"]:
        await runner.close()
        return "Exiting the session."

    # Format the user's input into the required Content object
    user_content = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    try: 
        events_async = runner.run_async(
            session_id=session.id, 
            user_id=session.user_id,
            new_message=user_content
        )

        # Process events
        async for event in events_async:

            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text

                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                
                await runner.close()
                return final_response_text

    except asyncio.CancelledError:
        return Exception("Stream was cancelled.")

    except Exception as e:
        return Exception(f"Unexpected error during tool streaming: {e}")


if __name__ == "__main__":

    import asyncio

    asyncio.run(run_agent())
   
    