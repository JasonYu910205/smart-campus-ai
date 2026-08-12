from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    device_code: str
    device_name: str
    device_type: str
    location: str
    manufacturer: str
    model: str
    status: str
    created_at: datetime
    updated_at: datetime
