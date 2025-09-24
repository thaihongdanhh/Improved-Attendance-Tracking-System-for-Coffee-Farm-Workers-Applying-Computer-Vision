from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AttendanceBase(BaseModel):
    farmer_id: str
    type: str  # check_in or check_out
    confidence: float

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: str
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AttendanceStats(BaseModel):
    total_today: int
    total_week: int
    total_month: int
    average_confidence: float