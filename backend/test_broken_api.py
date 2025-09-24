#!/usr/bin/env python3
"""
Test BROKEN beans analysis API on real domain
"""
import requests
import json
import os

def test_broken_beans_api():
    # API endpoint
    url = "http://kmou.n2nai.io:5200/api/v1/coffee-beans/analyze-test"
    
    print("🧪 Testing BROKEN beans analysis API")
    print("=" * 50)
    print(f"URL: {url}")
    
    # Create a dummy image file for testing
    test_image_path = "test_image.jpg"
    
    # Create a simple test image (1x1 pixel)
    try:
        from PIL import Image
        import io
        
        # Create a simple 100x100 test image
        img = Image.new('RGB', (100, 100), color='brown')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Prepare files and data
        files = {
            'file': ('test_broken_beans.jpg', img_bytes.getvalue(), 'image/jpeg')
        }
        data = {
            'notes': 'Test for BROKEN beans classification fix'
        }
        
        print("📤 Sending request...")
        
        # Make request
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print("\n📋 Analysis Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check specific fields
            analysis = result.get('analysis', {})
            print(f"\n🔍 Key metrics:")
            print(f"   total_beans: {analysis.get('total_beans', 'Missing!')}")
            print(f"   good_beans: {analysis.get('good_beans', 'Missing!')}")
            print(f"   defect_beans: {analysis.get('defect_beans', 'Missing!')}")
            print(f"   quality_score: {analysis.get('quality_score', 'Missing!')}")
            
            defects = analysis.get('defects', [])
            print(f"   defects array length: {len(defects)}")
            for defect in defects:
                print(f"     - {defect}")
                
        else:
            print(f"❌ API call failed!")
            print(f"Response: {response.text}")
            
    except ImportError:
        print("❌ PIL not available, using text file as test")
        
        # Fallback: use a text file as image
        with open('test_file.txt', 'w') as f:
            f.write('Test content for API')
            
        files = {
            'file': ('test_broken_beans.txt', open('test_file.txt', 'rb'), 'text/plain')
        }
        data = {
            'notes': 'Test for BROKEN beans classification fix (text file)'
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"📊 Response Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        finally:
            files['file'][1].close()
            os.remove('test_file.txt')
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_broken_beans_api()