from fastapi import HTTPException

from app.models import Device
from app.repositories.device import DeviceRepository


class DeviceService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    async def list_devices(self, limit: int, offset: int) -> list[Device]:
        return await self.repository.list(limit, offset)

    async def get_device(self, device_id: int) -> Device:
        device = await self.repository.get(device_id)
        if device is None:
            raise HTTPException(status_code=404, detail="Device not found")
        return device
