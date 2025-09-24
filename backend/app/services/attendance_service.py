from typing import Dict, List, Optional
from datetime import datetime, date, timedelta, timezone
import logging

from app.services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

class AttendanceService:
    """Service for attendance management with daily validation"""
    
    def __init__(self):
        self.db_service = FirebaseService()
    
    async def validate_check_in(self, farmer_id: str) -> Dict:
        """Validate if farmer can check in - enhanced with daily check"""
        # Check if already checked in today (regardless of status)
        today = date.today()
        today_attendance = await self.get_today_attendance_for_farmer(farmer_id, today)
        
        if today_attendance:
            if today_attendance.get('status') == 'working':
                return {
                    "valid": False,
                    "reason": "Already checked in. Please check out first.",
                    "active_attendance_id": today_attendance["id"]
                }
            elif today_attendance.get('status') == 'completed':
                return {
                    "valid": False,
                    "reason": "Already completed work for today. You can only check in once per day.",
                    "attendance_id": today_attendance["id"],
                    "check_in_time": today_attendance.get("check_in_time"),
                    "check_out_time": today_attendance.get("check_out_time")
                }
        
        return {"valid": True}
    
    async def get_today_attendance_for_farmer(self, farmer_id: str, target_date: date) -> Optional[Dict]:
        """Get attendance record for a specific farmer on a specific date"""
        try:
            date_str = target_date.isoformat()
            
            # Query attendance for farmer on specific date
            filters = [
                ("farmer_id", "==", farmer_id),
                ("date", "==", date_str)
            ]
            
            records = await self.db_service.query_documents(
                "attendance",
                filters=filters
            )
            
            if records:
                return records[0]
            
            return None
        except Exception as e:
            logger.error(f"Error getting today's attendance for farmer: {e}")
            return None
    
    async def validate_check_out(self, farmer_id: str) -> Dict:
        """Validate if farmer can check out"""
        # Check if has active check-in today
        today = date.today()
        today_attendance = await self.get_today_attendance_for_farmer(farmer_id, today)
        
        if not today_attendance:
            return {
                "valid": False,
                "reason": "No check-in found for today"
            }
        
        if today_attendance.get('status') != 'working':
            return {
                "valid": False,
                "reason": "Already checked out for today"
            }
        
        # Check minimum work duration (optional)
        check_in_time = today_attendance["check_in_time"]
        if isinstance(check_in_time, str):
            check_in_time = datetime.fromisoformat(check_in_time.replace('Z', '+00:00'))
        
        duration_minutes = (datetime.now(timezone.utc) - check_in_time).total_seconds() / 60
        
        if duration_minutes < 5:  # Minimum 5 minutes
            return {
                "valid": False,
                "reason": f"Too early to check out (minimum 5 minutes, worked {int(duration_minutes)} minutes)"
            }
        
        return {
            "valid": True,
            "attendance_id": today_attendance["id"]
        }
    
    async def calculate_overtime(self, work_duration_minutes: int) -> Dict:
        """Calculate overtime based on work duration"""
        standard_hours = 8
        standard_minutes = standard_hours * 60
        
        if work_duration_minutes <= standard_minutes:
            return {
                "regular_hours": work_duration_minutes / 60,
                "overtime_hours": 0,
                "total_hours": work_duration_minutes / 60
            }
        else:
            overtime_minutes = work_duration_minutes - standard_minutes
            return {
                "regular_hours": standard_hours,
                "overtime_hours": overtime_minutes / 60,
                "total_hours": work_duration_minutes / 60
            }
    
    async def get_attendance_summary(self, farm_id: str, target_date: date) -> Dict:
        """Get attendance summary for a farm on specific date"""
        try:
            date_str = target_date.isoformat()
            
            # Get all farmers for the farm
            farmers = await self.db_service.query_documents(
                "farmers",
                filters=[("farm_id", "==", farm_id), ("is_active", "==", True)]
            )
            total_farmers = len(farmers)
            
            # Get attendance records for the date
            present = 0
            late = 0
            overtime = 0
            
            for farmer in farmers:
                attendance = await self.get_today_attendance_for_farmer(farmer['id'], target_date)
                if attendance:
                    present += 1
                    
                    # Check if late (after 8 AM)
                    check_in_time = attendance.get('check_in_time')
                    if isinstance(check_in_time, str):
                        check_in_time = datetime.fromisoformat(check_in_time.replace('Z', '+00:00'))
                    
                    if check_in_time.hour >= 8:
                        late += 1
                    
                    # Check overtime
                    if attendance.get('work_duration_minutes', 0) > 480:  # 8 hours
                        overtime += 1
            
            attendance_rate = (present / total_farmers * 100) if total_farmers > 0 else 0
            
            return {
                "farm_id": farm_id,
                "date": date_str,
                "total_farmers": total_farmers,
                "present": present,
                "absent": total_farmers - present,
                "late": late,
                "overtime": overtime,
                "attendance_rate": round(attendance_rate, 2)
            }
        except Exception as e:
            logger.error(f"Error getting attendance summary: {e}")
            return {
                "farm_id": farm_id,
                "date": target_date.isoformat(),
                "total_farmers": 0,
                "present": 0,
                "absent": 0,
                "late": 0,
                "overtime": 0,
                "attendance_rate": 0.0
            }