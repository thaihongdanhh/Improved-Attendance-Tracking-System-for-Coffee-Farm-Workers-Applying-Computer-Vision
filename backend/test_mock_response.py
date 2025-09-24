#!/usr/bin/env python3
"""
Test mock response to verify response format
"""

import sys
sys.path.append('.')
import os
os.environ['YOLO_BEANS_MODEL_PATH'] = '/nonexistent/path'  # Force mock mode

def test_mock_response():
    print("🧪 TESTING MOCK RESPONSE FORMAT")
    print("=" * 50)
    
    try:
        from app.services.coffee_beans_service import CoffeeBeansService
        
        service = CoffeeBeansService()
        print(f"✅ Service initialized (mock_mode: {service.mock_mode})")
        
        # Test mock generation
        mock_result = service._generate_mock_results()
        
        print("\n📋 Mock Response Structure:")
        print(f"Success: {mock_result['success']}")
        
        analysis = mock_result['analysis']
        print(f"Analysis keys: {list(analysis.keys())}")
        
        print(f"\n📊 Mock Analysis Data:")
        print(f"   total_beans: {analysis['total_beans']}")
        print(f"   quality_score: {analysis['quality_score']}")
        print(f"   weight_estimate: {analysis['weight_estimate']}")
        
        # Check if new fields exist
        print(f"   good_beans: {analysis.get('good_beans', '❌ MISSING!')}")
        print(f"   defect_beans: {analysis.get('defect_beans', '❌ MISSING!')}")
        
        print(f"\n🔍 Defects array:")
        for defect in analysis['defects']:
            print(f"   - {defect}")
        
        print(f"\n📈 Defect counts:")
        for defect_type, count in analysis['defect_counts'].items():
            print(f"   {defect_type}: {count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mock_response()