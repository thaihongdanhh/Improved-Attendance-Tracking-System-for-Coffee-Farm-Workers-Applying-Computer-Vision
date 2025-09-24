import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Optional

def resize_image(image: np.ndarray, max_size: int = 1024) -> np.ndarray:
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if width > height:
        if width > max_size:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            return image
    else:
        if height > max_size:
            new_height = max_size
            new_width = int(width * (max_size / height))
        else:
            return image
    
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

def image_to_base64(image: np.ndarray) -> str:
    """Convert numpy array to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_base64}"

def base64_to_image(base64_str: str) -> np.ndarray:
    """Convert base64 string to numpy array"""
    if base64_str.startswith('data:'):
        base64_str = base64_str.split(',')[1]
    
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def crop_face(image: np.ndarray, bbox: Tuple[int, int, int, int], margin: float = 0.2) -> np.ndarray:
    """Crop face from image with margin"""
    x, y, w, h = bbox
    height, width = image.shape[:2]
    
    # Add margin
    margin_w = int(w * margin)
    margin_h = int(h * margin)
    
    x1 = max(0, x - margin_w)
    y1 = max(0, y - margin_h)
    x2 = min(width, x + w + margin_w)
    y2 = min(height, y + h + margin_h)
    
    return image[y1:y2, x1:x2]

def enhance_image(image: np.ndarray) -> np.ndarray:
    """Enhance image quality"""
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge channels
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced

def validate_image(image_data: bytes, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
    """Validate image data"""
    # Check size
    size_mb = len(image_data) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"Image size {size_mb:.1f}MB exceeds maximum {max_size_mb}MB"
    
    # Try to decode image
    try:
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False, "Invalid image format"
        
        # Check dimensions
        height, width = img.shape[:2]
        if width < 100 or height < 100:
            return False, "Image too small (minimum 100x100)"
        
        return True, None
    except Exception as e:
        return False, f"Error processing image: {str(e)}"