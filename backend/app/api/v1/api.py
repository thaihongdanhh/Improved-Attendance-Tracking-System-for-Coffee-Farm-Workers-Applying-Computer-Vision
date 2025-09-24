from fastapi import APIRouter
from app.api.v1.endpoints import auth, farmers, attendance, coffee_beans, coffee_leaves, face, farms, test, websocket, statistics, payroll, tasks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
api_router.include_router(farms.router, prefix="/farms", tags=["farms"])
api_router.include_router(face.router, prefix="/face", tags=["face"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(coffee_beans.router, prefix="/coffee-beans", tags=["coffee-beans"])
api_router.include_router(coffee_leaves.router, prefix="/coffee-leaves", tags=["coffee-leaves"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["payroll"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(websocket.router, tags=["websocket"])