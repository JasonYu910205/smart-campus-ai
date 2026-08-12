from typing import Protocol


class LLMService(Protocol):
    async def complete(self, messages: list[dict[str, str]]) -> str: ...
