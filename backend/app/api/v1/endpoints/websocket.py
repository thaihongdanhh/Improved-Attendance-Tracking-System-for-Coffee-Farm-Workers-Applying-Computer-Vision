from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio

router = APIRouter()

# Store active websocket connections by job_id
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/video-processing/{job_id}")
async def video_processing_websocket(websocket: WebSocket, job_id: str):
    print(f"WebSocket connection request for job {job_id}")
    await websocket.accept()
    active_connections[job_id] = websocket
    print(f"WebSocket connected for job {job_id}. Total connections: {len(active_connections)}")
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for job {job_id}")
        if job_id in active_connections:
            del active_connections[job_id]
    except Exception as e:
        print(f"WebSocket error for job {job_id}: {e}")
        if job_id in active_connections:
            del active_connections[job_id]

async def send_frame_update(job_id: str, data: dict):
    """Send frame update to connected client"""
    print(f"Attempting to send frame update for job {job_id}. Active connections: {list(active_connections.keys())}")
    if job_id in active_connections:
        try:
            websocket = active_connections[job_id]
            await websocket.send_json(data)
            print(f"Frame update sent successfully for job {job_id}")
        except Exception as e:
            print(f"Error sending websocket message for job {job_id}: {e}")
            if job_id in active_connections:
                del active_connections[job_id]
    else:
        print(f"No active WebSocket connection for job {job_id}")