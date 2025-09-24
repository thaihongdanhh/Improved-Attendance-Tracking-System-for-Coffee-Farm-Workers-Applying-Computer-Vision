from fastapi import APIRouter, Depends, HTTPException
from app.services.firebase_service import FirebaseService
from datetime import datetime

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_statistics(
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get dashboard statistics"""
    try:
        # Get farmers statistics
        farmers = await firebase.get_farmers()
        farmers_with_face = [f for f in farmers if f.get('face_enrolled', False) or f.get('has_face_enrolled', False)]
        
        # Get attendance statistics for today
        today = datetime.now().strftime("%Y-%m-%d")
        attendances = await firebase.get_attendance_by_date(today)
        active_attendances = [a for a in attendances if a.get('status') == 'working']
        completed_attendances = [a for a in attendances if a.get('status') == 'completed']
        
        # Get farms statistics
        farms = await firebase.get_farms()
        
        return {
            "farmers": {
                "total": len(farmers),
                "active": len([f for f in farmers if f.get('is_active', True)]),
                "with_face_enrolled": len(farmers_with_face),
                "enrollment_rate": len(farmers_with_face) / len(farmers) if farmers else 0
            },
            "attendances": {
                "today": len(attendances),
                "active": len(active_attendances),
                "checked_out_today": len(completed_attendances),
                "attendance_rate": len(attendances) / len(farmers) if farmers else 0
            },
            "farms": {
                "total": len(farms),
                "active": len([f for f in farms if f.get('is_active', True)])
            },
            "system": {
                "mode": "mock" if firebase.db is None else "production",
                "face_service": "mock" if firebase.db is None else "production",
                "database": "mock" if firebase.db is None else "firebase"
            }
        }
    except Exception as e:
        print(f"Error getting dashboard statistics: {e}")
        # Return default values on error
        return {
            "farmers": {
                "total": 0,
                "active": 0,
                "with_face_enrolled": 0,
                "enrollment_rate": 0
            },
            "attendances": {
                "today": 0,
                "active": 0,
                "checked_out_today": 0,
                "attendance_rate": 0
            },
            "farms": {
                "total": 0,
                "active": 0
            },
            "system": {
                "mode": "mock" if firebase.db is None else "production",
                "face_service": "mock" if firebase.db is None else "production",
                "database": "mock" if firebase.db is None else "firebase"
            }
        }

@router.get("/summary")
async def get_summary_statistics(
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get summary statistics"""
    dashboard_stats = await get_dashboard_statistics(firebase)
    
    total_entities = (
        dashboard_stats["farmers"]["total"] + 
        dashboard_stats["farms"]["total"] + 
        dashboard_stats["attendances"]["today"]
    )
    
    return {
        **dashboard_stats,
        "summary": {
            "total_entities": total_entities,
            "system_health": "healthy" if total_entities > 0 else "empty",
            "last_updated": datetime.now().isoformat()
        }
    }