#!/usr/bin/env python3
"""
Test API with real coffee beans images
"""
import requests
import json
import os

def test_with_real_image():
    print("🧪 TESTING API WITH REAL COFFEE BEANS IMAGE")
    print("=" * 60)
    
    # Use latest image
    image_path = "/mnt/data/AIFace/AICoffeePortal/backend/uploads/beans/beans_analysis_20250901_191520.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
        
    print(f"📸 Using image: {os.path.basename(image_path)}")
    print(f"📏 Image size: {os.path.getsize(image_path):,} bytes")
    
    # API endpoint
    url = "http://kmou.n2nai.io:5200/api/v1/coffee-beans/analyze-test"
    
    # Prepare request
    with open(image_path, 'rb') as f:
        files = {
            'file': (os.path.basename(image_path), f, 'image/jpeg')
        }
        data = {
            'notes': 'Testing BROKEN beans analysis with real image - checking for good_beans/defect_beans fields'
        }
        
        print("📤 Sending API request...")
        print(f"🌐 URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, timeout=45)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API call successful!")
                
                # Pretty print the response
                print("\n📋 FULL API RESPONSE:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Check analysis data specifically
                analysis = result.get('analysis', {})
                print(f"\n🔍 ANALYSIS BREAKDOWN:")
                
                # Check for old fields
                print(f"📊 Basic fields:")
                print(f"   total_beans: {analysis.get('total_beans', 'MISSING')}")
                print(f"   quality_score: {analysis.get('quality_score', 'MISSING')}")
                print(f"   weight_estimate: {analysis.get('weight_estimate', 'MISSING')}")
                
                # Check for NEW fields (the fix)
                print(f"🆕 New fields (the fix):")
                has_good_beans = 'good_beans' in analysis
                has_defect_beans = 'defect_beans' in analysis
                
                print(f"   good_beans: {analysis.get('good_beans', '❌ MISSING!')}")
                print(f"   defect_beans: {analysis.get('defect_beans', '❌ MISSING!')}")
                
                # Check defects array
                defects = analysis.get('defects', [])
                print(f"📋 Defects array ({len(defects)} entries):")
                for defect in defects:
                    print(f"   - {defect.get('type', 'NO_TYPE')}: {defect.get('count', 0)} beans ({defect.get('percentage', 0):.1f}%)")
                
                # Check defect_counts
                defect_counts = analysis.get('defect_counts', {})
                print(f"🔢 Defect counts:")
                for defect_type, count in defect_counts.items():
                    print(f"   {defect_type}: {count}")
                
                # Analyze if fix is working
                print(f"\n🎯 FIX STATUS:")
                if has_good_beans and has_defect_beans:
                    print(f"   ✅ NEW FIELDS ARE PRESENT!")
                    print(f"   ✅ Server has been updated with the fix")
                    
                    good_count = analysis.get('good_beans', 0)
                    defect_count = analysis.get('defect_beans', 0)
                    total = analysis.get('total_beans', 0)
                    
                    print(f"\n📈 Analysis Summary:")
                    print(f"   Total: {total} beans")
                    print(f"   Good: {good_count} beans (BROWN)")
                    print(f"   Defects: {defect_count} beans (BLACK, BROKEN, etc.)")
                    print(f"   Quality: {analysis.get('quality_score', 0)}%")
                    
                else:
                    print(f"   ❌ NEW FIELDS ARE MISSING!")
                    print(f"   ❌ Server still running old code")
                    print(f"   🔧 Need to restart backend server")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - server may be busy processing")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_real_image()