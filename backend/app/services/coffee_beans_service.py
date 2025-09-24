import numpy as np
import cv2
from typing import Dict, List, Optional, Callable
from app.core.config import settings
import os
from datetime import datetime
import shutil
from fastapi import UploadFile
import base64
import asyncio
from app.api.v1.endpoints.websocket import send_frame_update

# Conditional import for YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: Ultralytics YOLO not installed. Coffee beans detection will use mock mode.")

# Conditional import for supervision
try:
    import supervision as sv
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False
    print("Warning: Supervision not installed. ByteTrack tracking will not be available.")

class CoffeeBeansService:
    def __init__(self):
        # Initialize YOLO model
        if YOLO_AVAILABLE and os.path.exists(settings.YOLO_BEANS_MODEL_PATH):
            self.model = YOLO(settings.YOLO_BEANS_MODEL_PATH)
            self.mock_mode = False
            print(f"Loaded coffee beans model from: {settings.YOLO_BEANS_MODEL_PATH}")
        elif YOLO_AVAILABLE:
            self.model = YOLO('yolov8n.pt')  # Use default model for testing
            self.mock_mode = False
            print("Using default YOLOv8n model")
        else:
            self.model = None
            self.mock_mode = True
            print("YOLO not available, using mock mode")
        
        # Updated defect classes based on AICoffeeNew
        self.defect_classes = {
            0: "BLACK",
            1: "BROKEN", 
            2: "BROWN",
            3: "BigBroken",
            4: "IMMATURE",
            5: "INSECT",
            6: "MOLD",
            7: "PartlyBlack",
            8: "LIGHTFM",  # Light foreign matter
            9: "HEAVYFM"   # Heavy foreign matter
        }
        
        # Define which classes are considered GOOD vs DEFECTS
        self.good_classes = {"BROWN"}  # BROWN beans are good quality
        self.defect_classes_list = {
            "BLACK", "BROKEN", "BigBroken", "IMMATURE", 
            "INSECT", "MOLD", "PartlyBlack", "LIGHTFM", "HEAVYFM"
        }
        
        # Color mapping for visualization
        self.defect_colors = {
            "BLACK": "#000000",
            "BROKEN": "#8B4513",
            "BROWN": "#A52A2A",
            "BigBroken": "#D2691E",
            "IMMATURE": "#90EE90",
            "INSECT": "#FF6347",
            "MOLD": "#808080",
            "PartlyBlack": "#696969",
            "LIGHTFM": "#FFD700",
            "HEAVYFM": "#FF4500"
        }

    async def analyze_beans(self, image_data: bytes) -> Dict:
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if self.mock_mode:
                # Return mock results
                return self._generate_mock_results()
            
            # Run detection with confidence threshold
            results = self.model(img, conf=0.5)
            
            # Print average confidence score from model
            if len(results) > 0 and results[0].boxes is not None:
                confidences = results[0].boxes.conf.cpu().numpy()
                avg_conf = confidences.mean()
                print(f"[Coffee Beans Model] Detected {len(confidences)} objects - Avg Conf: {avg_conf:.3f}")
            else:
                print("[Coffee Beans Model] No detections found")
            
            # Process results
            detections = results[0].boxes if len(results) > 0 else None
            
            if detections is None or len(detections) == 0:
                return {
                    "success": False,
                    "message": "No coffee beans detected in the image"
                }
            
            # Count defects and draw boxes
            defect_counts = {}
            total_beans = len(detections)
            annotated_img = img.copy()
            
            for box in detections:
                class_id = int(box.cls[0])
                class_name = self.defect_classes.get(class_id, "UNKNOWN")
                defect_counts[class_name] = defect_counts.get(class_name, 0) + 1
                
                # Draw bounding box
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                color = self._hex_to_bgr(self.defect_colors.get(class_name, "#FFFFFF"))
                cv2.rectangle(annotated_img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(annotated_img, class_name, (int(x1), int(y1-10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Calculate quality score based on actual defects only
            defect_count = sum(count for defect, count in defect_counts.items() 
                             if defect in self.defect_classes_list)
            good_count = sum(count for defect, count in defect_counts.items() 
                           if defect in self.good_classes)
            
            # Quality score based on ratio of good beans vs defects
            if total_beans > 0:
                defect_percentage = (defect_count / total_beans) * 100
                quality_score = max(0, 100 - defect_percentage)
            else:
                quality_score = 0
            
            # Prepare defects list - only include actual defects, not good beans
            defects = []
            for defect_type, count in defect_counts.items():
                if defect_type in self.defect_classes_list:  # Only true defects
                    defects.append({
                        "type": defect_type,
                        "count": count,
                        "percentage": (count / total_beans) * 100
                    })
            
            # Generate recommendations based on AICoffeeNew logic
            recommendations = []
            if quality_score < 70:
                recommendations.append("Quality below acceptable threshold. Consider re-sorting.")
            if defect_counts.get("INSECT", 0) > 0:
                recommendations.append("Insect damage detected. Check storage conditions.")
            if defect_counts.get("MOLD", 0) > 0:
                recommendations.append("Mold detected. Review drying and storage process.")
            if defect_counts.get("BLACK", 0) + defect_counts.get("PartlyBlack", 0) > total_beans * 0.1:
                recommendations.append("High percentage of black beans. Review fermentation process.")
            if defect_counts.get("LIGHTFM", 0) + defect_counts.get("HEAVYFM", 0) > 0:
                recommendations.append("Foreign matter detected. Improve cleaning process.")
            
            # Estimate weight (simplified)
            weight_estimate = total_beans * 0.2  # Average bean weight in grams
            
            # Save processed image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_filename = f"beans_analysis_{timestamp}.jpg"
            # Create absolute path for uploads
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            processed_path = os.path.join(base_dir, settings.UPLOAD_DIR, "beans", processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            cv2.imwrite(processed_path, annotated_img)
            
            # Upload to Firebase Storage
            firebase_url = f"/uploads/beans/{processed_filename}"  # Default to local URL
            try:
                from app.services.firebase_service import FirebaseService
                firebase = FirebaseService()
                
                # Convert annotated image to bytes
                _, buffer = cv2.imencode('.jpg', annotated_img)
                img_bytes = buffer.tobytes()
                
                # Upload to Firebase Storage
                firebase_path = f"coffee_beans/{timestamp}/{processed_filename}"
                firebase_url = await firebase.upload_file(firebase_path, img_bytes, "image/jpeg")
                print(f"Uploaded coffee beans analysis to Firebase Storage: {firebase_url}")
            except Exception as e:
                print(f"Error uploading to Firebase Storage: {e}")
            
            return {
                "success": True,
                "analysis": {
                    "total_beans": total_beans,
                    "defects": defects,
                    "defect_counts": defect_counts,
                    "good_beans": good_count,
                    "defect_beans": defect_count,
                    "quality_score": round(quality_score, 2),
                    "weight_estimate": round(weight_estimate, 2),
                    "recommendations": recommendations
                },
                "image_url": firebase_url,
                "image_url_local": f"/uploads/beans/{processed_filename}",
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
        
        # Ensure is_video field is set for image analyses
        if "is_video" not in analysis_data:
            analysis_data["is_video"] = False
        
        # Save to Firestore
        await firebase.save_document("coffee_beans_analyses", analysis_id, analysis_data)
        
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
        
        analyses = await firebase.query_documents("coffee_beans_analyses", filters)
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return analyses

    async def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get a specific analysis by ID"""
        from app.services.firebase_service import FirebaseService
        firebase = FirebaseService()
        
        return await firebase.get_document("coffee_beans_analyses", analysis_id)
    
    async def get_farm_statistics(self, farm_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Get aggregated statistics for a farm"""
        from app.services.firebase_service import FirebaseService
        firebase = FirebaseService()
        
        filters = [("farm_id", "==", farm_id)]
        if start_date:
            filters.append(("created_at", ">=", start_date.isoformat()))
        if end_date:
            filters.append(("created_at", "<=", end_date.isoformat()))
        
        analyses = await firebase.query_documents("coffee_beans_analyses", filters)
        
        if not analyses:
            return {
                "total_analyses": 0,
                "average_quality": 0,
                "defect_distribution": {},
                "quality_trend": []
            }
        
        # Calculate statistics
        total_quality = 0
        defect_counts = {}
        quality_by_date = {}
        
        for analysis in analyses:
            if "analysis" in analysis:
                total_quality += analysis["analysis"].get("quality_score", 0)
                
                # Aggregate defects
                for defect, count in analysis["analysis"].get("defect_counts", {}).items():
                    defect_counts[defect] = defect_counts.get(defect, 0) + count
                
                # Track quality by date
                date_str = analysis.get("created_at", "")[:10]  # YYYY-MM-DD
                if date_str not in quality_by_date:
                    quality_by_date[date_str] = []
                quality_by_date[date_str].append(analysis["analysis"].get("quality_score", 0))
        
        # Calculate averages
        avg_quality = total_quality / len(analyses) if analyses else 0
        
        # Calculate daily averages for trend
        quality_trend = []
        for date, scores in sorted(quality_by_date.items()):
            quality_trend.append({
                "date": date,
                "average_quality": sum(scores) / len(scores) if scores else 0,
                "sample_count": len(scores)
            })
        
        return {
            "total_analyses": len(analyses),
            "average_quality": round(avg_quality, 2),
            "defect_distribution": defect_counts,
            "quality_trend": quality_trend
        }
    
    def _hex_to_bgr(self, hex_color: str) -> tuple:
        """Convert hex color to BGR for OpenCV"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (rgb[2], rgb[1], rgb[0])  # Convert RGB to BGR
    
    def _generate_mock_results(self) -> Dict:
        """Generate mock results for testing"""
        import random
        
        total_beans = random.randint(200, 400)
        defects = []
        defect_counts = {}
        
        # Generate random defects from actual classes
        defect_types = ["BLACK", "BROKEN", "BROWN", "IMMATURE", "INSECT"]
        for defect_type in defect_types:
            if random.random() > 0.5:  # 50% chance of having this defect
                count = random.randint(5, 30)
                defects.append({
                    "type": defect_type,
                    "count": count,
                    "percentage": round((count / total_beans) * 100, 2)
                })
                defect_counts[defect_type] = count
        
        # Calculate quality score
        total_defects = sum(defect_counts.values())
        quality_score = max(0, 100 - (total_defects / total_beans * 100))
        weight_estimate = total_beans * 0.2
        
        recommendations = []
        if quality_score < 70:
            recommendations.append("Quality below acceptable threshold. Consider re-sorting.")
        if "INSECT" in defect_counts:
            recommendations.append("Insect damage detected. Check storage conditions.")
        if "BLACK" in defect_counts and defect_counts["BLACK"] > total_beans * 0.1:
            recommendations.append("High percentage of black beans. Review fermentation process.")
        
        return {
            "success": True,
            "analysis": {
                "total_beans": total_beans,
                "defects": defects,
                "defect_counts": defect_counts,
                "quality_score": round(quality_score, 2),
                "weight_estimate": round(weight_estimate, 2),
                "recommendations": recommendations
            },
            "image_url": "/uploads/beans/mock_analysis.jpg",
            "timestamp": datetime.now().isoformat()
        }
    
    async def save_video_file(self, file: UploadFile, job_id: str) -> str:
        """Save uploaded video file"""
        # Create directory for video uploads
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        video_dir = os.path.join(base_dir, settings.UPLOAD_DIR, "videos", job_id)
        os.makedirs(video_dir, exist_ok=True)
        
        # Save video file
        video_path = os.path.join(video_dir, file.filename)
        with open(video_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return video_path
    
    async def process_video(self, video_path: str, job_id: str, progress_callback: Optional[Callable] = None) -> Dict:
        """Process video file and extract frame-by-frame analysis with ByteTrack tracking"""
        try:
            # Wait a bit for WebSocket to connect
            print(f"Waiting 2 seconds for WebSocket connection for job {job_id}...")
            await asyncio.sleep(2)
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception("Failed to open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Create output video writer
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            output_dir = os.path.join(base_dir, settings.UPLOAD_DIR, "videos", job_id)
            output_path = os.path.join(output_dir, "processed_output.mp4")
            
            # First try mp4v codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            temp_output_path = output_path.replace('.mp4', '_temp.mp4')
            out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))
            
            # Check if video writer opened successfully
            if not out.isOpened():
                print(f"Failed to open video writer with mp4v codec, trying MJPG")
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                temp_output_path = output_path.replace('.mp4', '_temp.avi')
                out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))
                
            if not out.isOpened():
                raise Exception("Failed to open video writer with any codec")
            
            # Initialize ByteTrack tracker if available
            tracker = None
            unique_bean_ids = set()
            if SUPERVISION_AVAILABLE and not self.mock_mode:
                tracker = sv.ByteTrack()
            
            # Process frames
            frame_analyses = []
            detection_timeline = []
            frame_count = 0
            # Don't skip frames - process all frames for real-time display
            process_every_n_frames = 1  # Process every frame
            analyze_every_n_frames = 10  # Analyze for statistics every 10 frames
            
            aggregate_defects = {}
            total_beans_all_frames = 0
            
            print(f"Starting video processing: {total_frames} frames at {fps} FPS")
            print(f"Output path: {output_path}")
            print(f"Processing all frames for real-time streaming")
            print(f"Analyzing statistics every {analyze_every_n_frames} frames")
            
            # Test write a frame
            test_frame = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.putText(test_frame, "Processing...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(test_frame)
            
            frames_written = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Update progress
                if progress_callback:
                    progress = {
                        "progress": int((frame_count / total_frames) * 100),
                        "processed_frames": frame_count,
                        "total_frames": total_frames
                    }
                    progress_callback(progress)
                
                # Process detection on every frame, but analyze for statistics less frequently
                process_this_frame = (frame_count % process_every_n_frames == 0)  # Always true (every frame)
                analyze_this_frame = (frame_count % analyze_every_n_frames == 0)  # Every 10 frames
                
                # Always run detection on every frame for real-time display
                if not self.mock_mode and process_this_frame:
                    # Run detection on current frame
                    results = self.model(frame, conf=0.5)
                    
                    # Print average confidence for every 100th frame
                    if frame_count % 100 == 0:
                        print(f"Processing frame {frame_count}/{total_frames} - FPS: {fps}")
                        if len(results) > 0 and results[0].boxes is not None:
                            confidences = results[0].boxes.conf.cpu().numpy()
                            avg_conf = confidences.mean()
                            print(f"[Coffee Beans Video] Frame {frame_count} - Detected {len(confidences)} objects - Avg Conf: {avg_conf:.3f}")
                    
                    if len(results) > 0 and results[0].boxes is not None:
                        boxes = results[0].boxes
                        
                        # Apply ByteTrack if available
                        if tracker and SUPERVISION_AVAILABLE:
                            # Convert to supervision format
                            detections = sv.Detections.from_ultralytics(results[0])
                            
                            # Update tracker
                            detections = tracker.update_with_detections(detections)
                            
                            # Track unique IDs
                            if hasattr(detections, 'tracker_id') and detections.tracker_id is not None:
                                unique_bean_ids.update(detections.tracker_id)
                            
                            # Draw tracked detections
                            box_annotator = sv.BoxAnnotator()
                            label_annotator = sv.LabelAnnotator()
                            
                            # Create labels with tracking IDs
                            labels = []
                            for i, (xyxy, class_id, confidence, tracker_id) in enumerate(zip(
                                detections.xyxy,
                                detections.class_id,
                                detections.confidence,
                                detections.tracker_id if hasattr(detections, 'tracker_id') else [None] * len(detections)
                            )):
                                class_name = self.defect_classes.get(int(class_id), "UNKNOWN")
                                if tracker_id is not None:
                                    labels.append(f"{class_name} #{int(tracker_id)}")
                                else:
                                    labels.append(class_name)
                            
                            # Annotate frame
                            frame = box_annotator.annotate(scene=frame, detections=detections)
                            frame = label_annotator.annotate(scene=frame, detections=detections, labels=labels)
                        else:
                            # Fallback to simple drawing without tracking
                            for box in results[0].boxes:
                                class_id = int(box.cls[0])
                                class_name = self.defect_classes.get(class_id, "UNKNOWN")
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                color = self._hex_to_bgr(self.defect_colors.get(class_name, "#FFFFFF"))
                                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                                cv2.putText(frame, class_name, (int(x1), int(y1-10)), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        
                        # Only do full analysis periodically
                        if analyze_this_frame:
                            # Count beans and defects from current detections
                            defect_counts = {}
                            for box in results[0].boxes:
                                class_id = int(box.cls[0])
                                class_name = self.defect_classes.get(class_id, "UNKNOWN")
                                defect_counts[class_name] = defect_counts.get(class_name, 0) + 1
                            
                            total_beans = len(results[0].boxes)
                            # Calculate actual defects vs good beans
                            actual_defects = sum(count for defect, count in defect_counts.items() 
                                               if defect in self.defect_classes_list)
                            good_beans = sum(count for defect, count in defect_counts.items() 
                                           if defect in self.good_classes)
                            
                            quality_score = max(0, 100 - (actual_defects / max(total_beans, 1) * 100))
                            
                            # Store frame analysis
                            frame_analysis = {
                                "frame_number": frame_count,
                                "timestamp": frame_count / fps,
                                "total_beans": total_beans,
                                "defect_counts": defect_counts,
                                "good_beans": good_beans,
                                "defect_beans": actual_defects,
                                "quality_score": quality_score
                            }
                            frame_analyses.append(frame_analysis)
                            
                            # Aggregate defects (only true defects, not good beans)
                            for defect, count in defect_counts.items():
                                if defect in self.defect_classes_list:  # Only aggregate actual defects
                                    aggregate_defects[defect] = aggregate_defects.get(defect, 0) + count
                            total_beans_all_frames += total_beans
                
                # Add frame info overlay
                cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if len(frame_analyses) > 0:
                    latest_analysis = frame_analyses[-1]
                    cv2.putText(frame, f"Beans in Frame: {latest_analysis['total_beans']}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Quality: {latest_analysis['quality_score']:.1f}%", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Add unique bean count if tracking is enabled
                    if tracker and len(unique_bean_ids) > 0:
                        cv2.putText(frame, f"Unique Beans: {len(unique_bean_ids)}", (10, 120),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Write frame to output video
                out.write(frame)
                frames_written += 1
                
                # Send frame via WebSocket for real-time display
                # Send every 2nd frame for smoother real-time display
                if frame_count % 2 == 0:
                    try:
                        # Resize frame for streaming with better quality
                        # Use frame which has annotations
                        stream_frame = cv2.resize(frame, (1024, 768))
                        _, buffer = cv2.imencode('.jpg', stream_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        frame_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        # Websocket send function already imported at top
                        
                        # Get latest analysis data
                        latest_beans = 0
                        latest_quality = 0
                        if len(frame_analyses) > 0:
                            latest_analysis = frame_analyses[-1]
                            latest_beans = latest_analysis.get('total_beans', 0)
                            latest_quality = latest_analysis.get('quality_score', 0)
                        
                        # Send frame update
                        print(f"Sending WebSocket frame for job {job_id}, frame {frame_count}")
                        try:
                            frame_data = {
                                "type": "frame",
                                "frame": frame_base64,
                                "frame_number": frame_count,
                                "total_frames": total_frames,
                                "progress": int((frame_count / total_frames) * 100),
                                "beans_detected": latest_beans,
                                "quality_score": latest_quality,
                                "unique_beans": len(unique_bean_ids) if tracker else 0
                            }
                            
                            # Use await to send frame update
                            await send_frame_update(job_id, frame_data)
                            print(f"WebSocket frame sent for job {job_id}")
                        except Exception as e:
                            print(f"Error sending WebSocket update: {e}")
                    except Exception as e:
                        print(f"Error sending WebSocket frame: {e}")
            
            # Release resources
            cap.release()
            out.release()
            # Don't call destroyAllWindows on server (no GUI)
            
            print(f"Video processing complete. Frames written: {frames_written}")
            
            # Check if temp output file was created and rename it
            if os.path.exists(temp_output_path):
                print(f"Temp video created at {temp_output_path}, size: {os.path.getsize(temp_output_path)} bytes")
                
                # If it's an AVI file, keep it as is for now
                if temp_output_path.endswith('.avi'):
                    output_path = output_path.replace('.mp4', '.avi')
                    
                # Rename temp file to final output
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_output_path, output_path)
                print(f"Renamed to final output: {output_path}")
            else:
                print(f"Warning: Temp video file not created at {temp_output_path}")
                # Fallback to original video
                output_path = video_path
                
            # Final check
            if not os.path.exists(output_path):
                print(f"Warning: Output video file not found at {output_path}")
                output_path = video_path
            else:
                print(f"Output video ready at {output_path}")
                print(f"Output video size: {os.path.getsize(output_path)} bytes")
            
            # Calculate summary statistics
            avg_quality = sum(fa["quality_score"] for fa in frame_analyses) / len(frame_analyses) if frame_analyses else 0
            
            # Generate summary
            summary = {
                "total_frames_analyzed": len(frame_analyses),
                "average_quality_score": round(avg_quality, 2),
                "total_beans_detected": total_beans_all_frames,
                "unique_beans_tracked": len(unique_bean_ids) if tracker else 0,
                "aggregate_defects": aggregate_defects,
                "defect_timeline": self._create_defect_timeline(frame_analyses, fps),
                "recommendations": self._generate_video_recommendations(aggregate_defects, total_beans_all_frames, avg_quality)
            }
            
            return {
                "success": True,
                "summary": summary,
                "frame_analyses": frame_analyses,
                "detection_timeline": detection_timeline,
                "total_frames": total_frames,
                "processed_video_url": f"/uploads/videos/{job_id}/{os.path.basename(output_path)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def save_video_analysis(self, analysis_data: Dict) -> Dict:
        """Save video analysis to Firebase/Firestore"""
        from app.services.firebase_service import FirebaseService
        firebase = FirebaseService()
        
        # Generate unique ID
        analysis_id = f"video_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{analysis_data.get('user_id', 'unknown')}"
        analysis_data["id"] = analysis_id
        analysis_data["created_at"] = datetime.now().isoformat()
        
        # Save to Firestore
        await firebase.save_document("coffee_beans_analyses", analysis_id, analysis_data)
        
        return analysis_data
    
    def _create_defect_timeline(self, frame_analyses: List[Dict], fps: int) -> List[Dict]:
        """Create timeline of defect occurrences"""
        timeline = []
        
        # Group by time intervals (e.g., every 5 seconds)
        interval = 5  # seconds
        current_interval = 0
        interval_data = {
            "start_time": 0,
            "end_time": interval,
            "defects": {},
            "total_beans": 0,
            "avg_quality": 0,
            "frame_count": 0
        }
        
        for analysis in frame_analyses:
            time = analysis["timestamp"]
            
            # Check if we've moved to a new interval
            if time >= interval_data["end_time"]:
                # Save current interval if it has data
                if interval_data["frame_count"] > 0:
                    interval_data["avg_quality"] /= interval_data["frame_count"]
                    timeline.append(interval_data.copy())
                
                # Start new interval
                current_interval += 1
                interval_data = {
                    "start_time": current_interval * interval,
                    "end_time": (current_interval + 1) * interval,
                    "defects": {},
                    "total_beans": 0,
                    "avg_quality": 0,
                    "frame_count": 0
                }
            
            # Add to current interval
            for defect, count in analysis["defect_counts"].items():
                interval_data["defects"][defect] = interval_data["defects"].get(defect, 0) + count
            interval_data["total_beans"] += analysis["total_beans"]
            interval_data["avg_quality"] += analysis["quality_score"]
            interval_data["frame_count"] += 1
        
        # Add last interval if it has data
        if interval_data["frame_count"] > 0:
            interval_data["avg_quality"] /= interval_data["frame_count"]
            timeline.append(interval_data)
        
        return timeline
    
    def _generate_video_recommendations(self, aggregate_defects: Dict, total_beans: int, avg_quality: float) -> List[str]:
        """Generate recommendations based on video analysis"""
        recommendations = []
        
        if avg_quality < 70:
            recommendations.append("Overall quality below acceptable threshold. Consider re-sorting the batch.")
        
        # Check for high defect rates
        for defect, count in aggregate_defects.items():
            percentage = (count / total_beans * 100) if total_beans > 0 else 0
            
            if defect == "INSECT" and percentage > 5:
                recommendations.append(f"High insect damage rate ({percentage:.1f}%). Check storage conditions immediately.")
            elif defect == "MOLD" and percentage > 3:
                recommendations.append(f"Mold detected in {percentage:.1f}% of beans. Review drying and storage process.")
            elif defect in ["BLACK", "PartlyBlack"] and percentage > 10:
                recommendations.append(f"High percentage of black beans ({percentage:.1f}%). Review fermentation process.")
            elif defect in ["LIGHTFM", "HEAVYFM"] and percentage > 2:
                recommendations.append(f"Foreign matter detected ({percentage:.1f}%). Improve cleaning process.")
            elif defect == "BROKEN" and percentage > 15:
                recommendations.append(f"High breakage rate ({percentage:.1f}%). Check processing equipment.")
        
        if len(recommendations) == 0 and avg_quality >= 85:
            recommendations.append("Excellent batch quality! Maintain current processing standards.")
        
        return recommendations