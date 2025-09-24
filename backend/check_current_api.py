#!/usr/bin/env python3
"""
Check current API response format
"""
import requests
import json

def check_api_response():
    print("🔍 CHECKING CURRENT API RESPONSE")
    print("=" * 50)
    
    # Check if server has our changes
    url = "http://kmou.n2nai.io:5200/api/v1/coffee-beans/analyze-test"
    
    # Create a simple test payload
    import io
    from PIL import Image
    
    try:
        # Create test image
        img = Image.new('RGB', (100, 100), color='brown')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            'file': ('test.jpg', img_bytes.getvalue(), 'image/jpeg')
        }
        data = {
            'notes': 'Check new fields: good_beans, defect_beans'
        }
        
        print("📤 Sending API request...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received!")
            
            analysis = result.get('analysis', {})
            
            print("\n🔍 Checking for new fields:")
            print(f"   good_beans: {'✅ PRESENT' if 'good_beans' in analysis else '❌ MISSING'}")
            print(f"   defect_beans: {'✅ PRESENT' if 'defect_beans' in analysis else '❌ MISSING'}")
            
            print(f"\n📋 All analysis fields:")
            for key, value in analysis.items():
                print(f"   {key}: {value}")
                
            if 'good_beans' in analysis and 'defect_beans' in analysis:
                print(f"\n✅ NEW FIELDS ARE PRESENT!")
                print(f"   Server has been updated with the fix")
            else:
                print(f"\n❌ NEW FIELDS ARE MISSING!")
                print(f"   Server needs to be restarted or code not deployed")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except ImportError:
        print("❌ PIL not available for image creation")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api_response()