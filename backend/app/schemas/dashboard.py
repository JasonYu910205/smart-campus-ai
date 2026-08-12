from pydantic import BaseModel


class DashboardStats(BaseModel):
    device_count: int
    today_inspection_count: int
    pending_maintenance_count: int
    supplier_count: int
