from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from datetime import datetime, timedelta
import random

router = APIRouter()

# Mock data generators
def generate_mock_beans_analysis():
    """Generate mock coffee beans analysis data"""
    analyses = []
    for i in range(20):
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        analyses.append({
            "id": f"mock_beans_{i}",
            "user_id": f"farmer_{random.randint(1, 10)}",
            "farm_id": random.choice(["farm_son_pacamara", "farm_ta_nung", "farm_future_coffee"]),
            "created_at": created_at.isoformat(),
            "analysis": {
                "total_beans": random.randint(300, 600),
                "good_beans": random.randint(200, 500),
                "defect_beans": random.randint(50, 150),
                "quality_score": random.uniform(65, 95),
                "defects_breakdown": {
                    "BLACK": random.randint(10, 50),
                    "BROKEN": random.randint(20, 80),
                    "BROWN": random.randint(5, 30),
                    "IMMATURE": random.randint(10, 40)
                }
            },
            "image_url": f"/uploads/beans/sample_{i}.jpg"
        })
    return analyses

def generate_mock_leaves_analysis():
    """Generate mock coffee leaves analysis data"""
    analyses = []
    diseases = ["Rust", "Berry disease", "Brown eye spot", "Leaf miner"]
    
    for i in range(15):
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        infected = random.randint(0, 50)
        total = random.randint(50, 150)
        
        diseases_detected = []
        if infected > 0:
            num_diseases = random.randint(1, 3)
            for _ in range(num_diseases):
                disease = random.choice(diseases)
                diseases_detected.append({
                    "disease": disease,
                    "confidence": random.uniform(0.7, 0.95),
                    "severity": random.choice(["low", "medium", "high"])
                })
        
        analyses.append({
            "id": f"mock_leaves_{i}",
            "user_id": f"farmer_{random.randint(1, 10)}",
            "farm_id": random.choice(["farm_son_pacamara", "farm_ta_nung", "farm_future_coffee"]),
            "created_at": created_at.isoformat(),
            "analysis": {
                "total_leaves": total,
                "infected_leaves": infected,
                "health_score": 100 - (infected / total * 100) if total > 0 else 100,
                "diseases_detected": diseases_detected
            },
            "image_url": f"/uploads/leaves/sample_{i}.jpg"
        })
    return analyses

@router.get("/coffee-beans/analyses")
async def get_mock_beans_analyses(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get mock coffee beans analyses"""
    return generate_mock_beans_analysis()[:limit]

@router.get("/coffee-leaves/analyses")
async def get_mock_leaves_analyses(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get mock coffee leaves analyses"""
    return generate_mock_leaves_analysis()[:limit]