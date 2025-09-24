#!/usr/bin/env python3
"""
Test script to debug BROKEN beans classification logic
"""

# Simulate the service logic
class TestCoffeeBeansService:
    def __init__(self):
        # Classes mapping
        self.defect_classes = {
            0: "BLACK",
            1: "BROKEN", 
            2: "BROWN",
            3: "BigBroken",
            4: "IMMATURE",
            5: "INSECT",
            6: "MOLD",
            7: "PartlyBlack",
            8: "LIGHTFM",
            9: "HEAVYFM"
        }
        
        # Define which classes are considered GOOD vs DEFECTS
        self.good_classes = {"BROWN"}  # BROWN beans are good quality
        self.defect_classes_list = {
            "BLACK", "BROKEN", "BigBroken", "IMMATURE", 
            "INSECT", "MOLD", "PartlyBlack", "LIGHTFM", "HEAVYFM"
        }

def test_broken_logic():
    service = TestCoffeeBeansService()
    
    print("🧪 TESTING BROKEN BEANS LOGIC")
    print("=" * 50)
    
    # Test case from user's log: 82 BROKENs
    defect_counts = {"BROKEN": 82}
    total_beans = 82
    
    print(f"📊 Input data:")
    print(f"   defect_counts: {defect_counts}")
    print(f"   total_beans: {total_beans}")
    print()
    
    # Calculate defects using current logic
    defect_count = sum(count for defect, count in defect_counts.items() 
                     if defect in service.defect_classes_list)
    good_count = sum(count for defect, count in defect_counts.items() 
                   if defect in service.good_classes)
    
    print(f"🔍 Logic check:")
    print(f"   Is 'BROKEN' in defect_classes_list? {'BROKEN' in service.defect_classes_list}")
    print(f"   Is 'BROKEN' in good_classes? {'BROKEN' in service.good_classes}")
    print()
    
    # Calculate quality score
    if total_beans > 0:
        defect_percentage = (defect_count / total_beans) * 100
        quality_score = max(0, 100 - defect_percentage)
    else:
        quality_score = 0
    
    print(f"📈 Results:")
    print(f"   good_count: {good_count}")
    print(f"   defect_count: {defect_count}")
    print(f"   defect_percentage: {defect_percentage:.2f}%")
    print(f"   quality_score: {quality_score:.2f}%")
    print()
    
    # Prepare defects list
    defects = []
    for defect_type, count in defect_counts.items():
        if defect_type in service.defect_classes_list:
            defects.append({
                "type": defect_type,
                "count": count,
                "percentage": (count / total_beans) * 100
            })
    
    print(f"📋 Defects array:")
    for defect in defects:
        print(f"   - {defect}")
    print()
    
    # Expected behavior
    print(f"✅ Expected behavior:")
    print(f"   - BROKEN beans should be classified as DEFECTS")
    print(f"   - defect_count should be: 82")
    print(f"   - quality_score should be: 0% (100% defective)")
    print(f"   - defects array should contain BROKEN entry")
    
    if defect_count == 82 and quality_score == 0:
        print(f"   ✅ LOGIC IS CORRECT!")
    else:
        print(f"   ❌ LOGIC HAS ISSUES!")

if __name__ == "__main__":
    test_broken_logic()