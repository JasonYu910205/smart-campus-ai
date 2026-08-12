from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Device, InspectionRecord, MaintenanceOrder, Supplier


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def counts(self) -> tuple[int, int, int, int]:
        today = datetime.now(UTC).date()
        queries = [
            select(func.count()).select_from(Device),
            select(func.count())
            .select_from(InspectionRecord)
            .where(func.date(InspectionRecord.inspected_at) == today),
            select(func.count())
            .select_from(MaintenanceOrder)
            .where(MaintenanceOrder.status.in_(["pending", "in_progress"])),
            select(func.count()).select_from(Supplier),
        ]
        values = [int((await self.session.scalar(q)) or 0) for q in queries]
        return values[0], values[1], values[2], values[3]
