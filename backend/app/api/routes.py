from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.dashboard import DashboardRepository
from app.repositories.device import DeviceRepository
from app.schemas.dashboard import DashboardStats
from app.schemas.device import DeviceRead
from app.services.device import DeviceService
from app.services.health import service_health

router = APIRouter(prefix="/api")
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("/health")
async def health(session: SessionDependency) -> dict[str, str]:
    return await service_health(session)


@router.get("/devices", response_model=list[DeviceRead])
async def devices(
    session: SessionDependency,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[DeviceRead]:
    records = await DeviceService(DeviceRepository(session)).list_devices(limit, offset)
    return [DeviceRead.model_validate(record) for record in records]


@router.get("/devices/{device_id}", response_model=DeviceRead)
async def device(device_id: int, session: SessionDependency) -> DeviceRead:
    record = await DeviceService(DeviceRepository(session)).get_device(device_id)
    return DeviceRead.model_validate(record)


@router.get("/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats(session: SessionDependency) -> DashboardStats:
    device_count, inspections, maintenance, suppliers = await DashboardRepository(session).counts()
    return DashboardStats(
        device_count=device_count,
        today_inspection_count=inspections,
        pending_maintenance_count=maintenance,
        supplier_count=suppliers,
    )
