from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from app.schemas.coffee_leaves import CoffeeLeafAnalysis, CoffeeLeafResult
from app.services.coffee_leaves_service import CoffeeLeavesService
from app.services.firebase_service import FirebaseService
from app.api.deps import get_current_user
from datetime import datetime

router = APIRouter()
coffee_leaves_service = CoffeeLeavesService()
firebase_service = FirebaseService()

@router.post("/analyze-test")
async def analyze_coffee_leaves_test(
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    field_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """Test endpoint without authentication"""
    # Read image file
    image_data = await file.read()
    
    # Analyze coffee leaves
    result = await coffee_leaves_service.analyze_leaves(image_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Save analysis to database with farm/field info
    analysis_data = {
        "user_id": "test_user",  # Use test user for unauthenticated requests
        "filename": file.filename,
        "analysis": result["analysis"],
        "image_url": result["image_url"],
        "farm_id": farm_id or "default_farm",
        "field_id": field_id or "default_field",
        "notes": notes or ""
    }
    
    saved_analysis = await coffee_leaves_service.save_analysis(analysis_data)
    
    return {
        "id": saved_analysis["id"],
        "analysis": result["analysis"],
        "image_url": result["image_url"],
        "created_at": saved_analysis.get("created_at"),
        "farm_id": saved_analysis.get("farm_id"),
        "field_id": saved_analysis.get("field_id"),
        "notes": saved_analysis.get("notes"),
        "filename": saved_analysis.get("filename"),
        "user_id": saved_analysis.get("user_id")
    }

@router.post("/analyze", response_model=CoffeeLeafResult)
async def analyze_coffee_leaves(
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    field_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # Read image file
    image_data = await file.read()
    
    # Analyze coffee leaves
    result = await coffee_leaves_service.analyze_leaves(image_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Save analysis to database with farm/field info
    analysis_data = {
        "user_id": current_user["id"],
        "filename": file.filename,
        "analysis": result["analysis"],
        "image_url": result["image_url"],
        "farm_id": farm_id or "default_farm",
        "field_id": field_id or "default_field",
        "notes": notes or "",
        "timestamp": result.get("timestamp")
    }
    
    saved_analysis = await coffee_leaves_service.save_analysis(analysis_data)
    
    return {
        "id": saved_analysis["id"],
        "analysis": result["analysis"],
        "image_url": result["image_url"],
        "timestamp": result.get("timestamp"),
        "created_at": saved_analysis["created_at"]
    }

@router.get("/history", response_model=List[CoffeeLeafResult])
async def get_analysis_history(
    farm_id: Optional[str] = Query(None),
    field_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    history = await coffee_leaves_service.get_user_history(
        current_user["id"],
        farm_id=farm_id,
        field_id=field_id
    )
    return history

@router.get("/analyses")
async def get_all_analyses(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all coffee leaves analyses"""
    try:
        # Get analyses from Firestore
        analyses = await firebase_service.query_documents(
            "coffee_leaves_analyses",
            limit=limit
        )
        
        # Sort manually by created_at
        analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return analyses
    except Exception as e:
        print(f"Error getting analyses: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{analysis_id}", response_model=CoffeeLeafResult)
async def get_analysis(analysis_id: str, current_user: dict = Depends(get_current_user)):
    analysis = await coffee_leaves_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis