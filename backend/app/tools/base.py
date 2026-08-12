from typing import Protocol


class Tool(Protocol):
    name: str
    description: str

    async def run(self, **kwargs: object) -> object: ...
