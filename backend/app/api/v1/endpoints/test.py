from fastapi import APIRouter, Depends
from app.core.config import settings
from app.services.firebase_service import FirebaseService
from app.api.deps import get_current_user
import os

router = APIRouter()

@router.get("/firebase-config")
async def get_firebase_config(current_user: dict = Depends(get_current_user)):
    """Test endpoint to check Firebase configuration"""
    # Force reload settings
    from app.core.config import Settings
    fresh_settings = Settings()
    
    firebase = FirebaseService()
    
    return {
        "env_USE_MOCK": os.getenv('USE_MOCK_FIREBASE'),
        "env_PATH": os.getenv('FIREBASE_CONFIG_PATH'),
        "settings_USE_MOCK": fresh_settings.USE_MOCK_FIREBASE,
        "settings_PATH": fresh_settings.FIREBASE_CONFIG_PATH,
        "firebase_db": str(firebase.db) if firebase.db else "None",
        "firebase_bucket": str(firebase.bucket) if firebase.bucket else "None",
        "is_mock": hasattr(firebase, '_mock_data'),
        "collections": list(firebase._mock_data.keys()) if hasattr(firebase, '_mock_data') else []
    }

@router.post("/create-test-doc")
async def create_test_document(current_user: dict = Depends(get_current_user)):
    """Create a test document in Firestore"""
    firebase = FirebaseService()
    
    test_data = {
        "test": True,
        "user_id": current_user["id"],
        "message": "Test document from API"
    }
    
    try:
        await firebase.save_document("test_collection", "api_test_doc", test_data)
        return {"success": True, "message": "Test document created", "data": test_data}
    except Exception as e:
        return {"success": False, "error": str(e)}