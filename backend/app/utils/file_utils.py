import os
import uuid
from datetime import datetime
from typing import Optional
import aiofiles
from app.core.config import settings

def generate_unique_filename(original_filename: str, prefix: Optional[str] = None) -> str:
    """Generate unique filename with timestamp and UUID"""
    ext = os.path.splitext(original_filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}{ext}"
    return f"{timestamp}_{unique_id}{ext}"

def get_upload_path(category: str, filename: str) -> str:
    """Get upload path for file"""
    date_path = datetime.now().strftime("%Y/%m/%d")
    return os.path.join(settings.UPLOAD_DIR, category, date_path, filename)

async def save_upload_file(file_data: bytes, category: str, filename: str) -> str:
    """Save uploaded file to disk"""
    file_path = get_upload_path(category, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_data)
    
    return file_path

async def delete_file(file_path: str) -> bool:
    """Delete file from disk"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def ensure_dir(directory: str) -> None:
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    return 0.0