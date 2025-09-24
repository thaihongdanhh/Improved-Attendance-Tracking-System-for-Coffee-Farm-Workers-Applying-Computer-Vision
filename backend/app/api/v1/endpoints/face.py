from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel
import traceback
from app.schemas.face import FaceEnrollRequest, FaceEnrollResponse
from app.services.face_recognition_service import FaceRecognitionService
from app.services.firebase_service import FirebaseService
from app.api.deps import get_current_user
from app.utils.image_utils import base64_to_image, validate_image
import base64

# Request model for face quality check
class FaceQualityRequest(BaseModel):
    image: str  # base64 encoded image
    expected_angle: Optional[str] = None  # "front", "left", or "right"

# Request model for face verification
class FaceVerifyRequest(BaseModel):
    image: str  # base64 encoded image

router = APIRouter()
face_service = FaceRecognitionService()
firebase_service = FirebaseService()

@router.post("/enroll", response_model=FaceEnrollResponse)
async def enroll_face(
    enrollment_data: FaceEnrollRequest,
    current_user: dict = Depends(get_current_user)
):
    # Verify farmer exists
    farmer = await firebase_service.get_farmer(enrollment_data.farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Check if overwriting existing enrollment
    is_overwriting = farmer.get("face_enrolled", False)
    
    embeddings_saved = 0
    uploaded_images = []
    
    # Process each angle
    for angle, image_data in enrollment_data.images.dict().items():
        if not image_data:
            continue
            
        # Extract base64 data
        if image_data.startswith('data:'):
            image_data = image_data.split(',')[1]
        
        # Convert to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Validate image
        is_valid, error_msg = validate_image(image_bytes)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid {angle} image: {error_msg}")
        
        # Save image to Firebase Storage
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"faces/{enrollment_data.farmer_id}/{angle}_{timestamp}.jpg"
        
        try:
            image_url = await firebase_service.upload_file(file_path, image_bytes, "image/jpeg")
            uploaded_images.append({"angle": angle, "url": image_url})
            print(f"Uploaded {angle} image to Firebase Storage: {image_url}")
        except Exception as e:
            print(f"Error uploading {angle} image to Firebase Storage: {e}")
        
        # Enroll face
        result = await face_service.enroll_face(
            farmer_id=enrollment_data.farmer_id,
            image_data=image_bytes,
            angle=angle
        )
        
        if result["success"]:
            embeddings_saved += 1
    
    if embeddings_saved == 0:
        raise HTTPException(status_code=400, detail="No faces could be enrolled")
    
    # Update farmer's face_enrolled status and store image URLs
    update_data = {
        "face_enrolled": True,
        "face_images": uploaded_images,
        "face_enrollment_date": datetime.now().isoformat()
    }
    
    await firebase_service.update_farmer(
        enrollment_data.farmer_id,
        update_data
    )
    
    message = f"Successfully {'updated' if is_overwriting else 'enrolled'} face with {embeddings_saved} angles"
    
    return {
        "success": True,
        "message": message,
        "embeddings_saved": embeddings_saved,
        "uploaded_images": uploaded_images,
        "farmer_id": enrollment_data.farmer_id,
        "was_update": is_overwriting
    }

@router.post("/verify")
async def verify_face(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Read image bytes
    image_bytes = await image.read()
    
    # Validate image
    is_valid, error_msg = validate_image(image_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid image: {error_msg}")
    
    # Perform face recognition
    result = await face_service.recognize_face(image_bytes)
    
    if result["success"]:
        # Get farmer details
        farmer = await firebase_service.get_farmer(result["farmer_id"])
        return {
            "verified": True,
            "farmer_id": result["farmer_id"],
            "farmer_name": farmer.get("name") or farmer.get("full_name") or "Unknown" if farmer else "Unknown",
            "confidence": result["confidence"],
            "message": "Face verified successfully"
        }
    else:
        return {
            "verified": False,
            "message": result["message"]
        }

@router.post("/quality")
async def check_face_quality(
    image: UploadFile = File(...)
    # Temporarily remove auth requirement for testing
    # current_user: dict = Depends(get_current_user)
):
    """
    Check face quality for enrollment suitability
    """
    try:
        # Log request details
        print(f"Received face quality check request")
        print(f"Image filename: {image.filename}")
        print(f"Image content type: {image.content_type}")
        
        # Read image bytes
        image_bytes = await image.read()
        print(f"Image size: {len(image_bytes)} bytes")
        
        # Validate image
        is_valid, error_msg = validate_image(image_bytes)
        if not is_valid:
            return {
                "face_detected": False,
                "message": f"Invalid image: {error_msg}"
            }
        
        # Analyze face quality
        quality_result = await face_service.check_face_quality(image_bytes, expected_angle=request.expected_angle)
        
        return quality_result
    except Exception as e:
        print(f"Error in check_face_quality: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "face_detected": False,
                "message": f"Error processing image: {str(e)}"
            }
        )

@router.post("/quality-json")
async def check_face_quality_json(
    request: FaceQualityRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Check face quality for enrollment suitability (JSON version)
    """
    try:
        # Extract base64 data
        image_data = request.image
        if image_data.startswith('data:'):
            image_data = image_data.split(',')[1]
        
        # Convert to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Validate image
        is_valid, error_msg = validate_image(image_bytes)
        if not is_valid:
            return {
                "face_detected": False,
                "message": f"Invalid image: {error_msg}"
            }
        
        # Analyze face quality
        quality_result = await face_service.check_face_quality(image_bytes, expected_angle=request.expected_angle)
        
        return quality_result
    except Exception as e:
        print(f"Error in check_face_quality_json: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "face_detected": False,
            "message": f"Error processing image: {str(e)}"
        }

@router.post("/verify-json")
async def verify_face_json(
    request: FaceVerifyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify face using JSON request with base64 image
    """
    try:
        # Extract base64 data
        image_data = request.image
        if image_data.startswith('data:'):
            image_data = image_data.split(',')[1]
        
        # Convert to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Validate image
        is_valid, error_msg = validate_image(image_bytes)
        if not is_valid:
            return {
                "verified": False,
                "message": f"Invalid image: {error_msg}"
            }
        
        # Perform face recognition
        result = await face_service.recognize_face(image_bytes)
        
        if result["success"]:
            # Get farmer details
            farmer = await firebase_service.get_farmer(result["farmer_id"])
            return {
                "verified": True,
                "farmer_id": result["farmer_id"],
                "farmer_name": farmer.get("name") or farmer.get("full_name") or "Unknown" if farmer else "Unknown",
                "farm_id": farmer.get("farm_id") if farmer else None,
                "confidence": result["confidence"],
                "message": "Face verified successfully"
            }
        else:
            return {
                "verified": False,
                "message": result.get("message", "Face not recognized")
            }
    except Exception as e:
        print(f"Error in verify_face_json: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "verified": False,
            "message": f"Error processing image: {str(e)}"
        }