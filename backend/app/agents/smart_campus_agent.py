from app.services.llm import LLMService
from app.tools.base import Tool


class SmartCampusAgent:
    """V0.1 composition boundary; tool selection is implemented in V0.4."""

    def __init__(self, llm: LLMService, tools: list[Tool]):
        self.llm, self.tools = llm, tools
