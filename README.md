# multi-agent-stock-screener
An intelligent Stock Screener system powered by Gemini Agents, A2A server, FastMCP and yfinance.

## To get set up
1. Download and install `uv`
2. Create a new virtual environment: `uv venv .venv`
3. Install the repository code as a Python package: `uv pip install .`
4. Set up `configs/env.toml` from `configs/env.toml.dist`:

```
[secrets]
GOOGLE_API_KEY=""  # <- Google AI Studio key or Vertex AI key

[mcp-urls]
YFINANCE=""  # <- URL for yfinance MCP server

[agent-urls]
TECH_ANALYST="http://127.0.0.1:9999"  # <- A2A server endpoint for the Technical Analyst Agent
```

### Start A2A server

`uv run -m stock_screener.a2a_server.server`

### Run A2A test client

**NOTE:** Make sure the MCP server is running before trying to access the remote agent.

`uv run -m stock_screener.a2a_client.test_client`

### Run A2A Host Agent (and Gradio app)

`uv run -m stock_screener.a2a_client.main`

### To run Streamlit app

**NOTE:** Only available for a local Stock Screener agent.

`uv run streamlit run src/stock_screener/streamlit_app/app.py`


## References
- https://github.com/jlowin/fastmcp
- https://google.github.io/adk-docs/
- https://a2a-protocol.org/dev/sdk/python/
- https://github.com/a2aproject/a2a-python
- https://github.com/a2aproject/a2a-samples/tree/main
