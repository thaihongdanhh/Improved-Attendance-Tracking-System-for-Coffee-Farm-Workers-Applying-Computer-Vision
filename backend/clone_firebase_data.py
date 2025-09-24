import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# Initialize both Firebase projects
def init_firebase_apps():
    # Source Firebase (AIFaceKMOU_v2)
    cred_source = credentials.Certificate("app/credentials/firebase-aiface.json")
    source_app = firebase_admin.initialize_app(cred_source, name='source')
    source_db = firestore.client(app=source_app)
    
    # Target Firebase (AICoffeePortal)
    cred_target = credentials.Certificate("app/credentials/firebase-admin.json")
    target_app = firebase_admin.initialize_app(cred_target, name='target')
    target_db = firestore.client(app=target_app)
    
    return source_db, target_db

def get_farms_mapping(target_db):
    """Get existing farms from target database"""
    farms_ref = target_db.collection('farms')
    farms = farms_ref.stream()
    
    farms_mapping = {}
    for farm in farms:
        farm_data = farm.to_dict()
        farms_mapping[farm.id] = farm_data
        print(f"Found farm: {farm.id} - {farm_data.get('name', 'Unknown')}")
    
    return farms_mapping

def import_farms_data(target_db):
    """Import farms data from farms_data.py"""
    from app.data.farms_data import FARMS_DATA
    
    print("\n=== Importing Farms Data ===")
    farms_mapping = {}
    
    for farm_data in FARMS_DATA[:3]:  # Import first 3 farms only
        farm_id = farm_data['id']
        
        # Convert fields to sections format
        sections = []
        for field in farm_data.get('fields', []):
            sections.append({
                "id": field['id'],
                "name": field['name'],
                "area": field['area']
            })
        
        farm_doc = {
            "id": farm_id,
            "name": farm_data['name'],
            "location": farm_data['location'],
            "area_hectares": farm_data['area_hectares'],
            "elevation": farm_data['elevation'],
            "coffee_varieties": farm_data['coffee_varieties'],
            "owner": farm_data['owner'],
            "contact": farm_data['contact'],
            "sections": sections,
            "fields": farm_data['fields'],
            "coordinates": farm_data['coordinates'],
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        target_db.collection('farms').document(farm_id).set(farm_doc)
        farms_mapping[farm_id] = farm_doc
        print(f"Imported farm: {farm_id} - {farm_data['name']}")
    
    return farms_mapping

def clone_farmers_data(source_db, target_db):
    """Clone farmers from source to target with farm mapping"""
    print("\n=== Cloning Farmers Data ===")
    
    # Import farms data first
    farms_mapping = import_farms_data(target_db)
    
    # Get farm IDs for rotation
    farm_ids = list(farms_mapping.keys())
    if not farm_ids:
        print("No farms available!")
        return
    
    # Get farmers from source
    farmers_ref = source_db.collection('farmers')
    farmers = farmers_ref.stream()
    
    count = 0
    for farmer in farmers:
        farmer_data = farmer.to_dict()
        farmer_id = farmer.id
        
        # Rotate through farms
        farm_index = count % len(farm_ids)
        selected_farm_id = farm_ids[farm_index]
        selected_farm = farms_mapping[selected_farm_id]
        
        # Map to new farm structure
        farmer_data['farm_id'] = selected_farm_id
        farmer_data['farm_name'] = selected_farm['name']
        
        # Assign field/section (rotate through available fields)
        fields = selected_farm.get('fields', [])
        if fields:
            field_index = count % len(fields)
            farmer_data['field_id'] = fields[field_index]['id']
            farmer_data['field_name'] = fields[field_index]['name']
            # Also keep section for compatibility
            farmer_data['section_id'] = fields[field_index]['id']
            farmer_data['section_name'] = fields[field_index]['name']
        
        # Ensure required fields
        farmer_data['is_active'] = farmer_data.get('is_active', True)
        farmer_data['created_at'] = farmer_data.get('created_at', datetime.now().isoformat())
        farmer_data['has_face_enrolled'] = farmer_data.get('has_face_enrolled', False)
        
        # Clone to target
        target_db.collection('farmers').document(farmer_id).set(farmer_data)
        count += 1
        
        print(f"Cloned farmer: {farmer_id} - {farmer_data.get('name', 'Unknown')} -> Farm: {farmer_data['farm_name']}, Field: {farmer_data.get('field_name', 'N/A')}")
    
    print(f"\nTotal farmers cloned: {count}")

def clone_attendance_data(source_db, target_db):
    """Clone attendance records from source to target"""
    print("\n=== Cloning Attendance Data ===")
    
    # Get farmer mappings from target to know their farms
    farmers_ref = target_db.collection('farmers')
    farmers = farmers_ref.stream()
    
    farmer_farm_mapping = {}
    for farmer in farmers:
        farmer_data = farmer.to_dict()
        farmer_farm_mapping[farmer.id] = {
            'farm_id': farmer_data.get('farm_id'),
            'farm_name': farmer_data.get('farm_name')
        }
    
    # Get attendance from source (last 30 days)
    attendance_ref = source_db.collection('attendance')
    attendances = attendance_ref.limit(100).stream()  # Limit to recent records
    
    count = 0
    for attendance in attendances:
        attendance_data = attendance.to_dict()
        attendance_id = attendance.id
        
        # Map to correct farm based on farmer
        farmer_id = attendance_data.get('farmer_id')
        if farmer_id and farmer_id in farmer_farm_mapping:
            attendance_data['farm_id'] = farmer_farm_mapping[farmer_id]['farm_id']
            attendance_data['farm_name'] = farmer_farm_mapping[farmer_id]['farm_name']
        else:
            # Default to first farm if farmer not found
            attendance_data['farm_id'] = 'farm_ta_nung'
            attendance_data['farm_name'] = 'Em Tà Nung Coffee Farm'
        
        # Clone to target
        target_db.collection('attendance').document(attendance_id).set(attendance_data)
        count += 1
        
        date = attendance_data.get('date', 'Unknown')
        print(f"Cloned attendance: {attendance_id} - Farmer: {farmer_id}, Date: {date}, Farm: {attendance_data.get('farm_name')}")
    
    print(f"\nTotal attendance records cloned: {count}")

def main():
    try:
        # Initialize Firebase apps
        source_db, target_db = init_firebase_apps()
        
        print("=== Firebase Data Clone Tool ===")
        print("Source: AIFaceKMOU_v2 (kmou-aiface-v2)")
        print("Target: AICoffeePortal")
        
        # Clone farmers
        clone_farmers_data(source_db, target_db)
        
        # Clone attendance
        clone_attendance_data(source_db, target_db)
        
        print("\n=== Clone completed successfully! ===")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()