from pydantic import BaseModel
from typing import Dict

class FaceImages(BaseModel):
    front: str
    left: str
    right: str

class FaceEnrollRequest(BaseModel):
    farmer_id: str
    images: FaceImages

class FaceEnrollResponse(BaseModel):
    success: bool
    message: str
    embeddings_saved: int

class FaceVerifyRequest(BaseModel):
    image: str

class FaceVerifyResponse(BaseModel):
    success: bool
    farmer: Dict
    confidence: float