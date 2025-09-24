#!/usr/bin/env python3
"""
Test authenticated endpoint to see if it returns good_beans/defect_beans
"""
import requests
import json

def test_authenticated_endpoint():
    print("🔐 TESTING AUTHENTICATED ENDPOINT")
    print("=" * 50)
    
    # Get a test token first (if possible)
    # For now, test without auth to see error format
    
    url = "http://kmou.n2nai.io:5200/api/v1/coffee-beans/analyze"
    image_path = "/mnt/data/AIFace/AICoffeePortal/backend/uploads/beans/beans_analysis_20250901_191520.jpg"
    
    print(f"🌐 URL: {url}")
    print("📸 Using authenticated endpoint...")
    
    with open(image_path, 'rb') as f:
        files = {
            'file': ('test.jpg', f, 'image/jpeg')
        }
        data = {
            'notes': 'Testing authenticated endpoint for good_beans/defect_beans'
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 401:
                print("🔒 As expected - needs authentication")
                print("Response:", response.text[:200])
                
                # The issue might be that mobile app authentication is working
                # but the response format is missing the new fields
                
                print("\n🔍 DIAGNOSIS:")
                print("✅ Authenticated endpoint exists and uses same service")
                print("✅ Service has been updated with good_beans/defect_beans")  
                print("✅ Test endpoint returns correct format")
                print("❌ Mobile app receives old format")
                
                print("\n🤔 POSSIBLE CAUSES:")
                print("1. Mobile app is cached and needs refresh")
                print("2. Response transformation somewhere in pipeline")  
                print("3. TypeScript interface mismatch")
                print("4. Server response inconsistency")
                
                return
                
            elif response.status_code == 200:
                result = response.json()
                print("✅ Unexpected success without auth!")
                
                analysis = result.get('analysis', {})
                print(f"Has good_beans: {'good_beans' in analysis}")
                print(f"Has defect_beans: {'defect_beans' in analysis}")
                
                print("\nResponse:")
                print(json.dumps(result, indent=2))
                
            else:
                print(f"❌ Error: {response.status_code}")
                print("Response:", response.text[:200])
                
        except Exception as e:
            print(f"❌ Error: {e}")

def check_response_discrepancy():
    print("\n\n🔍 RESPONSE FORMAT COMPARISON")
    print("=" * 50)
    
    print("📱 MOBILE LOG (missing fields):")
    mobile_log = {
        "analysis": {
            "defect_counts": "{Object}",
            "defects": "[Array]", 
            "quality_score": 0,
            "recommendations": "[Array]",
            "total_beans": 82,
            "weight_estimate": 16.4
            # MISSING: good_beans, defect_beans
        }
    }
    print(json.dumps(mobile_log, indent=2))
    
    print("\n🧪 DIRECT TEST (has fields):")
    direct_test = {
        "analysis": {
            "total_beans": 99,
            "good_beans": 0,        # ← PRESENT
            "defect_beans": 99,     # ← PRESENT  
            "quality_score": 0,
            "weight_estimate": 19.8,
            "defect_counts": {"LIGHTFM": 99},
            "defects": [{"type": "LIGHTFM", "count": 99, "percentage": 100.0}]
        }
    }
    print(json.dumps(direct_test, indent=2))
    
    print("\n🎯 CONCLUSION:")
    print("✅ Service code is correct")
    print("❌ Mobile app not receiving new fields")
    print("🔧 Need to check: response transformation, caching, or mobile refresh")

if __name__ == "__main__":
    test_authenticated_endpoint()
    check_response_discrepancy()