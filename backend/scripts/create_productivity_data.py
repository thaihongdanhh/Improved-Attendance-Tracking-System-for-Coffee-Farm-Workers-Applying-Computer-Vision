#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime, timedelta, timezone
import random
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
from app.core.config import settings

# Initialize services
firebase_service = FirebaseService()

# Quality score patterns
QUALITY_PATTERNS = {
    "excellent": {"range": (85, 95), "defect_rate": (0.05, 0.15)},
    "good": {"range": (75, 85), "defect_rate": (0.15, 0.25)},
    "average": {"range": (65, 75), "defect_rate": (0.25, 0.35)},
    "poor": {"range": (50, 65), "defect_rate": (0.35, 0.50)}
}

# Disease patterns
DISEASE_PATTERNS = {
    "healthy": {"health_score": (85, 95), "infected_rate": (0.05, 0.15)},
    "minor_issues": {"health_score": (70, 85), "infected_rate": (0.15, 0.30)},
    "moderate_issues": {"health_score": (55, 70), "infected_rate": (0.30, 0.45)},
    "severe_issues": {"health_score": (40, 55), "infected_rate": (0.45, 0.60)}
}

# Coffee bean defect types
DEFECT_TYPES = ["BLACK", "BROKEN", "BROWN", "IMMATURE", "INSECT", "DAMAGED", "WITHERED", "SHELL"]

# Coffee leaf diseases
DISEASE_TYPES = [
    {"name": "Rust", "severity": ["low", "medium", "high"]},
    {"name": "Berry disease", "severity": ["low", "medium", "high"]},
    {"name": "Brown eye spot", "severity": ["low", "medium", "high"]},
    {"name": "Leaf miner", "severity": ["low", "medium"]},
    {"name": "Sooty mold", "severity": ["low", "medium"]}
]

async def create_coffee_beans_analysis(farmer_id, farmer_name, farm_id, date, quality_pattern="good"):
    """Create a coffee beans analysis record"""
    pattern = QUALITY_PATTERNS[quality_pattern]
    
    # Generate analysis data
    total_beans = random.randint(300, 600)
    quality_score = random.uniform(*pattern["range"])
    defect_rate = random.uniform(*pattern["defect_rate"])
    defect_beans = int(total_beans * defect_rate)
    good_beans = total_beans - defect_beans
    
    # Generate defect breakdown
    defects_breakdown = {}
    remaining_defects = defect_beans
    selected_defects = random.sample(DEFECT_TYPES, random.randint(3, 6))
    
    for i, defect in enumerate(selected_defects):
        if i == len(selected_defects) - 1:
            # Last defect gets remaining count
            defects_breakdown[defect] = remaining_defects
        else:
            # Random distribution
            count = random.randint(1, remaining_defects // (len(selected_defects) - i))
            defects_breakdown[defect] = count
            remaining_defects -= count
    
    # Generate recommendations based on quality
    recommendations = []
    if quality_score < 70:
        recommendations.extend([
            "Improve harvesting practices to reduce immature beans",
            "Enhance post-harvest processing to minimize defects",
            "Consider upgrading drying facilities"
        ])
    elif quality_score < 85:
        recommendations.extend([
            "Monitor moisture levels more closely during drying",
            "Implement better sorting practices",
            "Regular maintenance of processing equipment"
        ])
    else:
        recommendations.extend([
            "Maintain current high standards",
            "Consider specialty coffee certification",
            "Explore premium market opportunities"
        ])
    
    # Create analysis data
    analysis_data = {
        "user_id": farmer_id,
        "farmer_name": farmer_name,
        "farm_id": farm_id,
        "filename": f"beans_sample_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}.jpg",
        "analysis": {
            "total_beans": total_beans,
            "good_beans": good_beans,
            "defect_beans": defect_beans,
            "quality_score": round(quality_score, 2),
            "defects_breakdown": defects_breakdown,
            "recommendations": recommendations
        },
        "image_url": f"/uploads/beans/sample_{farmer_id}_{date.strftime('%Y%m%d')}.jpg",
        "created_at": datetime.combine(
            date,
            datetime.min.time()
        ).replace(
            hour=random.randint(8, 16),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            tzinfo=timezone(timedelta(hours=7))
        ).isoformat(),
        "notes": f"Sample analysis for quality assessment"
    }
    
    # Generate document ID
    doc_id = f"beans_{farmer_id}_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}"
    analysis_data["id"] = doc_id
    
    # Save to Firebase
    await firebase_service.save_document("coffee_beans_analyses", doc_id, analysis_data)
    
    return analysis_data

async def create_coffee_leaves_analysis(farmer_id, farmer_name, farm_id, date, health_pattern="healthy"):
    """Create a coffee leaves analysis record"""
    pattern = DISEASE_PATTERNS[health_pattern]
    
    # Generate analysis data
    total_leaves = random.randint(50, 150)
    health_score = random.uniform(*pattern["health_score"])
    infected_rate = random.uniform(*pattern["infected_rate"])
    infected_leaves = int(total_leaves * infected_rate)
    
    # Generate disease detections
    diseases_detected = []
    if infected_leaves > 0:
        num_diseases = random.randint(1, min(3, len(DISEASE_TYPES)))
        selected_diseases = random.sample(DISEASE_TYPES, num_diseases)
        
        for disease in selected_diseases:
            confidence = random.uniform(0.75, 0.95)
            severity = random.choice(disease["severity"])
            diseases_detected.append({
                "disease": disease["name"],
                "confidence": round(confidence, 2),
                "severity": severity,
                "bbox": [
                    random.randint(10, 200),
                    random.randint(10, 200),
                    random.randint(250, 400),
                    random.randint(250, 400)
                ]
            })
    
    # Generate recommendations based on health
    recommendations = []
    if health_score < 60:
        recommendations.extend([
            "Immediate fungicide application recommended",
            "Remove and destroy severely infected leaves",
            "Improve air circulation in the plantation",
            "Consult with agricultural extension officer"
        ])
    elif health_score < 80:
        recommendations.extend([
            "Monitor disease progression closely",
            "Apply preventive fungicide treatment",
            "Ensure proper nutrition for plant resistance",
            "Maintain optimal shade levels"
        ])
    else:
        recommendations.extend([
            "Continue regular monitoring",
            "Maintain current management practices",
            "Ensure balanced nutrition program"
        ])
    
    # Create analysis data
    analysis_data = {
        "user_id": farmer_id,
        "farmer_name": farmer_name,
        "farm_id": farm_id,
        "filename": f"leaves_sample_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}.jpg",
        "analysis": {
            "total_leaves": total_leaves,
            "infected_leaves": infected_leaves,
            "health_score": round(health_score, 2),
            "diseases_detected": diseases_detected,
            "recommendations": recommendations
        },
        "image_url": f"/uploads/leaves/sample_{farmer_id}_{date.strftime('%Y%m%d')}.jpg",
        "created_at": datetime.combine(
            date,
            datetime.min.time()
        ).replace(
            hour=random.randint(8, 16),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            tzinfo=timezone(timedelta(hours=7))
        ).isoformat(),
        "notes": f"Leaf health assessment"
    }
    
    # Generate document ID
    doc_id = f"leaves_{farmer_id}_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}"
    analysis_data["id"] = doc_id
    
    # Save to Firebase
    await firebase_service.save_document("coffee_leaves_analyses", doc_id, analysis_data)
    
    return analysis_data

async def main():
    """Create dummy productivity data"""
    print("Creating dummy productivity data...")
    
    # Get all farmers
    farmers = await firebase_service.query_documents("farmers")
    print(f"Found {len(farmers)} farmers")
    
    # Define productivity profiles for farmers
    farmer_profiles = {}
    for i, farmer in enumerate(farmers):
        # Assign different productivity profiles
        if i < len(farmers) * 0.2:  # Top 20% performers
            farmer_profiles[farmer["id"]] = {
                "quality_pattern": "excellent",
                "health_pattern": "healthy",
                "analysis_frequency": 0.8  # 80% chance of analysis per week
            }
        elif i < len(farmers) * 0.5:  # Next 30% good performers
            farmer_profiles[farmer["id"]] = {
                "quality_pattern": "good",
                "health_pattern": "minor_issues",
                "analysis_frequency": 0.6
            }
        elif i < len(farmers) * 0.8:  # Next 30% average performers
            farmer_profiles[farmer["id"]] = {
                "quality_pattern": "average",
                "health_pattern": "moderate_issues",
                "analysis_frequency": 0.4
            }
        else:  # Bottom 20% poor performers
            farmer_profiles[farmer["id"]] = {
                "quality_pattern": "poor",
                "health_pattern": "severe_issues",
                "analysis_frequency": 0.2
            }
    
    # Generate data for the last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    beans_count = 0
    leaves_count = 0
    
    # Iterate through each day
    current_date = start_date
    while current_date <= end_date:
        print(f"\nCreating analyses for {current_date}...")
        
        for farmer in farmers:
            farmer_id = farmer.get("id")
            farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
            farm_id = farmer.get("farm_id", "default_farm")
            profile = farmer_profiles[farmer_id]
            
            # Randomly decide if farmer has analysis this day based on frequency
            if random.random() < profile["analysis_frequency"] / 7:  # Weekly frequency to daily
                # Create coffee beans analysis
                try:
                    await create_coffee_beans_analysis(
                        farmer_id=farmer_id,
                        farmer_name=farmer_name,
                        farm_id=farm_id,
                        date=current_date,
                        quality_pattern=profile["quality_pattern"]
                    )
                    beans_count += 1
                except Exception as e:
                    print(f"  Error creating beans analysis for {farmer_name}: {e}")
                
                # Sometimes create leaves analysis too (50% chance)
                if random.random() < 0.5:
                    try:
                        await create_coffee_leaves_analysis(
                            farmer_id=farmer_id,
                            farmer_name=farmer_name,
                            farm_id=farm_id,
                            date=current_date,
                            health_pattern=profile["health_pattern"]
                        )
                        leaves_count += 1
                    except Exception as e:
                        print(f"  Error creating leaves analysis for {farmer_name}: {e}")
        
        current_date += timedelta(days=1)
    
    print(f"\nTotal analyses created:")
    print(f"  Coffee beans analyses: {beans_count}")
    print(f"  Coffee leaves analyses: {leaves_count}")
    
    # Print summary by farmer profile
    print("\nSummary by farmer profile:")
    excellent_farmers = sum(1 for p in farmer_profiles.values() if p["quality_pattern"] == "excellent")
    good_farmers = sum(1 for p in farmer_profiles.values() if p["quality_pattern"] == "good")
    average_farmers = sum(1 for p in farmer_profiles.values() if p["quality_pattern"] == "average")
    poor_farmers = sum(1 for p in farmer_profiles.values() if p["quality_pattern"] == "poor")
    
    print(f"  Excellent performers: {excellent_farmers} farmers")
    print(f"  Good performers: {good_farmers} farmers")
    print(f"  Average performers: {average_farmers} farmers")
    print(f"  Poor performers: {poor_farmers} farmers")

if __name__ == "__main__":
    asyncio.run(main())