from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from stock_screener.a2a_server.technical_analyst_agent import TechnicalAnalystAgent


capabilities = AgentCapabilities(streaming=False)

technical_signal_skill = AgentSkill(
    id="technical_stock_signals",
    name="Returns technical signals for a stock",
    description="Performs technical analysis on a stock and provides its technical signals",
    tags=["technical", "analysis", "bullish", "bearish"],
    examples=[
        "Run technical analysis for stock TSLA",
        "Is the stock JNJ bullish or bearish right now?",
        "What are the technical signals like for INTL?"
    ]
)

technical_stock_screening_skill = AgentSkill(
    id="technical_stock_screener",
    name="Returns bullish stocks",
    description="Performs technical analysis on all stocks in a given list of stock ticker symbols, \
        and returns all bullish stocks from that list",
    tags=["technical", "analysis", "bullish", "bearish"],
    examples=[
        "Perform technical analysis on: TSLA, INTC, GOOGL, META."
    ]   
)

public_agent_card = AgentCard(
    name="Technical Analyst Agent",
    description="Main agent for stock screening based on technical indicators.",
    url="http://localhost:9999/",
    version="1.0.0",
    default_input_modes=TechnicalAnalystAgent.SUPPORTED_CONTENT_TYPES,
    default_output_modes=TechnicalAnalystAgent.SUPPORTED_CONTENT_TYPES,
    capabilities=capabilities,
    skills=[technical_signal_skill, technical_stock_screening_skill],
    # supports_authenticated_extended_card=True,
)
