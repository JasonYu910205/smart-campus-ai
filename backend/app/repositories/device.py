from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Device


class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, limit: int = 100, offset: int = 0) -> list[Device]:
        result = await self.session.scalars(
            select(Device).order_by(Device.id).limit(limit).offset(offset)
        )
        return list(result)

    async def get(self, device_id: int) -> Device | None:
        return await self.session.get(Device, device_id)
