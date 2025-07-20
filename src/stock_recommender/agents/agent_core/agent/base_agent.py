import os
import datetime
from abc import ABC, abstractmethod
from google import genai
from google.genai import types
from typing import List, Callable, Dict, Any, Optional


# DOCS: https://github.com/googleapis/python-genai


class BaseAgent(ABC):
    """
    Abstract base class for stock recommender agents.
    Provides a structure for integrating Gemini API and tool usage.
    """

    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize the agent with a Gemini model and optional tools.
        """
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        elif "GOOGLE_API_KEY" not in os.environ:
            raise ValueError(
                "Google API Key not found. Please set the GOOGLE_API_KEY "
                "environment variable or pass it to the constructor."
            )
        self.client = genai.Client()
        self.model_name = model_name
        self.mcp_urls: List[str] = []
        self.tools: List[types.Tool] = []
        self._register_default_tools()

    def _register_default_tools(self):
        """Registers any default tools the agent should have."""
        # Example of a default tool
        def get_current_datetime() -> str:
            """Returns the current date and time in a human-readable format."""
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._register_tool(get_current_datetime)

    def _register_tool(self, tool_decl: types.Tool):
        """
        Registers a Python function as a tool for the agent.

        The function's docstring and type hints are used by the model
        to understand its purpose and parameters.

        Args:
            tool_decl (Callable): The function to register as a tool.
        """
        self.tools.append(tool_decl)
        if type(tool_decl) is types.Tool:
            print(f"Tool '{tool_decl.function_declarations[0].name}' registered successfully.")
        else:
            print(f"Tool '{tool_decl.__name__}' registered successfully.")

    @abstractmethod
    def build_tools(self):
        """
        Abstract method to build and return a list of tools.
        Should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def run(self, query: str):
        """
        Abstract method to run the agent on a given query.
        Should be implemented by subclasses.
        """
        pass

    # def 
