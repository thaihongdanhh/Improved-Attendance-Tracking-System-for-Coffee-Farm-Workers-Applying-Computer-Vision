from fastapi import APIRouter, Depends, HTTPException
from app.services.firebase_service import FirebaseService
from datetime import datetime, timedelta
import random
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class TaskCreate(BaseModel):
    farm_id: str
    assigned_to: str
    task_type: str
    title: str
    description: str
    field_location: Optional[str] = None
    priority: str = "medium"
    estimated_hours: int = 8
    due_date: str
    quality_requirements: Optional[dict] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    completion_notes: Optional[str] = None

def generate_mock_task_data():
    """Generate mock task data"""
    task_types = [
        "harvesting", "planting", "pruning", "fertilizing", 
        "pest_control", "irrigation", "maintenance", "inspection",
        "processing", "drying", "sorting", "packaging"
    ]
    
    priorities = ["low", "medium", "high", "urgent"]
    statuses = ["pending", "in_progress", "completed", "cancelled"]
    
    locations = [
        "Block A - Section 1", "Block A - Section 2", "Block A - Section 3",
        "Block B - Section 1", "Block B - Section 2", "Block C - Section 1",
        "Processing Area", "Drying Yard", "Storage Warehouse", "Main Field"
    ]
    
    tasks = []
    for i in range(20):
        task_type = random.choice(task_types)
        status = random.choice(statuses)
        priority = random.choice(priorities)
        
        # Generate realistic task titles and descriptions
        if task_type == "harvesting":
            title = f"Harvest Coffee Cherries - {random.choice(locations)}"
            description = "Harvest only ripe red cherries, avoid overripe and underripe ones"
            quality_req = {"min_ripeness": 90, "max_defects": 5}
        elif task_type == "planting":
            title = f"Plant New Coffee Seedlings - {random.choice(locations)}"
            description = "Plant 100 coffee seedlings with proper spacing and soil preparation"
            quality_req = {"spacing_meters": 2.5, "soil_depth_cm": 40}
        elif task_type == "pruning":
            title = f"Prune Coffee Trees - {random.choice(locations)}"
            description = "Remove dead branches and suckers, maintain tree structure"
            quality_req = {"max_height": 2.5, "sucker_removal": 100}
        else:
            title = f"{task_type.title()} Task - {random.choice(locations)}"
            description = f"Complete {task_type} work according to farm standards"
            quality_req = {"quality_standard": "high"}
        
        due_date = datetime.now() + timedelta(days=random.randint(1, 14))
        created_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        task = {
            "task_id": f"task_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}",
            "farm_id": random.choice(["farm_son_pacamara", "farm_ta_nung", "farm_future_coffee"]),
            "assigned_to": f"farmer_{random.randint(1, 20)}",
            "assigned_by": f"supervisor_{random.randint(1, 3)}",
            "task_type": task_type,
            "title": title,
            "description": description,
            "field_location": random.choice(locations),
            "priority": priority,
            "estimated_hours": random.randint(4, 12),
            "due_date": due_date.isoformat(),
            "status": status,
            "progress_percentage": random.randint(0, 100) if status != "pending" else 0,
            "quality_requirements": quality_req,
            "completion_notes": "Task completed successfully" if status == "completed" else "",
            "supervisor_approval": status == "completed" and random.choice([True, False]),
            "created_at": created_date.isoformat(),
            "updated_at": datetime.now().isoformat(),
            "actual_hours": random.randint(3, 10) if status == "completed" else None,
            "quality_score": random.randint(70, 100) if status == "completed" else None
        }
        tasks.append(task)
    
    return tasks

@router.get("/tasks/{farmer_id}")
async def get_farmer_tasks(
    farmer_id: str,
    status: Optional[str] = None,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get tasks assigned to a specific farmer"""
    try:
        # Generate mock data
        all_tasks = generate_mock_task_data()
        
        # Filter by farmer
        farmer_tasks = [task for task in all_tasks if task["assigned_to"] == farmer_id]
        
        # Filter by status if provided
        if status:
            farmer_tasks = [task for task in farmer_tasks if task["status"] == status]
        
        return {
            "farmer_id": farmer_id,
            "tasks": farmer_tasks,
            "summary": {
                "total_tasks": len(farmer_tasks),
                "pending": len([t for t in farmer_tasks if t["status"] == "pending"]),
                "in_progress": len([t for t in farmer_tasks if t["status"] == "in_progress"]),
                "completed": len([t for t in farmer_tasks if t["status"] == "completed"]),
                "overdue": len([t for t in farmer_tasks 
                              if datetime.fromisoformat(t["due_date"].replace('Z', '+00:00')) < datetime.now() 
                              and t["status"] not in ["completed", "cancelled"]])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/farm/{farm_id}")
async def get_farm_tasks(
    farm_id: str,
    status: Optional[str] = None,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get all tasks for a specific farm"""
    try:
        # Generate mock data
        all_tasks = generate_mock_task_data()
        
        # Filter by farm
        farm_tasks = [task for task in all_tasks if task["farm_id"] == farm_id]
        
        # Filter by status if provided
        if status:
            farm_tasks = [task for task in farm_tasks if task["status"] == status]
        
        # Group by farmer
        tasks_by_farmer = {}
        for task in farm_tasks:
            farmer_id = task["assigned_to"]
            if farmer_id not in tasks_by_farmer:
                tasks_by_farmer[farmer_id] = []
            tasks_by_farmer[farmer_id].append(task)
        
        return {
            "farm_id": farm_id,
            "tasks": farm_tasks,
            "tasks_by_farmer": tasks_by_farmer,
            "summary": {
                "total_tasks": len(farm_tasks),
                "active_farmers": len(tasks_by_farmer),
                "pending": len([t for t in farm_tasks if t["status"] == "pending"]),
                "in_progress": len([t for t in farm_tasks if t["status"] == "in_progress"]),
                "completed": len([t for t in farm_tasks if t["status"] == "completed"]),
                "overdue": len([t for t in farm_tasks 
                              if datetime.fromisoformat(t["due_date"].replace('Z', '+00:00')) < datetime.now() 
                              and t["status"] not in ["completed", "cancelled"]])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/assign")
async def assign_task(
    task_data: TaskCreate,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Assign a new task to a farmer"""
    try:
        # Create task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
        
        # Create task record
        task = {
            "task_id": task_id,
            "farm_id": task_data.farm_id,
            "assigned_to": task_data.assigned_to,
            "assigned_by": "supervisor_01",  # Would come from auth context
            "task_type": task_data.task_type,
            "title": task_data.title,
            "description": task_data.description,
            "field_location": task_data.field_location,
            "priority": task_data.priority,
            "estimated_hours": task_data.estimated_hours,
            "due_date": task_data.due_date,
            "status": "pending",
            "progress_percentage": 0,
            "quality_requirements": task_data.quality_requirements or {},
            "completion_notes": "",
            "supervisor_approval": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "actual_hours": None,
            "quality_score": None
        }
        
        # In real implementation, save to Firebase
        # await firebase.save_document("tasks", task_id, task)
        
        return {
            "status": "success",
            "message": "Task assigned successfully",
            "task": task
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    update_data: TaskUpdate,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Update task status and progress"""
    try:
        # In real implementation, get and update task from Firebase
        # For now, return mock response
        
        updated_task = {
            "task_id": task_id,
            "status": update_data.status,
            "progress_percentage": update_data.progress_percentage,
            "completion_notes": update_data.completion_notes,
            "updated_at": datetime.now().isoformat()
        }
        
        if update_data.status == "completed":
            updated_task["completed_at"] = datetime.now().isoformat()
            updated_task["actual_hours"] = random.randint(4, 10)
            updated_task["quality_score"] = random.randint(70, 100)
        
        return {
            "status": "success",
            "message": "Task updated successfully",
            "task": updated_task
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/dashboard/{farm_id}")
async def get_tasks_dashboard(
    farm_id: str,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get task dashboard data for farm management"""
    try:
        # Generate mock data
        all_tasks = generate_mock_task_data()
        farm_tasks = [task for task in all_tasks if task["farm_id"] == farm_id]
        
        # Calculate statistics
        total_tasks = len(farm_tasks)
        completed_tasks = len([t for t in farm_tasks if t["status"] == "completed"])
        overdue_tasks = len([t for t in farm_tasks 
                           if datetime.fromisoformat(t["due_date"].replace('Z', '+00:00')) < datetime.now() 
                           and t["status"] not in ["completed", "cancelled"]])
        
        # Task type distribution
        task_type_counts = {}
        for task in farm_tasks:
            task_type = task["task_type"]
            task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
        
        # Priority distribution
        priority_counts = {}
        for task in farm_tasks:
            priority = task["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Farmer workload
        farmer_workload = {}
        for task in farm_tasks:
            farmer_id = task["assigned_to"]
            if farmer_id not in farmer_workload:
                farmer_workload[farmer_id] = {
                    "total_tasks": 0,
                    "pending": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "estimated_hours": 0
                }
            farmer_workload[farmer_id]["total_tasks"] += 1
            farmer_workload[farmer_id][task["status"]] += 1
            farmer_workload[farmer_id]["estimated_hours"] += task["estimated_hours"]
        
        return {
            "farm_id": farm_id,
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0,
                "overdue_tasks": overdue_tasks,
                "active_farmers": len(farmer_workload)
            },
            "task_type_distribution": task_type_counts,
            "priority_distribution": priority_counts,
            "farmer_workload": farmer_workload,
            "recent_completions": [
                task for task in farm_tasks 
                if task["status"] == "completed"
            ][:5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/performance/{farmer_id}")
async def get_farmer_task_performance(
    farmer_id: str,
    period_days: int = 30,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get farmer task performance metrics"""
    try:
        # Generate mock data
        all_tasks = generate_mock_task_data()
        farmer_tasks = [task for task in all_tasks if task["assigned_to"] == farmer_id]
        
        # Filter by period
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_tasks = [
            task for task in farmer_tasks 
            if datetime.fromisoformat(task["created_at"].replace('Z', '+00:00')) >= cutoff_date
        ]
        
        completed_tasks = [t for t in recent_tasks if t["status"] == "completed"]
        overdue_tasks = [
            t for t in recent_tasks 
            if datetime.fromisoformat(t["due_date"].replace('Z', '+00:00')) < datetime.now() 
            and t["status"] not in ["completed", "cancelled"]
        ]
        
        # Calculate metrics
        completion_rate = len(completed_tasks) / len(recent_tasks) if recent_tasks else 0
        avg_quality_score = sum(t["quality_score"] for t in completed_tasks if t["quality_score"]) / len(completed_tasks) if completed_tasks else 0
        on_time_completion = len([t for t in completed_tasks 
                                if datetime.fromisoformat(t.get("completed_at", t["updated_at"]).replace('Z', '+00:00')) <= 
                                   datetime.fromisoformat(t["due_date"].replace('Z', '+00:00'))]) / len(completed_tasks) if completed_tasks else 0
        
        return {
            "farmer_id": farmer_id,
            "period_days": period_days,
            "performance_metrics": {
                "total_tasks": len(recent_tasks),
                "completed_tasks": len(completed_tasks),
                "completion_rate": round(completion_rate * 100, 1),
                "overdue_tasks": len(overdue_tasks),
                "average_quality_score": round(avg_quality_score, 1),
                "on_time_completion_rate": round(on_time_completion * 100, 1),
                "total_hours_worked": sum(t["actual_hours"] for t in completed_tasks if t["actual_hours"])
            },
            "task_breakdown": {
                "harvesting": len([t for t in recent_tasks if t["task_type"] == "harvesting"]),
                "planting": len([t for t in recent_tasks if t["task_type"] == "planting"]),
                "maintenance": len([t for t in recent_tasks if t["task_type"] == "maintenance"]),
                "other": len([t for t in recent_tasks if t["task_type"] not in ["harvesting", "planting", "maintenance"]])
            },
            "recent_tasks": recent_tasks[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))