import tomllib
import os
from typing import Union
from pathlib import Path

from stock_screener.utils.paths import CONFIGS_DIR


class EnvVars:
    def __init__(self, config_path: Union[str, Path]=CONFIGS_DIR / "env.toml"):
        """Initialize environment variables from a TOML file."""
        with open(config_path, "rb") as f:
            env_vars = tomllib.load(f)

        self.google_api_key = env_vars.get("secrets", {}).get("GOOGLE_API_KEY", "")
        self.mcp_urls = env_vars.get("mcp-urls", [])
        agent_urls = env_vars.get("agent-urls", {})
        self.agent_urls = [agent_urls[key] for key in agent_urls]
    
    def export_google_api_key(self):
        """Export the Google API key."""
        os.environ["GOOGLE_API_KEY"] = self.google_api_key
        
    
ENV = EnvVars()

