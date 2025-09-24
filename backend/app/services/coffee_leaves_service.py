import numpy as np
import cv2
from typing import Dict, List, Optional
from app.core.config import settings
import os
from datetime import datetime

# Conditional import for YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: Ultralytics YOLO not installed. Coffee leaves detection will use mock mode.")

class CoffeeLeavesService:
    def __init__(self):
        # Initialize YOLO model
        if YOLO_AVAILABLE and os.path.exists(settings.YOLO_LEAVES_MODEL_PATH):
            self.model = YOLO(settings.YOLO_LEAVES_MODEL_PATH)
        elif YOLO_AVAILABLE:
            self.model = YOLO('yolov8n.pt')  # Use default model for testing
        else:
            self.model = None
        
        self.mock_mode = not YOLO_AVAILABLE
        
        self.disease_classes = {
            0: "cercospora",
            1: "miner",
            2: "phoma",
            3: "rust",
            4: "healthy"
        }
        
        # Color mapping for visualization (BGR format for OpenCV)
        self.disease_colors = {
            "cercospora": (139, 69, 19),    # Brown
            "miner": (128, 128, 128),        # Gray
            "phoma": (0, 0, 0),              # Black
            "rust": (0, 140, 255),           # Orange
            "healthy": (0, 255, 0),          # Green
            "unknown": (255, 0, 0)           # Blue for unknown
        }
        
        self.severity_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9
        }

    async def analyze_leaves(self, image_data: bytes) -> Dict:
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if self.mock_mode:
                # Return mock results
                return self._generate_mock_results()
            
            # Run detection with confidence threshold
            results = self.model(img, conf=0.5)
            
            # Print confidence scores from model
            if len(results) > 0 and results[0].boxes is not None:
                confidences = results[0].boxes.conf.cpu().numpy()
                class_ids = results[0].boxes.cls.cpu().numpy()
                print(f"[Coffee Leaves Model] Detected {len(confidences)} objects:")
                for i, (conf, cls_id) in enumerate(zip(confidences, class_ids)):
                    class_name = self.disease_classes.get(int(cls_id), "UNKNOWN")
                    print(f"  Detection {i+1}: {class_name} - Confidence: {conf:.3f}")
            else:
                print("[Coffee Leaves Model] No detections found")
            
            # Process results
            detections = results[0].boxes if len(results) > 0 and results[0].boxes is not None else []
            
            # If no detections, it means leaves are healthy
            if len(detections) == 0:
                # Return healthy leaf result
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                processed_filename = f"leaves_analysis_{timestamp}.jpg"
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                processed_path = os.path.join(base_dir, settings.UPLOAD_DIR, "leaves", processed_filename)
                os.makedirs(os.path.dirname(processed_path), exist_ok=True)
                cv2.imwrite(processed_path, img)
                
                return {
                    "success": True,
                    "analysis": {
                        "diseases_detected": [],
                        "health_score": 100.0,
                        "total_leaves": 1,  # Assume at least 1 leaf in image
                        "infected_leaves": 0,
                        "recommendations": ["Leaves are healthy. Continue regular maintenance and monitoring."]
                    },
                    "image_url": f"/uploads/leaves/{processed_filename}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Analyze diseases
            diseases_detected = []
            health_score = 100.0
            annotated_img = img.copy()
            
            for box in detections:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                disease_name = self.disease_classes.get(class_id, "unknown")
                
                # Draw bounding box with disease-specific color
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                color = self.disease_colors.get(disease_name, self.disease_colors["unknown"])
                
                # Draw thicker box for better visibility
                cv2.rectangle(annotated_img, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
                
                # Add label with background for better readability
                label = f"{disease_name} {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                
                # Draw label background
                cv2.rectangle(annotated_img, 
                            (int(x1), int(y1-25)), 
                            (int(x1) + label_size[0], int(y1)), 
                            color, -1)
                
                # Draw label text
                cv2.putText(annotated_img, label, 
                           (int(x1), int(y1-8)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if disease_name != "healthy" and disease_name != "unknown":
                    # Determine severity
                    severity = "low"
                    if confidence > self.severity_thresholds["high"]:
                        severity = "high"
                    elif confidence > self.severity_thresholds["medium"]:
                        severity = "medium"
                    
                    diseases_detected.append({
                        "disease": disease_name,
                        "confidence": round(confidence, 3),
                        "severity": severity,
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    })
                    
                    # Reduce health score based on disease severity
                    if severity == "high":
                        health_score -= 30
                    elif severity == "medium":
                        health_score -= 20
                    else:
                        health_score -= 10
            
            health_score = max(0, health_score)
            
            # Generate recommendations
            recommendations = []
            if any(d["disease"] == "rust" for d in diseases_detected):
                recommendations.append("Rust detected. Apply fungicide treatment immediately.")
            if any(d["disease"] == "cercospora" for d in diseases_detected):
                recommendations.append("Cercospora leaf spot found. Improve air circulation.")
            if any(d["disease"] == "miner" for d in diseases_detected):
                recommendations.append("Leaf miner damage detected. Consider biological control.")
            if any(d["disease"] == "phoma" for d in diseases_detected):
                recommendations.append("Phoma detected. Remove affected leaves and apply copper-based fungicide.")
            
            if health_score < 50:
                recommendations.append("Critical health condition. Immediate intervention required.")
            elif health_score < 70:
                recommendations.append("Multiple diseases detected. Start treatment plan.")
            
            # Save processed image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_filename = f"leaves_analysis_{timestamp}.jpg"
            # Create absolute path for uploads
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            processed_path = os.path.join(base_dir, settings.UPLOAD_DIR, "leaves", processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            cv2.imwrite(processed_path, annotated_img)
            
            # Upload to Firebase Storage
            firebase_url = f"/uploads/leaves/{processed_filename}"  # Default to local URL
            try:
                from app.services.firebase_service import FirebaseService
                firebase = FirebaseService()
                
                # Convert annotated image to bytes
                _, buffer = cv2.imencode('.jpg', annotated_img)
                img_bytes = buffer.tobytes()
                
                # Upload to Firebase Storage
                firebase_path = f"coffee_leaves/{timestamp}/{processed_filename}"
                firebase_url = await firebase.upload_file(firebase_path, img_bytes, "image/jpeg")
                print(f"Uploaded coffee leaves analysis to Firebase Storage: {firebase_url}")
            except Exception as e:
                print(f"Error uploading to Firebase Storage: {e}")
            
            return {
                "success": True,
                "analysis": {
                    "diseases_detected": diseases_detected,
                    "health_score": round(health_score, 2),
                    "total_leaves": len(detections),
                    "infected_leaves": len(diseases_detected),
                    "recommendations": recommendations
                },
                "image_url": firebase_url,
                "image_url_local": f"/uploads/leaves/{processed_filename}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing image: {str(e)}"
            }

    async def save_analysis(self, analysis_data: Dict) -> Dict:
        """Save analysis to Firebase/Firestore"""
        from app.services.firebase_service import FirebaseService
        firebase = FirebaseService()
        
        # Generate unique ID
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{analysis_data.get('user_id', 'unknown')}"
        analysis_data["id"] = analysis_id
        analysis_data["created_at"] = datetime.now().isoformat()
        
        # Add farm and field information if provided
        if "farm_id" not in analysis_data:
            analysis_data["farm_id"] = analysis_data.get("farm_id", "default_farm")
        if "field_id" not in analysis_data:
            analysis_data["field_id"] = analysis_data.get("field_id", "default_field")
        
        # Save to Firestore
        await firebase.save_document("coffee_leaves_analyses", analysis_id, analysis_data)
        
        return analysis_data

    async def get_user_history(self, user_id: str, farm_id: str = None, field_id: str = None) -> List[Dict]:
        """Get analysis history for a user, optionally filtered by farm/field"""
        from app.services.firebase_service import FirebaseService
        firebase = FirebaseService()
        
        # Query analyses
        filters = [("user_id", "==", user_id)]
        if farm_id:
            filters.append(("farm_id", "==", farm_id))
        if field_id:
            filters.append(("field_id", "==", field_id))
        
        analyses = await firebase.query_documents("coffee_leaves_analyses", filters)
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return analyses

    async def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get a specific analysis by ID"""
        from app.services.firebase_service import FirebaseService
        firebase = FirebaseService()
        
        return await firebase.get_document("coffee_leaves_analyses", analysis_id)
    
    def _generate_mock_results(self) -> Dict:
        """Generate mock results for testing"""
        import random
        
        diseases = []
        total_leaves = random.randint(5, 15)
        health_score = random.uniform(60, 95)
        
        # Generate random diseases
        infected_leaves = 0
        if health_score < 80:
            disease_types = ["rust", "cercospora", "miner", "phoma"]
            num_diseases = random.randint(1, 3)
            
            for disease in random.sample(disease_types, num_diseases):
                confidence = random.uniform(0.6, 0.95)
                severity = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
                
                diseases.append({
                    "disease": disease,
                    "confidence": round(confidence, 3),
                    "severity": severity,
                    "bbox": [
                        random.randint(50, 200),
                        random.randint(50, 200),
                        random.randint(250, 400),
                        random.randint(250, 400)
                    ]
                })
                infected_leaves += 1
        
        recommendations = []
        if health_score < 50:
            recommendations.extend([
                "Critical health condition. Immediate intervention required.",
                "Apply systemic fungicide",
                "Remove severely infected leaves"
            ])
        elif health_score < 70:
            recommendations.extend([
                "Multiple diseases detected. Start treatment plan.",
                "Improve air circulation",
                "Monitor daily for progression"
            ])
        elif health_score < 85:
            recommendations.append("Monitor plants closely for disease progression")
        else:
            recommendations.append("Leaves are healthy. Continue regular maintenance.")
        
        # Save mock processed image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_filename = f"leaves_analysis_{timestamp}_mock.jpg"
        
        return {
            "success": True,
            "analysis": {
                "diseases_detected": diseases,
                "health_score": round(health_score, 2),
                "total_leaves": total_leaves,
                "infected_leaves": infected_leaves,
                "recommendations": recommendations
            },
            "image_url": f"/uploads/leaves/{processed_filename}",
            "timestamp": datetime.now().isoformat()
        }