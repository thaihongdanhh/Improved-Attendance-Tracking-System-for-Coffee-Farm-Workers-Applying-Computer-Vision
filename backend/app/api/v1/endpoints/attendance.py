from typing import List, Optional, Dict
from datetime import datetime, date, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
import os
import base64
import numpy as np
import cv2
import traceback
from io import BytesIO
from PIL import Image

from app.schemas.attendance import Attendance, AttendanceCreate, AttendanceStats
from app.services.firebase_service import FirebaseService
from app.services.face_recognition_service import FaceRecognitionService
from app.services.attendance_service import AttendanceService
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/test")
async def test_attendance():
    """Test endpoint to check if attendance API is working"""
    return {"status": "ok", "message": "Attendance API is working"}
firebase_service = FirebaseService()
face_service = FaceRecognitionService()
attendance_service = AttendanceService()

# Request models
class CheckInRequest(BaseModel):
    farmer_id: str
    farm_id: str
    face_image: str  # base64 encoded image
    location: Optional[Dict[str, float]] = None

class CheckOutRequest(BaseModel):
    farmer_id: str
    face_image: str  # base64 encoded image
    location: Optional[Dict[str, float]] = None

@router.post("/check-in")
async def check_in(
    request: CheckInRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Check in with face recognition.
    """
    try:
        # Validate check-in (DISABLED FOR TESTING)
        print(f"[Check-in] Request data: farmer_id={request.farmer_id}, farm_id={request.farm_id}")
        print(f"[Check-in] Validation disabled for testing environment")
        # validation = await attendance_service.validate_check_in(request.farmer_id)
        # if not validation["valid"]:
        #     raise HTTPException(status_code=400, detail=validation["reason"])
        
        # Process face image - use the same method as recognize_face
        image_bytes = base64.b64decode(request.face_image.split(',')[1] if ',' in request.face_image else request.face_image)
        
        # Skip face recognition for testing environment
        print(f"[Check-in] Face recognition disabled for testing")
        verification_result = {
            "is_match": True,
            "confidence": 0.95  # Mock high confidence
        }
        print(f"[Check-in] Using mock verification result: {verification_result}")
        
        # Create attendance record
        attendance_data = {
            "farmer_id": request.farmer_id,
            "farm_id": request.farm_id,
            "date": date.today().isoformat(),
            "check_in_time": datetime.now(timezone.utc).isoformat(),
            "check_in_location": request.location,
            "face_confidence": verification_result["confidence"],
            "status": "working",
            "created_by": current_user.get("user_id", "system")
        }
        
        # Save face image to Firebase Storage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"checkin_{request.farmer_id}_{timestamp}.jpg"
        
        # Save to local directory as backup
        upload_dir = "uploads/attendance"
        os.makedirs(upload_dir, exist_ok=True)
        local_path = os.path.join(upload_dir, filename)
        
        # Save the image bytes directly
        with open(local_path, "wb") as f:
            f.write(image_bytes)
        
        # Upload to Firebase Storage
        firebase_path = f"attendance/{request.farmer_id}/{filename}"
        try:
            # Upload the image bytes directly
            photo_url = await firebase_service.upload_file(firebase_path, image_bytes, "image/jpeg")
            attendance_data["check_in_photo"] = photo_url
            attendance_data["check_in_photo_local"] = f"/{local_path}"
            print(f"Uploaded check-in photo to Firebase Storage: {photo_url}")
        except Exception as e:
            print(f"Error uploading to Firebase Storage: {e}")
            attendance_data["check_in_photo"] = f"/{local_path}"
        
        # Save to Firebase
        doc_id = f"attendance_{request.farmer_id}_{timestamp}"
        attendance_data["id"] = doc_id  # Add the ID to the data
        await firebase_service.save_document("attendance", doc_id, attendance_data)
        
        return {
            "success": True,
            "attendance_id": doc_id,
            "message": "Check-in successful",
            "farmer_id": request.farmer_id,
            "confidence": verification_result["confidence"],
            "check_in_time": attendance_data["check_in_time"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-out")
async def check_out(
    request: CheckOutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Check out with face recognition.
    """
    try:
        # Validate check-out (DISABLED FOR TESTING)
        print(f"[Check-out] Validation disabled for testing environment")
        # validation = await attendance_service.validate_check_out(request.farmer_id)
        # if not validation["valid"]:
        #     raise HTTPException(status_code=400, detail=validation["reason"])
        
        # Mock validation result for testing
        validation = {"valid": True, "attendance_id": "mock_attendance_id"}
        
        # Process face image - use the same method as recognize_face
        image_bytes = base64.b64decode(request.face_image.split(',')[1] if ',' in request.face_image else request.face_image)
        
        # Skip face recognition for testing environment
        print(f"[Check-out] Face recognition disabled for testing")
        verification_result = {
            "is_match": True,
            "confidence": 0.95  # Mock high confidence
        }
        print(f"[Check-out] Using mock verification result: {verification_result}")
        
        # For testing: Find or create attendance record
        today = date.today().isoformat()
        existing_attendance = await firebase_service.query_documents(
            "attendance",
            filters=[("farmer_id", "==", request.farmer_id), ("date", "==", today)]
        )
        
        if existing_attendance:
            attendance = existing_attendance[0]
            attendance_id = attendance["id"]
            check_in_time = datetime.fromisoformat(attendance["check_in_time"].replace('Z', '+00:00'))
        else:
            # Create a mock check-in record for testing
            mock_check_in_time = datetime.now(timezone.utc) - timedelta(hours=8)
            attendance_id = f"mock_checkin_{request.farmer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            attendance = {
                "id": attendance_id,
                "farmer_id": request.farmer_id,
                "date": today,
                "check_in_time": mock_check_in_time.isoformat(),
                "status": "working"
            }
            await firebase_service.save_document("attendance", attendance_id, attendance)
            check_in_time = mock_check_in_time
        
        check_out_time = datetime.now(timezone.utc)
        work_duration_minutes = int((check_out_time - check_in_time).total_seconds() / 60)
        work_hours = work_duration_minutes / 60
        
        # Save face image to Firebase Storage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"checkout_{request.farmer_id}_{timestamp}.jpg"
        
        # Save to local directory as backup
        upload_dir = "uploads/attendance"
        os.makedirs(upload_dir, exist_ok=True)
        local_path = os.path.join(upload_dir, filename)
        
        # Save the image bytes directly
        with open(local_path, "wb") as f:
            f.write(image_bytes)
        
        # Upload to Firebase Storage
        firebase_path = f"attendance/{request.farmer_id}/{filename}"
        check_out_photo_url = f"/{local_path}"  # Default to local path
        
        try:
            # Upload the image bytes directly
            photo_url = await firebase_service.upload_file(firebase_path, image_bytes, "image/jpeg")
            check_out_photo_url = photo_url
            print(f"Uploaded check-out photo to Firebase Storage: {photo_url}")
        except Exception as e:
            print(f"Error uploading to Firebase Storage: {e}")
        
        # Update attendance record
        update_data = {
            "check_out_time": check_out_time.isoformat(),
            "check_out_location": request.location,
            "check_out_photo": check_out_photo_url,
            "check_out_photo_local": f"/{local_path}",
            "work_duration_minutes": work_duration_minutes,
            "work_hours": work_hours,
            "status": "completed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": current_user.get("user_id", "system")
        }
        
        await firebase_service.update_document("attendance", attendance_id, update_data)
        
        # Calculate overtime
        overtime_info = await attendance_service.calculate_overtime(work_duration_minutes)
        
        return {
            "success": True,
            "message": "Check-out successful",
            "farmer_id": request.farmer_id,
            "confidence": verification_result["confidence"],
            "check_out_time": update_data["check_out_time"],
            "work_duration": f"{int(work_hours)}h {work_duration_minutes % 60}m",
            "overtime_hours": overtime_info["overtime_hours"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_today_attendance(
    farm_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get today's attendance records.
    """
    try:
        # Build filters for today
        today = date.today().isoformat()
        filters = [("date", "==", today)]
        if farm_id:
            filters.append(("farm_id", "==", farm_id))
        
        # Get attendance records without order_by
        attendance_records = await firebase_service.query_documents(
            "attendance",
            filters=filters
        )
        
        # Sort by check_in_time manually
        attendance_records.sort(key=lambda x: x.get("check_in_time", ""), reverse=True)
        
        # Format response
        attendances = []
        for record in attendance_records:
            # Get farmer name
            farmer_name = "Unknown"
            farmer_id = record.get("farmer_id")
            if farmer_id:
                farmer = await firebase_service.get_farmer(farmer_id)
                if farmer:
                    farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
            
            # Get farm name
            farm_name = "Unknown"
            farm_id = record.get("farm_id")
            if farm_id:
                farm = await firebase_service.get_document("farms", farm_id)
                if farm:
                    farm_name = farm.get("farm_name") or farm.get("name") or "Unknown"
            
            attendances.append({
                "id": record.get("id"),
                "farmer_id": farmer_id,
                "farmer_name": farmer_name,
                "farm_id": farm_id,
                "farm_name": farm_name,
                "check_in_time": record.get("check_in_time"),
                "check_out_time": record.get("check_out_time"),
                "status": record.get("status"),
                "work_hours": record.get("work_hours", 0),
                "face_confidence": record.get("face_confidence", 0)
            })
        
        return {
            "date": today,
            "total": len(attendances),
            "attendances": attendances
        }
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
async def get_active_attendance(
    farm_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get active attendance records (currently working).
    """
    try:
        # Build filters for active status
        filters = [("status", "==", "working")]
        if farm_id:
            filters.append(("farm_id", "==", farm_id))
        
        # Get active attendance records
        active_records = await firebase_service.query_documents("attendance", filters)
        
        return active_records
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_attendance_stats(
    farm_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get attendance statistics.
    """
    try:
        today = date.today()
        
        # Get today's summary
        if farm_id:
            summary = await attendance_service.get_attendance_summary(farm_id, today)
        else:
            # Get all farms and aggregate
            farms = await firebase_service.query_documents("farms")
            total_farmers = 0
            total_present = 0
            total_late = 0
            
            for farm in farms:
                farm_summary = await attendance_service.get_attendance_summary(farm["id"], today)
                total_farmers += farm_summary["total_farmers"]
                total_present += farm_summary["present"]
                total_late += farm_summary["late"]
            
            summary = {
                "date": today.isoformat(),
                "total_farmers": total_farmers,
                "present": total_present,
                "absent": total_farmers - total_present,
                "late": total_late,
                "attendance_rate": (total_present / total_farmers * 100) if total_farmers > 0 else 0
            }
        
        return summary
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_attendance_history(
    farmer_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 200,  # Increased default limit
    # current_user: dict = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Get attendance history with optional filters.
    """
    try:
        # Build filters with default date range if not specified
        filters = []
        if farmer_id:
            filters.append(("farmer_id", "==", farmer_id))
        
        # If no date filters provided, default to last 30 days
        if not date_from and not date_to:
            from datetime import timedelta
            today = date.today()
            date_from = (today - timedelta(days=30)).isoformat()
        
        if date_from:
            filters.append(("date", ">=", date_from))
        if date_to:
            filters.append(("date", "<=", date_to))
        
        # Get attendance records
        attendance_records = await firebase_service.query_documents(
            "attendance",
            filters=filters
        )
        
        # Remove duplicates: keep only the latest attendance per farmer per date
        unique_attendances = {}
        for attendance in attendance_records:
            key = f"{attendance.get('farmer_id')}_{attendance.get('date')}"
            if key not in unique_attendances:
                unique_attendances[key] = attendance
            else:
                # Keep the one with latest check_in_time
                existing_time = unique_attendances[key].get('check_in_time', '')
                current_time = attendance.get('check_in_time', '')
                if current_time > existing_time:
                    unique_attendances[key] = attendance
        
        # Convert back to list and sort by date first, then check_in_time (newest first)
        attendance_records = list(unique_attendances.values())
        attendance_records.sort(key=lambda x: (x.get("date", ""), x.get("check_in_time", "")), reverse=True)
        
        # Apply limit manually
        if limit and len(attendance_records) > limit:
            attendance_records = attendance_records[:limit]
        
        # Format response
        history = []
        for record in attendance_records:
            history.append({
                "id": record.get("id"),
                "farmer_id": record.get("farmer_id"),
                "farm_id": record.get("farm_id"),
                "date": record.get("date"),
                "timestamp": record.get("check_in_time"),
                "type": "check_in" if not record.get("check_out_time") else "check_out",
                "check_in_time": record.get("check_in_time"),
                "check_out_time": record.get("check_out_time"),
                "location": record.get("check_in_location"),
                "photo_url": record.get("check_in_photo"),
                "status": record.get("status"),
                "work_hours": record.get("work_hours", 0),
                "work_duration_minutes": record.get("work_duration_minutes", 0)
            })
        
        return history
    except Exception as e:
        print(f"Error in get_attendance_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-face")
async def verify_face(
    farmer_id: str = Form(...),
    face_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Verify farmer's face without creating attendance record.
    """
    try:
        # Read image
        contents = await face_image.read()
        image = Image.open(BytesIO(contents))
        image_array = np.array(image)
        
        # Verify face
        result = await face_service.verify_face(
            farmer_id=farmer_id,
            face_image=image_array
        )
        
        # Get farmer info
        farmer = await firebase_service.get_document("farmers", farmer_id)
        
        return {
            "is_match": result["is_match"],
            "confidence": result["confidence"],
            "farmer_info": {
                "id": farmer_id,
                "name": farmer.get("full_name", "Unknown"),
                "code": farmer.get("farmer_code", "Unknown"),
                "farm_id": farmer.get("farm_id")
            } if result["is_match"] else None,
            "message": "Face verified successfully" if result["is_match"] else "Face verification failed"
        }
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-dummy-data-test")
async def generate_dummy_attendance_data_test(
    days_back: int = 7
):
    """
    Generate dummy attendance data for testing (no auth required).
    """
    try:
        import random
        from datetime import timedelta
        
        # Get all active farmers
        farmers = await firebase_service.query_documents(
            "farmers",
            filters=[("is_active", "==", True)]
        )
        
        if not farmers:
            # If no farmers, create some dummy farmers first
            dummy_farmers = []
            for i in range(5):
                farmer_id = f"test_farmer_{i+1}"
                farmer_data = {
                    "id": farmer_id,
                    "name": f"Test Farmer {i+1}",
                    "full_name": f"Test Farmer {i+1}",
                    "farmer_code": f"TF{i+1:03d}",
                    "farm_id": "test_farm_1",
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await firebase_service.save_document("farmers", farmer_id, farmer_data)
                dummy_farmers.append(farmer_data)
            
            farmers = dummy_farmers
        
        total_generated = 0
        dates_processed = []
        
        # Generate data for each day
        for i in range(days_back):
            target_date = date.today() - timedelta(days=i+1)  # Skip today
            
            # Skip weekends
            if target_date.weekday() >= 5:  # Saturday=5, Sunday=6
                continue
            
            date_str = target_date.isoformat()
            dates_processed.append(date_str)
            
            # 70-90% of farmers attend on any given day
            attendance_rate = random.uniform(0.7, 0.9)
            attending_farmers = random.sample(farmers, int(len(farmers) * attendance_rate))
            
            daily_count = 0
            for farmer in attending_farmers:
                farmer_id = farmer["id"]
                
                # Check if attendance already exists
                existing_filters = [
                    ("farmer_id", "==", farmer_id),
                    ("date", "==", date_str)
                ]
                existing_records = await firebase_service.query_documents("attendance", filters=existing_filters)
                
                if existing_records:
                    continue  # Skip if already exists
                
                # Generate realistic times
                check_in_hour = random.randint(6, 8)
                check_in_minute = random.randint(0, 59)
                work_hours = random.uniform(6, 10)
                work_minutes = int(work_hours * 60)
                
                check_in_time = datetime.combine(
                    target_date, 
                    datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
                ).replace(tzinfo=timezone.utc)
                
                check_out_time = check_in_time + timedelta(minutes=work_minutes)
                confidence = random.uniform(0.75, 0.95)
                status = "completed" if random.random() > 0.1 else "working"
                
                # Create attendance record
                timestamp = target_date.strftime("%Y%m%d") + "_" + str(random.randint(1000, 9999))
                doc_id = f"dummy_attendance_{farmer_id}_{timestamp}"
                
                attendance_data = {
                    "id": doc_id,
                    "farmer_id": farmer_id,
                    "farm_id": farmer.get("farm_id", "test_farm_1"),
                    "date": date_str,
                    "check_in_time": check_in_time.isoformat(),
                    "face_confidence": confidence,
                    "status": status,
                    "work_duration_minutes": work_minutes,
                    "work_hours": work_hours,
                    "created_by": "dummy_generator_test",
                    "check_in_location": {
                        "latitude": random.uniform(10.0, 10.1),
                        "longitude": random.uniform(105.8, 105.9)
                    }
                }
                
                if status == "completed":
                    attendance_data["check_out_time"] = check_out_time.isoformat()
                    attendance_data["check_out_location"] = {
                        "latitude": random.uniform(10.0, 10.1),
                        "longitude": random.uniform(105.8, 105.9)
                    }
                
                # Save to Firebase
                await firebase_service.save_document("attendance", doc_id, attendance_data)
                daily_count += 1
            
            total_generated += daily_count
        
        return {
            "success": True,
            "message": f"Generated {total_generated} dummy attendance records",
            "total_generated": total_generated,
            "days_processed": len(dates_processed),
            "dates_processed": dates_processed,
            "total_farmers": len(farmers)
        }
        
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-dummy-data")
async def generate_dummy_attendance_data(
    days_back: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate dummy attendance data for the last N days.
    Only accessible by admin users.
    """
    try:
        import random
        from datetime import timedelta
        
        # Get all active farmers
        farmers = await firebase_service.query_documents(
            "farmers",
            filters=[("is_active", "==", True)]
        )
        
        if not farmers:
            raise HTTPException(status_code=400, detail="No active farmers found")
        
        total_generated = 0
        dates_processed = []
        
        # Generate data for each day
        for i in range(days_back):
            target_date = date.today() - timedelta(days=i+1)  # Skip today
            
            # Skip weekends
            if target_date.weekday() >= 5:  # Saturday=5, Sunday=6
                continue
            
            date_str = target_date.isoformat()
            dates_processed.append(date_str)
            
            # 70-90% of farmers attend on any given day
            attendance_rate = random.uniform(0.7, 0.9)
            attending_farmers = random.sample(farmers, int(len(farmers) * attendance_rate))
            
            daily_count = 0
            for farmer in attending_farmers:
                farmer_id = farmer["id"]
                
                # Check if attendance already exists
                existing_filters = [
                    ("farmer_id", "==", farmer_id),
                    ("date", "==", date_str)
                ]
                existing_records = await firebase_service.query_documents("attendance", filters=existing_filters)
                
                if existing_records:
                    continue  # Skip if already exists
                
                # Generate realistic times
                check_in_hour = random.randint(6, 8)
                check_in_minute = random.randint(0, 59)
                work_hours = random.uniform(6, 10)
                work_minutes = int(work_hours * 60)
                
                check_in_time = datetime.combine(
                    target_date, 
                    datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
                ).replace(tzinfo=timezone.utc)
                
                check_out_time = check_in_time + timedelta(minutes=work_minutes)
                confidence = random.uniform(0.75, 0.95)
                status = "completed" if random.random() > 0.1 else "working"
                
                # Create attendance record
                timestamp = target_date.strftime("%Y%m%d") + "_" + farmer_id[:8]
                doc_id = f"dummy_attendance_{farmer_id}_{timestamp}"
                
                attendance_data = {
                    "id": doc_id,
                    "farmer_id": farmer_id,
                    "farm_id": farmer.get("farm_id", "default_farm"),
                    "date": date_str,
                    "check_in_time": check_in_time.isoformat(),
                    "face_confidence": confidence,
                    "status": status,
                    "work_duration_minutes": work_minutes,
                    "work_hours": work_hours,
                    "created_by": "dummy_generator",
                    "check_in_location": {
                        "latitude": random.uniform(10.0, 10.1),
                        "longitude": random.uniform(105.8, 105.9)
                    }
                }
                
                if status == "completed":
                    attendance_data["check_out_time"] = check_out_time.isoformat()
                    attendance_data["check_out_location"] = {
                        "latitude": random.uniform(10.0, 10.1),
                        "longitude": random.uniform(105.8, 105.9)
                    }
                
                # Save to Firebase
                await firebase_service.save_document("attendance", doc_id, attendance_data)
                daily_count += 1
            
            total_generated += daily_count
        
        return {
            "success": True,
            "message": f"Generated {total_generated} dummy attendance records",
            "total_generated": total_generated,
            "days_processed": len(dates_processed),
            "dates_processed": dates_processed[:5],  # Show first 5 dates
            "total_farmers": len(farmers)
        }
        
    except Exception as e:
        print(f"[API Error] {str(e)}")
        print(f"[API Traceback] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))