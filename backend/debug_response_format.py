#!/usr/bin/env python3
"""
Debug the actual response format from the API
"""

def analyze_broken_beans_logic():
    print("🔍 DEBUGGING BROKEN BEANS ANALYSIS")
    print("=" * 60)
    
    # Simulate what should happen with 82 BROKEN beans
    print("📊 Input from log:")
    print("   Detected: 82 BROKENs")
    print("   Image size: 1280x960")
    print()
    
    # The service logic
    defect_classes = {
        0: "BLACK", 1: "BROKEN", 2: "BROWN", 3: "BigBroken", 
        4: "IMMATURE", 5: "INSECT", 6: "MOLD", 7: "PartlyBlack", 
        8: "LIGHTFM", 9: "HEAVYFM"
    }
    
    good_classes = {"BROWN"}
    defect_classes_list = {
        "BLACK", "BROKEN", "BigBroken", "IMMATURE", 
        "INSECT", "MOLD", "PartlyBlack", "LIGHTFM", "HEAVYFM"
    }
    
    # Simulate the analysis
    defect_counts = {"BROKEN": 82}
    total_beans = 82
    
    # Calculate using fixed logic
    defect_count = sum(count for defect, count in defect_counts.items() 
                     if defect in defect_classes_list)
    good_count = sum(count for defect, count in defect_counts.items() 
                   if defect in good_classes)
    
    # Quality score
    defect_percentage = (defect_count / total_beans) * 100
    quality_score = max(0, 100 - defect_percentage)
    
    # Defects array
    defects = []
    for defect_type, count in defect_counts.items():
        if defect_type in defect_classes_list:
            defects.append({
                "type": defect_type,
                "count": count,
                "percentage": (count / total_beans) * 100
            })
    
    print("✅ Expected API Response:")
    expected_response = {
        "success": True,
        "analysis": {
            "total_beans": total_beans,
            "defects": defects,
            "defect_counts": defect_counts,
            "good_beans": good_count,        # NEW FIELD
            "defect_beans": defect_count,    # NEW FIELD  
            "quality_score": round(quality_score, 2),
            "weight_estimate": round(total_beans * 0.2, 2),
            "recommendations": [
                "High breakage rate (100.0%). Check processing equipment."
            ]
        },
        "image_url": "firebase_url",
        "timestamp": "2025-09-01T19:15:20"
    }
    
    import json
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))
    
    print("\n🎯 Key Points:")
    print(f"   ✅ total_beans: {total_beans}")
    print(f"   ❌ defect_beans: {defect_count} (82 BROKEN beans)")  
    print(f"   ✅ good_beans: {good_count} (0 - no BROWN beans)")
    print(f"   ❌ quality_score: {quality_score}% (0% - all defective)")
    print(f"   📋 defects array: 1 entry (BROKEN: 82 beans, 100%)")
    
    print("\n💡 Frontend should display:")
    print("   - Total Beans: 82")
    print("   - Good Beans: 0") 
    print("   - Defect Beans: 82")
    print("   - Quality Score: 0%")
    print("   - Defects: BROKEN (82 beans - 100%)")

if __name__ == "__main__":
    analyze_broken_beans_logic()