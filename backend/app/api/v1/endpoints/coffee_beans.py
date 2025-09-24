from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.schemas.coffee_beans import CoffeeBeanAnalysis, CoffeeBeanResult
from app.services.coffee_beans_service import CoffeeBeansService
from app.api.deps import get_current_user
from datetime import datetime
import base64
import uuid
import asyncio

router = APIRouter()
coffee_beans_service = CoffeeBeansService()

# Store for video processing status
video_processing_status = {}

@router.post("/analyze-test")
async def analyze_coffee_beans_test(
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    field_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """Test endpoint without authentication"""
    # Read image file
    image_data = await file.read()
    
    # Analyze coffee beans
    result = await coffee_beans_service.analyze_beans(image_data)
    
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
        "notes": notes or "",
        "is_video": False
    }
    
    saved_analysis = await coffee_beans_service.save_analysis(analysis_data)
    
    return {
        "id": saved_analysis["id"],
        "analysis": result["analysis"],
        "image_url": result["image_url"],
        "timestamp": result.get("timestamp"),
        "created_at": saved_analysis.get("created_at"),
        "farm_id": saved_analysis.get("farm_id"),
        "field_id": saved_analysis.get("field_id"),
        "notes": saved_analysis.get("notes"),
        "filename": saved_analysis.get("filename"),
        "user_id": saved_analysis.get("user_id"),
        "is_video": saved_analysis.get("is_video", False)
    }

@router.post("/analyze")
async def analyze_coffee_beans(
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    field_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # Read image file
    image_data = await file.read()
    
    # Analyze coffee beans
    result = await coffee_beans_service.analyze_beans(image_data)
    
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
        "is_video": False  # Explicitly set for image analyses
    }
    
    saved_analysis = await coffee_beans_service.save_analysis(analysis_data)
    
    return {
        "id": saved_analysis["id"],
        "analysis": result["analysis"],
        "image_url": result["image_url"],
        "timestamp": result.get("timestamp"),
        "created_at": saved_analysis.get("created_at"),
        "farm_id": saved_analysis.get("farm_id"),
        "field_id": saved_analysis.get("field_id"),
        "notes": saved_analysis.get("notes"),
        "filename": saved_analysis.get("filename"),
        "user_id": saved_analysis.get("user_id"),
        "is_video": saved_analysis.get("is_video", False)
    }

@router.get("/history")
async def get_analysis_history(
    farm_id: Optional[str] = Query(None),
    field_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    history = await coffee_beans_service.get_user_history(
        current_user["id"],
        farm_id=farm_id,
        field_id=field_id
    )
    
    # Format response to match frontend expectations
    formatted_history = []
    for item in history:
        try:
            formatted_history.append({
                "id": item.get("id", ""),
                "analysis": item.get("analysis", {}),
                "image_url": item.get("image_url", ""),
                "video_url": item.get("video_url", ""),
                "is_video": item.get("is_video", False),
                "timestamp": item.get("timestamp"),
                "created_at": item.get("created_at"),
                "farm_id": item.get("farm_id"),
                "field_id": item.get("field_id"),
                "notes": item.get("notes"),
                "filename": item.get("filename"),
                "user_id": item.get("user_id")
            })
        except Exception as e:
            print(f"Error formatting history item: {e}")
            continue
    
    return formatted_history

@router.get("/statistics/{farm_id}")
async def get_farm_statistics(
    farm_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    # Parse dates
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    stats = await coffee_beans_service.get_farm_statistics(farm_id, start, end)
    return stats

@router.get("/{analysis_id}", response_model=CoffeeBeanResult)
async def get_analysis(analysis_id: str, current_user: dict = Depends(get_current_user)):
    analysis = await coffee_beans_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.post("/analyze-video")
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    field_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and analyze a video file for coffee beans detection.
    Returns a job ID for tracking the processing status.
    """
    # Validate file type
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save video file
    video_path = await coffee_beans_service.save_video_file(file, job_id)
    
    # Initialize job status
    video_processing_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "total_frames": 0,
        "processed_frames": 0,
        "results": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
        "farm_id": farm_id,
        "field_id": field_id,
        "notes": notes
    }
    
    # Start background processing
    background_tasks.add_task(
        process_video_background,
        job_id,
        video_path,
        farm_id,
        field_id,
        notes,
        current_user["id"]
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Video processing started. Use the job ID to check status."
    }

@router.get("/video-status/{job_id}")
async def get_video_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get the processing status of a video analysis job."""
    if job_id not in video_processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return video_processing_status[job_id]

@router.get("/video-stream/{job_id}")
async def stream_video_processing(job_id: str, current_user: dict = Depends(get_current_user)):
    """Stream real-time processing updates for a video analysis job."""
    if job_id not in video_processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    async def generate():
        while True:
            status = video_processing_status.get(job_id)
            if not status:
                break
                
            yield f"data: {base64.b64encode(str(status).encode()).decode()}\n\n"
            
            if status["status"] in ["completed", "failed"]:
                break
                
            await asyncio.sleep(0.5)
    
    return StreamingResponse(generate(), media_type="text/event-stream")

async def process_video_background(
    job_id: str,
    video_path: str,
    farm_id: Optional[str],
    field_id: Optional[str],
    notes: Optional[str],
    user_id: str
):
    """Background task to process video file."""
    try:
        # Create event loop for background task if needed
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Process video and get results
        results = await coffee_beans_service.process_video(
            video_path,
            job_id,
            lambda progress: update_job_progress(job_id, progress)
        )
        
        # Check if processing was successful
        if not results.get("success", False):
            raise Exception(results.get("error", "Video processing failed"))
        
        # Save analysis results
        analysis_data = {
            "user_id": user_id,
            "filename": f"video_{job_id}.mp4",
            "analysis": results["summary"],
            "video_url": results["processed_video_url"],
            "farm_id": farm_id or "default_farm",
            "field_id": field_id or "default_field",
            "notes": notes or "",
            "is_video": True,
            "frame_analyses": results["frame_analyses"]
        }
        
        saved_analysis = await coffee_beans_service.save_video_analysis(analysis_data)
        
        # Update job status
        video_processing_status[job_id].update({
            "status": "completed",
            "progress": 100,
            "results": {
                "analysis_id": saved_analysis["id"],
                "summary": results["summary"],
                "processed_video_url": results["processed_video_url"],
                "total_frames_analyzed": results["total_frames"],
                "detection_timeline": results["detection_timeline"]
            }
        })
        
    except Exception as e:
        video_processing_status[job_id].update({
            "status": "failed",
            "error": str(e)
        })

def update_job_progress(job_id: str, progress: dict):
    """Update job progress."""
    if job_id in video_processing_status:
        video_processing_status[job_id].update(progress)

@router.get("/analyses")
async def get_all_analyses(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get all coffee beans analyses"""
    try:
        # Get analyses from Firestore
        analyses = await firebase_service.query_documents(
            "coffee_beans_analyses",
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