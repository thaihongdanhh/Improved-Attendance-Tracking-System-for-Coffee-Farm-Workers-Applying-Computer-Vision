from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.farm import Farm, FarmCreate, FarmUpdate
from app.services.farm_service import FarmService
from app.services.firebase_service import FirebaseService
from app.api.deps import get_current_user
from datetime import datetime, timezone
import random

router = APIRouter()
farm_service = FarmService()

@router.get("/test-simple")
async def get_farms_simple():
    """Get all farms directly from Firebase (no auth required for testing)"""
    try:
        firebase_service = FirebaseService()
        farms = await firebase_service.query_documents("farms")
        return {
            "success": True,
            "count": len(farms),
            "farms": farms[:10] if farms else []  # Limit to first 10
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/", response_model=List[Farm])
async def get_farms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    # current_user: dict = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get all farms with optional search"""
    try:
        firebase_service = FirebaseService()
        farms = await firebase_service.query_documents("farms")
        return farms[:limit] if farms else []
    except Exception as e:
        print(f"Error getting farms: {str(e)}")
        return []

@router.get("/{farm_id}", response_model=Farm)
async def get_farm(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific farm by ID"""
    farm = await farm_service.get_farm(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.post("/", response_model=Farm)
async def create_farm(
    farm_data: FarmCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new farm"""
    # Check if user has admin role
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create farms")
    
    farm = await farm_service.create_farm(farm_data.dict())
    return farm

@router.put("/{farm_id}", response_model=Farm)
async def update_farm(
    farm_id: str,
    farm_data: FarmUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a farm"""
    # Check if user has admin role
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update farms")
    
    farm = await farm_service.update_farm(farm_id, farm_data.dict(exclude_unset=True))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.delete("/{farm_id}")
async def delete_farm(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a farm"""
    # Check if user has admin role
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete farms")
    
    success = await farm_service.delete_farm(farm_id)
    if not success:
        raise HTTPException(status_code=404, detail="Farm not found")
    return {"message": "Farm deleted successfully"}

@router.get("/{farm_id}/fields/")
async def get_farm_fields(
    farm_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all fields for a specific farm"""
    farm = await farm_service.get_farm(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm.get("fields", [])

@router.get("/nearby/{latitude}/{longitude}")
async def get_nearby_farms(
    latitude: float,
    longitude: float,
    radius_km: float = Query(10, ge=0.1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get farms within a certain radius of coordinates"""
    farms = await farm_service.get_nearby_farms(latitude, longitude, radius_km)
    return farms

@router.post("/generate-dummy-farms-test")
async def generate_dummy_farms_test():
    """
    Generate dummy farm data for testing (no auth required).
    """
    try:
        firebase_service = FirebaseService()
        
        # Check if farms already exist
        existing_farms = await firebase_service.query_documents("farms")
        if len(existing_farms) >= 5:
            return {
                "success": True,
                "message": f"Already have {len(existing_farms)} farms in database",
                "existing_farms": [f.get("farm_name", f.get("id", "Unknown")) for f in existing_farms[:5]]
            }
        
        # Generate dummy farms around Ho Chi Minh City area
        dummy_farms = [
            {
                "id": "test_farm_1",
                "farm_code": "CF001",
                "farm_name": "Green Coffee Farm",
                "location": {
                    "lat": 10.0503 + random.uniform(-0.02, 0.02),
                    "lng": 105.8425 + random.uniform(-0.02, 0.02)
                },
                "address": "District 1, Ho Chi Minh City",
                "area_hectares": random.uniform(5.0, 15.0),
                "manager_name": "Nguyen Van A",
                "contact_phone": "0901234567",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "test_farm_2", 
                "farm_code": "CF002",
                "farm_name": "Highland Coffee Plantation",
                "location": {
                    "lat": 10.0503 + random.uniform(-0.03, 0.03),
                    "lng": 105.8425 + random.uniform(-0.03, 0.03)
                },
                "address": "District 2, Ho Chi Minh City",
                "area_hectares": random.uniform(8.0, 20.0),
                "manager_name": "Tran Thi B",
                "contact_phone": "0987654321",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "test_farm_3",
                "farm_code": "CF003", 
                "farm_name": "Sunrise Coffee Estate",
                "location": {
                    "lat": 10.0503 + random.uniform(-0.025, 0.025),
                    "lng": 105.8425 + random.uniform(-0.025, 0.025)
                },
                "address": "District 7, Ho Chi Minh City",
                "area_hectares": random.uniform(6.0, 18.0),
                "manager_name": "Le Van C",
                "contact_phone": "0912345678",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "test_farm_4",
                "farm_code": "CF004",
                "farm_name": "Mountain View Coffee",
                "location": {
                    "lat": 10.0503 + random.uniform(-0.015, 0.015),
                    "lng": 105.8425 + random.uniform(-0.015, 0.015)
                },
                "address": "Thu Duc City, Ho Chi Minh City",
                "area_hectares": random.uniform(4.0, 12.0),
                "manager_name": "Pham Thi D",
                "contact_phone": "0923456789",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "test_farm_5",
                "farm_code": "CF005",
                "farm_name": "Golden Bean Farm",
                "location": {
                    "lat": 10.0503 + random.uniform(-0.035, 0.035),
                    "lng": 105.8425 + random.uniform(-0.035, 0.035)
                },
                "address": "District 9, Ho Chi Minh City",
                "area_hectares": random.uniform(7.0, 16.0),
                "manager_name": "Hoang Van E",
                "contact_phone": "0934567890",
                "is_active": False,  # One inactive farm
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Save farms to Firebase
        created_count = 0
        for farm_data in dummy_farms:
            farm_id = farm_data["id"]
            await firebase_service.save_document("farms", farm_id, farm_data)
            created_count += 1
        
        return {
            "success": True,
            "message": f"Generated {created_count} dummy farms",
            "farms_created": [f.get("farm_name", "Unknown") for f in dummy_farms]
        }
        
    except Exception as e:
        print(f"Error generating dummy farms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))