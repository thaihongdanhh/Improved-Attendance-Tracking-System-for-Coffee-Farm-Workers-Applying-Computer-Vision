import numpy as np
import cv2
from typing import Dict, Optional
from app.core.config import settings
import os
from datetime import datetime

# Conditional imports for ML libraries
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("Warning: ONNX Runtime not installed. Face recognition will use mock mode.")

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("Warning: InsightFace not installed. Face recognition will use mock mode.")

class FaceRecognitionService:
    def __init__(self):
        if INSIGHTFACE_AVAILABLE:
            try:
                # Use the downloaded model path from settings
                self.app = FaceAnalysis(
                    name='buffalo_l',
                    root=os.path.dirname(settings.INSIGHTFACE_MODEL_PATH),
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
                )
                self.app.prepare(ctx_id=0, det_size=(640, 640))
                print(f"✅ InsightFace loaded from: {settings.INSIGHTFACE_MODEL_PATH}")
            except Exception as e:
                print(f"❌ Failed to load InsightFace model: {e}")
                self.app = None
        else:
            self.app = None
        
        # Initialize ONNX model if exists
        if ONNX_AVAILABLE and os.path.exists(settings.ONNX_MODEL_PATH):
            self.session = ort.InferenceSession(
                settings.ONNX_MODEL_PATH,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
        else:
            self.session = None
        
        # In production, load face embeddings from database
        self.face_embeddings = {}
        self.mock_mode = not (INSIGHTFACE_AVAILABLE and self.app is not None)
        
    async def _load_all_embeddings_from_firebase(self):
        """Load all face embeddings from Firebase"""
        try:
            from app.services.firebase_service import FirebaseService
            firebase = FirebaseService()
            
            # Get all embeddings
            embeddings_docs = await firebase.query_documents("face_embeddings")
            
            for doc in embeddings_docs:
                if "farmer_id" in doc and "angle" in doc and "embedding" in doc:
                    key = f"{doc['farmer_id']}_{doc['angle']}"
                    # Convert list back to numpy array
                    self.face_embeddings[key] = np.array(doc["embedding"])
            
            print(f"Loaded {len(self.face_embeddings)} face embeddings from Firebase")
        except Exception as e:
            print(f"Error loading embeddings from Firebase: {e}")

    async def extract_face_embedding(self, image_data: bytes) -> Optional[np.ndarray]:
        if self.mock_mode:
            # Return mock embedding
            return np.random.rand(512)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print(f"[extract_face_embedding] Failed to decode image")
            return None
        
        print(f"[extract_face_embedding] Image shape: {img.shape}")
        
        # Detect faces
        faces = self.app.get(img)
        print(f"[extract_face_embedding] Detected {len(faces)} faces")
        
        if len(faces) == 0:
            return None
        
        # Get the largest face
        face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
        
        return face.embedding

    async def recognize_face(self, image_data: bytes) -> Dict:
        embedding = await self.extract_face_embedding(image_data)
        
        if embedding is None:
            return {
                "success": False,
                "message": "No face detected in the image"
            }
        
        # Load all embeddings from Firebase if cache is empty
        if len(self.face_embeddings) == 0:
            await self._load_all_embeddings_from_firebase()
        
        # Compare with stored embeddings
        best_match = None
        best_similarity = -1
        farmer_scores = {}
        
        # Group embeddings by farmer
        for key, stored_embedding in self.face_embeddings.items():
            farmer_id = key.split('_')[0]  # Extract farmer_id from key
            similarity = np.dot(embedding, stored_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(stored_embedding))
            
            if farmer_id not in farmer_scores:
                farmer_scores[farmer_id] = []
            farmer_scores[farmer_id].append(similarity)
        
        # Calculate average similarity for each farmer
        print(f"[Face Recognition] Comparing with {len(farmer_scores)} farmers")
        for farmer_id, scores in farmer_scores.items():
            avg_similarity = np.mean(scores)
            print(f"[Face Recognition] Farmer {farmer_id}: similarity = {avg_similarity:.3f}")
            if avg_similarity > best_similarity and avg_similarity > 0.6:  # Threshold
                best_similarity = avg_similarity
                best_match = farmer_id
        
        if best_match:
            # Get farmer details from Firebase
            from app.services.firebase_service import FirebaseService
            firebase = FirebaseService()
            farmer = await firebase.get_farmer(best_match)
            farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown" if farmer else "Unknown"
            
            print(f"[Face Recognition] Best match: Farmer {best_match} with confidence {best_similarity:.3f}")
            return {
                "success": True,
                "farmer_id": best_match,
                "confidence": float(best_similarity),
                "farmer": {"id": best_match, "name": farmer_name}
            }
        else:
            print(f"[Face Recognition] No match found. Best similarity was {best_similarity:.3f}")
            return {
                "success": False,
                "message": "Face not recognized"
            }

    async def enroll_face(self, farmer_id: str, image_data: bytes, angle: str = "front") -> Dict:
        embedding = await self.extract_face_embedding(image_data)
        
        if embedding is None:
            return {
                "success": False,
                "message": f"No face detected in the {angle} image"
            }
        
        # Store embedding with angle identifier
        embedding_key = f"{farmer_id}_{angle}"
        self.face_embeddings[embedding_key] = embedding
        
        # Save to Firebase
        try:
            from app.services.firebase_service import FirebaseService
            firebase = FirebaseService()
            
            # Convert numpy array to list for JSON serialization
            embedding_data = {
                "farmer_id": farmer_id,
                "angle": angle,
                "embedding": embedding.tolist() if not self.mock_mode else embedding.tolist(),
                "created_at": datetime.now().isoformat()
            }
            
            # Save to Firebase
            doc_id = f"{farmer_id}_{angle}"
            await firebase.save_document("face_embeddings", doc_id, embedding_data)
            print(f"Saved face embedding for {farmer_id} - {angle} to Firebase")
        except Exception as e:
            print(f"Error saving embedding to Firebase: {e}")
        
        return {
            "success": True,
            "message": f"Face {angle} view enrolled successfully"
        }
    
    async def get_farmer_embeddings(self, farmer_id: str) -> Dict[str, np.ndarray]:
        """Get all embeddings for a farmer"""
        embeddings = {}
        
        # First check memory cache
        for angle in ["front", "left", "right"]:
            key = f"{farmer_id}_{angle}"
            if key in self.face_embeddings:
                embeddings[angle] = self.face_embeddings[key]
        
        # If not in memory, load from Firebase
        if not embeddings:
            try:
                from app.services.firebase_service import FirebaseService
                firebase = FirebaseService()
                
                for angle in ["front", "left", "right"]:
                    doc_id = f"{farmer_id}_{angle}"
                    doc = await firebase.get_document("face_embeddings", doc_id)
                    if doc and "embedding" in doc:
                        # Convert list back to numpy array
                        embedding_list = doc["embedding"]
                        embeddings[angle] = np.array(embedding_list)
                        # Also cache in memory
                        self.face_embeddings[f"{farmer_id}_{angle}"] = embeddings[angle]
                
                if embeddings:
                    print(f"Loaded {len(embeddings)} embeddings for farmer {farmer_id} from Firebase")
            except Exception as e:
                print(f"Error loading embeddings from Firebase: {e}")
        
        return embeddings
    
    async def verify_face(self, farmer_id: str, face_image: np.ndarray) -> Dict:
        """Verify if the face belongs to a specific farmer"""
        if self.mock_mode:
            # Mock mode - randomly return success with high confidence
            import random
            is_match = random.random() > 0.2  # 80% success rate
            return {
                "is_match": is_match,
                "confidence": random.uniform(0.85, 0.95) if is_match else random.uniform(0.3, 0.5)
            }
        
        try:
            # Convert numpy array to bytes for processing
            _, buffer = cv2.imencode('.jpg', face_image)
            image_data = buffer.tobytes()
            
            # Extract face embedding
            print(f"[verify_face] Image data size: {len(image_data)} bytes")
            embedding = await self.extract_face_embedding(image_data)
            
            if embedding is None:
                print(f"[verify_face] Failed to extract embedding - no face detected")
                return {
                    "is_match": False,
                    "confidence": 0.0,
                    "error": "No face detected in the image"
                }
            
            # Get farmer's stored embeddings
            farmer_embeddings = await self.get_farmer_embeddings(farmer_id)
            print(f"[verify_face] Farmer {farmer_id} has {len(farmer_embeddings)} embeddings")
            
            if not farmer_embeddings:
                return {
                    "is_match": False,
                    "confidence": 0.0,
                    "error": "No registered face data for this farmer"
                }
            
            # Compare with all stored embeddings for this farmer
            similarities = []
            for angle, stored_embedding in farmer_embeddings.items():
                similarity = np.dot(embedding, stored_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(stored_embedding))
                similarities.append(similarity)
            
            # Get the best match
            best_similarity = max(similarities) if similarities else 0.0
            print(f"[verify_face] Similarities for farmer {farmer_id}: {similarities}")
            print(f"[verify_face] Best similarity: {best_similarity}")
            
            # Threshold for face match (adjustable based on security requirements)
            threshold = 0.6
            is_match = best_similarity > threshold
            print(f"[verify_face] Threshold: {threshold}, Is match: {is_match}")
            
            return {
                "is_match": is_match,
                "confidence": float(best_similarity)
            }
        except Exception as e:
            return {
                "is_match": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def check_face_quality(self, image_data: bytes, expected_angle: str = None) -> Dict:
        """
        Check face quality for enrollment suitability
        """
        if self.mock_mode:
            # Mock mode - simulate angle-specific responses
            import random
            
            # Simulate angle detection
            mock_yaw = 0
            recommendations = []
            quality_score = 0.92
            
            if expected_angle == "left":
                # Left turn shows positive yaw with front camera
                mock_yaw = random.uniform(25, 30)
            elif expected_angle == "right":
                # Right turn shows negative yaw with front camera
                mock_yaw = random.uniform(-30, -25)
            else:  # front
                mock_yaw = random.uniform(-5, 5)
            
            return {
                "face_detected": True,
                "quality_score": quality_score,
                "quality_details": {
                    "overall_score": quality_score,
                    "pose": {
                        "pitch": random.uniform(-5, 5),
                        "yaw": mock_yaw,
                        "roll": random.uniform(-3, 3),
                        "is_frontal": abs(mock_yaw) < 20
                    },
                    "face_size": 0.35,
                    "brightness": 0.88,
                    "sharpness": 0.91
                },
                "recommendations": recommendations,
                "message": "Face quality is good for enrollment"
            }
        
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {
                    "face_detected": False,
                    "message": "Failed to decode image"
                }
            
            # Detect faces
            faces = self.app.get(img) if self.app else []
            
            if len(faces) == 0:
                return {
                    "face_detected": False,
                    "message": "No face detected in the image"
                }
            
            # Get the largest face
            face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
            
            # Calculate quality metrics
            bbox = face.bbox
            face_width = bbox[2] - bbox[0]
            face_height = bbox[3] - bbox[1]
            image_width = img.shape[1]
            image_height = img.shape[0]
            
            # Face size relative to image
            face_size = (face_width * face_height) / (image_width * image_height)
            
            # Pose estimation (if available)
            pose = getattr(face, 'pose', None)
            if pose is not None:
                pitch, yaw, roll = pose
                is_frontal = abs(pitch) < 20 and abs(yaw) < 20 and abs(roll) < 20
            else:
                pitch, yaw, roll = 0, 0, 0
                is_frontal = True
            
            # Check if the angle matches expectation
            angle_correct = True
            angle_message = ""
            
            # Log the detected pose
            print(f"[Face Quality] Detected pose - Yaw: {yaw:.1f}, Pitch: {pitch:.1f}, Roll: {roll:.1f}")
            print(f"[Face Quality] Expected angle: {expected_angle}")
            
            if expected_angle:
                if expected_angle == "front":
                    # For front view, yaw should be close to 0
                    if abs(yaw) > 15:
                        angle_correct = False
                        angle_message = "Please look straight at the camera"
                elif expected_angle == "left":
                    # For left view with front camera (selfie), yaw should be POSITIVE
                    # because camera is mirrored like a mirror
                    # Made more lenient: 15 to 40 degrees
                    if yaw < 15 or yaw > 40:
                        angle_correct = False
                        angle_message = f"Please turn your head to the left (current: {yaw:.1f}°, need: 15° to 40°)"
                elif expected_angle == "right":
                    # For right view with front camera (selfie), yaw should be NEGATIVE
                    # because camera is mirrored like a mirror
                    # Made more lenient: -15 to -40 degrees
                    if yaw > -15 or yaw < -40:
                        angle_correct = False
                        angle_message = f"Please turn your head to the right (current: {yaw:.1f}°, need: -15° to -40°)"
            
            print(f"[Face Quality] Angle correct: {angle_correct}")
            
            # Image quality checks
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray) / 255.0
            
            # Sharpness check using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = min(1.0, laplacian.var() / 1000.0)
            
            # Overall quality score
            quality_score = 0.0
            recommendations = []
            
            # Angle check (highest priority)
            if not angle_correct:
                quality_score = 0.0  # Force low score if angle is wrong
                recommendations.insert(0, angle_message)
            
            # Face size score (ideal: 15-50% of image)
            if face_size < 0.1:
                quality_score += 0.1
                recommendations.append("Move closer to the camera")
            elif face_size > 0.5:
                quality_score += 0.1
                recommendations.append("Move further from the camera")
            else:
                quality_score += 0.3
            
            # Pose score (only if angle is correct)
            if angle_correct:
                if expected_angle == "front" and is_frontal:
                    quality_score += 0.3
                elif expected_angle in ["left", "right"] and not is_frontal:
                    quality_score += 0.3  # Good - face is turned
                else:
                    quality_score += 0.1
            else:
                quality_score += 0.0  # No pose score if angle is wrong
            
            # Brightness score
            if brightness < 0.3:
                quality_score += 0.1
                recommendations.append("Move to a brighter location")
            elif brightness > 0.8:
                quality_score += 0.1
                recommendations.append("Reduce lighting or move away from direct light")
            else:
                quality_score += 0.2
            
            # Sharpness score
            if sharpness < 0.3:
                quality_score += 0.1
                recommendations.append("Hold the camera steady and ensure focus")
            else:
                quality_score += 0.2
            
            result = {
                "face_detected": True,
                "quality_score": round(quality_score, 2),
                "quality_details": {
                    "overall_score": round(quality_score, 2),
                    "pose": {
                        "pitch": round(float(pitch), 1),
                        "yaw": round(float(yaw), 1),
                        "roll": round(float(roll), 1),
                        "is_frontal": bool(is_frontal)  # Convert numpy.bool_ to Python bool
                    },
                    "face_size": round(float(face_size), 2),
                    "brightness": round(float(brightness), 2),
                    "sharpness": round(float(sharpness), 2)
                },
                "recommendations": recommendations,
                "message": "Good face quality" if quality_score > 0.7 else "Face quality could be improved"
            }
            
            print(f"[Face Quality] Final score: {quality_score:.2f}")
            print(f"[Face Quality] Recommendations: {recommendations}")
            
            return result
            
        except Exception as e:
            return {
                "face_detected": False,
                "message": f"Error processing image: {str(e)}"
            }