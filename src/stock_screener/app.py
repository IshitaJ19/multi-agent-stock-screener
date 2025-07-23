import streamlit as st
import asyncio

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from stock_screener.agents.main_agent import get_agent, ask_agent

st.set_page_config(page_title="Stock Screener", layout="centered")

APP_NAME = "StockScreener"

# -- Setup persistent ADK session, agent, and runner
if "adk_agent" not in st.session_state:

    session_service = InMemorySessionService()

    # Create a session
    session = asyncio.run(session_service.create_session(
        state={},
        app_name=APP_NAME,
        user_id="user",
    ))

    # Create the agent with the tools
    agent = asyncio.run(get_agent())

    # Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    st.session_state.adk_agent = agent
    st.session_state.adk_session = session
    st.session_state.adk_runner = runner


st.title("📈 Natural Language Stock Screener")

user_query = st.text_input(
    "Ask a stock-related question",
    placeholder="e.g., Show me small-cap healthcare stocks with rising revenue",
    key="user_query"
)

if "response" not in st.session_state:
    st.session_state.response = ""

buttons = st.columns([2,6,1])

with buttons[0]:
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            st.session_state["response"] = asyncio.run(ask_agent(
                user_query,
                st.session_state.adk_session,
                st.session_state.adk_runner
            ))
    
with buttons[2]:
    st.button("Clear", on_click=lambda: st.session_state.update({"user_query": ""}))

if st.session_state.response:
    st.markdown("### Response:")
    st.markdown(st.session_state.response)
