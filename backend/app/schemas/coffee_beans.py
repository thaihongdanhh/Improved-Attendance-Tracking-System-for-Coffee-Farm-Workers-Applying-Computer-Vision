from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class BeanDefect(BaseModel):
    type: str
    count: int
    percentage: float

class CoffeeBeanAnalysis(BaseModel):
    total_beans: int
    defects: List[BeanDefect]
    defect_counts: Dict[str, int]
    quality_score: float
    weight_estimate: float
    recommendations: List[str]

class CoffeeBeanResult(BaseModel):
    id: str
    analysis: CoffeeBeanAnalysis
    image_url: str
    timestamp: str = None
    created_at: datetime = None
    farm_id: str = None
    field_id: str = None
    notes: str = None
    filename: str = None
    user_id: str = None

    class Config:
        from_attributes = True