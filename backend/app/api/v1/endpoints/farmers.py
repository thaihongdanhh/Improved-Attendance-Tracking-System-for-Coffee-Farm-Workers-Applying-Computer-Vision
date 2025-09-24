from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.farmer import Farmer, FarmerCreate, FarmerUpdate
from app.services.firebase_service import FirebaseService
from app.api.deps import get_current_user

router = APIRouter()
firebase_service = FirebaseService()

@router.get("/", response_model=List[Farmer])
async def get_farmers(current_user: dict = Depends(get_current_user)):
    farmers = await firebase_service.get_farmers()
    # Transform data to match schema
    transformed_farmers = []
    for farmer in farmers:
        # Map full_name to name if needed
        if 'full_name' in farmer and 'name' not in farmer:
            farmer['name'] = farmer['full_name']
        # Map has_face_enrolled to face_enrolled
        if 'has_face_enrolled' in farmer:
            farmer['face_enrolled'] = farmer['has_face_enrolled']
        # Map updatedAt to updated_at
        if 'updatedAt' in farmer and 'updated_at' not in farmer:
            farmer['updated_at'] = farmer['updatedAt']
        # Ensure email exists (even if empty)
        if 'email' not in farmer:
            farmer['email'] = None
        transformed_farmers.append(farmer)
    return transformed_farmers

@router.get("/{farmer_id}", response_model=Farmer)
async def get_farmer(farmer_id: str, current_user: dict = Depends(get_current_user)):
    farmer = await firebase_service.get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Transform data to match schema
    if 'full_name' in farmer and 'name' not in farmer:
        farmer['name'] = farmer['full_name']
    if 'has_face_enrolled' in farmer:
        farmer['face_enrolled'] = farmer['has_face_enrolled']
    if 'updatedAt' in farmer and 'updated_at' not in farmer:
        farmer['updated_at'] = farmer['updatedAt']
    if 'email' not in farmer:
        farmer['email'] = None
        
    return farmer

@router.post("/", response_model=Farmer)
async def create_farmer(farmer_data: FarmerCreate, current_user: dict = Depends(get_current_user)):
    farmer = await firebase_service.create_farmer(farmer_data.dict())
    return farmer

@router.put("/{farmer_id}", response_model=Farmer)
async def update_farmer(
    farmer_id: str,
    farmer_data: FarmerUpdate,
    current_user: dict = Depends(get_current_user)
):
    farmer = await firebase_service.update_farmer(farmer_id, farmer_data.dict(exclude_unset=True))
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer

@router.delete("/{farmer_id}")
async def delete_farmer(farmer_id: str, current_user: dict = Depends(get_current_user)):
    success = await firebase_service.delete_farmer(farmer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return {"message": "Farmer deleted successfully"}

@router.get("/{farmer_id}/attendances")
async def get_farmer_attendances(
    farmer_id: str,
    limit: int = 100,  # Increased default limit
    offset: int = 0,
    date_from: str = None,
    date_to: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get attendance records for a specific farmer with improved filtering"""
    from datetime import date, timedelta
    
    # Get farmer details first
    farmer = await firebase_service.get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Build filters with default date range
    filters = [("farmer_id", "==", farmer_id)]
    
    # If no date filters provided, default to last 60 days for farmer detail
    if not date_from and not date_to:
        today = date.today()
        date_from = (today - timedelta(days=60)).isoformat()
    
    if date_from:
        filters.append(("date", ">=", date_from))
    if date_to:
        filters.append(("date", "<=", date_to))
    
    # Get attendance records for this farmer
    attendances = await firebase_service.query_documents(
        "attendance",
        filters=filters
    )
    
    # Remove duplicates: keep only the latest attendance per farmer per date
    unique_attendances = {}
    for attendance in attendances:
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
    attendances = list(unique_attendances.values())
    attendances.sort(key=lambda x: (x.get("date", ""), x.get("check_in_time", "")), reverse=True)
    
    # Apply offset and limit
    paginated_attendances = attendances[offset:offset + limit] if limit else attendances[offset:]
    
    return {
        "farmer_id": farmer_id,
        "farmer_name": farmer.get("name") or farmer.get("full_name") or "Unknown",
        "from_date": attendances[-1].get("date") if attendances else None,
        "to_date": attendances[0].get("date") if attendances else None,
        "total_records": len(attendances),
        "limit": limit,
        "offset": offset,
        "attendances": paginated_attendances
    }