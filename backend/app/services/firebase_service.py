from typing import Dict, List, Optional
from datetime import datetime
from app.core.config import settings
from app.core.security import get_password_hash
import asyncio
import traceback
from functools import wraps

# Conditional imports for Firebase
if not settings.USE_MOCK_FIREBASE:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage
    except ImportError:
        print("Warning: Firebase libraries not installed. Using mock mode.")
        settings.USE_MOCK_FIREBASE = True

def async_wrap(func):
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return run

# Global mock data storage for consistency
_MOCK_DATA_STORE = {
    "users": {},
    "farmers": {},
    "farms": {},
    "attendance": {},
    "coffee_beans": {},
    "coffee_leaves": {},
    "coffee_beans_analyses": {},
    "coffee_leaves_analyses": {}
}

class FirebaseService:
    def __init__(self):
        if settings.USE_MOCK_FIREBASE:
            self.db = None
            self.bucket = None
            # Use global mock data store
            self._mock_data = _MOCK_DATA_STORE
            
            # Initialize default data only if not already present
            if not self._mock_data["users"]:
                self._mock_data["users"] = {
                    "admin_1": {
                        "id": "admin_1",
                        "email": "admin@aicoffee.com",
                        "password": "$2b$12$nzb.Kqhwc384wB3vvsdw/uoyBYBizYxY5vxOU4wIG6sAGa1TZaUqi",  # password: admin123
                        "name": "Admin User",
                        "role": "admin",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    },
                    "user_1": {
                        "id": "user_1",
                        "email": "user@aicoffee.com",
                        "password": "$2b$12$nzb.Kqhwc384wB3vvsdw/uoyBYBizYxY5vxOU4wIG6sAGa1TZaUqi",  # password: admin123
                        "name": "Test User",
                        "role": "user",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            
            if not self._mock_data["farmers"]:
                self._mock_data["farmers"] = {
                    "farmer_1": {
                        "id": "farmer_1",
                        "name": "John Doe",
                        "email": "john@example.com",
                        "phone": "+84123456789",
                        "address": "123 Coffee Street",
                        "farm_id": "farm_1",
                        "face_enrolled": False,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    },
                    "farmer_2": {
                        "id": "farmer_2",
                        "name": "Jane Smith",
                        "email": "jane@example.com",
                        "phone": "+84987654321",
                        "address": "456 Bean Avenue",
                        "farm_id": "farm_1",
                        "face_enrolled": True,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            
            if not self._mock_data["farms"]:
                self._mock_data["farms"] = {
                    "farm_1": {
                        "id": "farm_1",
                        "name": "Green Valley Coffee Farm",
                        "location": "Da Lat, Lam Dong",
                        "size_hectares": 25.5,
                        "manager_name": "Mr. Nguyen",
                        "manager_phone": "+84333444555",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
        else:
            if 'firebase_admin' in globals() and not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CONFIG_PATH)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'kmou-aicofee.firebasestorage.app'
                })
            self.db = firestore.client() if 'firestore' in globals() else None
            self.bucket = storage.bucket() if 'storage' in globals() else None

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        if settings.USE_MOCK_FIREBASE:
            for user in self._mock_data["users"].values():
                if user["email"] == email:
                    return user
            return None
        else:
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = await async_wrap(query.get)()
            for doc in docs:
                return {**doc.to_dict(), "id": doc.id}
            return None

    async def create_user(self, user_data: Dict) -> Dict:
        user_data["password"] = get_password_hash(user_data["password"])
        user_data["created_at"] = datetime.now()
        user_data["updated_at"] = datetime.now()
        
        if settings.USE_MOCK_FIREBASE:
            user_id = f"user_{len(self._mock_data['users']) + 1}"
            user_data["id"] = user_id
            self._mock_data["users"][user_id] = user_data
            return user_data
        else:
            doc_ref = self.db.collection('users').document()
            user_data["id"] = doc_ref.id
            await async_wrap(doc_ref.set)(user_data)
            return user_data

    async def get_farmers(self) -> List[Dict]:
        if settings.USE_MOCK_FIREBASE:
            return list(self._mock_data["farmers"].values())
        else:
            farmers_ref = self.db.collection('farmers')
            docs = await async_wrap(farmers_ref.get)()
            return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    async def get_farmer(self, farmer_id: str) -> Optional[Dict]:
        if settings.USE_MOCK_FIREBASE:
            return self._mock_data["farmers"].get(farmer_id)
        else:
            doc_ref = self.db.collection('farmers').document(farmer_id)
            doc = await async_wrap(doc_ref.get)()
            if doc.exists:
                return {**doc.to_dict(), "id": doc.id}
            return None

    async def create_farmer(self, farmer_data: Dict) -> Dict:
        farmer_data["created_at"] = datetime.now()
        farmer_data["updated_at"] = datetime.now()
        farmer_data["face_enrolled"] = False
        
        if settings.USE_MOCK_FIREBASE:
            farmer_id = f"farmer_{len(self._mock_data['farmers']) + 1}"
            farmer_data["id"] = farmer_id
            self._mock_data["farmers"][farmer_id] = farmer_data
            return farmer_data
        else:
            doc_ref = self.db.collection('farmers').document()
            farmer_data["id"] = doc_ref.id
            await async_wrap(doc_ref.set)(farmer_data)
            return farmer_data

    async def update_farmer(self, farmer_id: str, update_data: Dict) -> Optional[Dict]:
        update_data["updated_at"] = datetime.now()
        
        if settings.USE_MOCK_FIREBASE:
            if farmer_id in self._mock_data["farmers"]:
                self._mock_data["farmers"][farmer_id].update(update_data)
                return self._mock_data["farmers"][farmer_id]
            return None
        else:
            doc_ref = self.db.collection('farmers').document(farmer_id)
            await async_wrap(doc_ref.update)(update_data)
            return await self.get_farmer(farmer_id)

    async def delete_farmer(self, farmer_id: str) -> bool:
        if settings.USE_MOCK_FIREBASE:
            if farmer_id in self._mock_data["farmers"]:
                del self._mock_data["farmers"][farmer_id]
                return True
            return False
        else:
            doc_ref = self.db.collection('farmers').document(farmer_id)
            await async_wrap(doc_ref.delete)()
            return True

    # Generic document methods
    async def save_document(self, collection: str, doc_id: str, data: Dict) -> Dict:
        """Save a document to a collection"""
        if settings.USE_MOCK_FIREBASE:
            if collection not in self._mock_data:
                self._mock_data[collection] = {}
            self._mock_data[collection][doc_id] = data
            return data
        else:
            doc_ref = self.db.collection(collection).document(doc_id)
            await async_wrap(doc_ref.set)(data)
            return data
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Get a document from a collection"""
        if settings.USE_MOCK_FIREBASE:
            return self._mock_data.get(collection, {}).get(doc_id)
        else:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = await async_wrap(doc_ref.get)()
            if doc.exists:
                return {**doc.to_dict(), "id": doc.id}
            return None
    
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document from a collection"""
        if settings.USE_MOCK_FIREBASE:
            if collection in self._mock_data and doc_id in self._mock_data[collection]:
                del self._mock_data[collection][doc_id]
                return True
            return False
        else:
            try:
                doc_ref = self.db.collection(collection).document(doc_id)
                await async_wrap(doc_ref.delete)()
                return True
            except Exception as e:
                print(f"Error deleting document: {e}")
                return False
    
    async def update_document(self, collection: str, doc_id: str, update_data: Dict) -> Optional[Dict]:
        """Update a document in a collection"""
        if settings.USE_MOCK_FIREBASE:
            if collection in self._mock_data and doc_id in self._mock_data[collection]:
                self._mock_data[collection][doc_id].update(update_data)
                return self._mock_data[collection][doc_id]
            return None
        else:
            try:
                doc_ref = self.db.collection(collection).document(doc_id)
                await async_wrap(doc_ref.update)(update_data)
                # Return the updated document
                doc = await async_wrap(doc_ref.get)()
                if doc.exists:
                    return {**doc.to_dict(), "id": doc.id}
                return None
            except Exception as e:
                print(f"Error updating document: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return None
    
    async def query_documents(self, collection: str, filters: List[tuple] = None) -> List[Dict]:
        """Query documents with filters"""
        if settings.USE_MOCK_FIREBASE:
            docs = self._mock_data.get(collection, {}).values()
            if filters:
                # Simple filter implementation for mock mode
                filtered_docs = []
                for doc in docs:
                    match = True
                    for field, op, value in filters:
                        doc_value = doc.get(field)
                        if op == "==" and doc_value != value:
                            match = False
                            break
                        elif op == ">=" and doc_value < value:
                            match = False
                            break
                        elif op == "<=" and doc_value > value:
                            match = False
                            break
                    if match:
                        filtered_docs.append(doc)
                return filtered_docs
            return list(docs)
        else:
            query = self.db.collection(collection)
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            docs = await async_wrap(query.get)()
            return [{**doc.to_dict(), "id": doc.id} for doc in docs]
    
    # Farm methods
    async def get_farms(self) -> List[Dict]:
        if settings.USE_MOCK_FIREBASE:
            return list(self._mock_data["farms"].values())
        else:
            farms_ref = self.db.collection('farms')
            docs = await async_wrap(farms_ref.get)()
            return [{**doc.to_dict(), "id": doc.id} for doc in docs]
    
    async def get_farm(self, farm_id: str) -> Optional[Dict]:
        if settings.USE_MOCK_FIREBASE:
            return self._mock_data["farms"].get(farm_id)
        else:
            doc_ref = self.db.collection('farms').document(farm_id)
            doc = await async_wrap(doc_ref.get)()
            if doc.exists:
                return {**doc.to_dict(), "id": doc.id}
            return None
    
    async def create_farm(self, farm_data: Dict) -> Dict:
        farm_data["created_at"] = datetime.now()
        farm_data["updated_at"] = datetime.now()
        
        if settings.USE_MOCK_FIREBASE:
            farm_id = f"farm_{len(self._mock_data['farms']) + 1}"
            farm_data["id"] = farm_id
            self._mock_data["farms"][farm_id] = farm_data
            return farm_data
        else:
            doc_ref = self.db.collection('farms').document()
            farm_data["id"] = doc_ref.id
            await async_wrap(doc_ref.set)(farm_data)
            return farm_data
    
    async def update_farm(self, farm_id: str, update_data: Dict) -> Optional[Dict]:
        update_data["updated_at"] = datetime.now()
        
        if settings.USE_MOCK_FIREBASE:
            if farm_id in self._mock_data["farms"]:
                self._mock_data["farms"][farm_id].update(update_data)
                return self._mock_data["farms"][farm_id]
            return None
        else:
            doc_ref = self.db.collection('farms').document(farm_id)
            await async_wrap(doc_ref.update)(update_data)
            return await self.get_farm(farm_id)
    
    async def delete_farm(self, farm_id: str) -> bool:
        if settings.USE_MOCK_FIREBASE:
            if farm_id in self._mock_data["farms"]:
                del self._mock_data["farms"][farm_id]
                return True
            return False
        else:
            doc_ref = self.db.collection('farms').document(farm_id)
            await async_wrap(doc_ref.delete)()
            return True

    # Attendance methods
    async def create_attendance(self, attendance_data: Dict) -> Dict:
        attendance_data["created_at"] = datetime.now()
        
        if settings.USE_MOCK_FIREBASE:
            attendance_id = f"attendance_{len(self._mock_data['attendance']) + 1}"
            attendance_data["id"] = attendance_id
            self._mock_data["attendance"][attendance_id] = attendance_data
            return attendance_data
        else:
            doc_ref = self.db.collection('attendance').document()
            attendance_data["id"] = doc_ref.id
            await async_wrap(doc_ref.set)(attendance_data)
            return attendance_data
    
    async def get_attendance_by_date(self, date: str) -> List[Dict]:
        if settings.USE_MOCK_FIREBASE:
            return [a for a in self._mock_data["attendance"].values() 
                   if a.get("date", "") == date]
        else:
            # Query by date field directly (stored as ISO date string)
            attendance_ref = self.db.collection('attendance')
            query = attendance_ref.where('date', '==', date)
            docs = await async_wrap(query.get)()
            return [{**doc.to_dict(), "id": doc.id} for doc in docs]
    
    async def get_attendance_stats(self) -> Dict:
        if settings.USE_MOCK_FIREBASE:
            total = len(self._mock_data["attendance"])
            return {
                "total_today": total,
                "total_week": total,
                "total_month": total,
                "average_confidence": 0.95
            }
        else:
            # In production, implement actual stats calculation
            return {
                "total_today": 0,
                "total_week": 0,
                "total_month": 0,
                "average_confidence": 0.0
            }
    
    # Storage methods
    async def upload_file(self, file_path: str, file_data: bytes, content_type: str = 'image/jpeg') -> str:
        if settings.USE_MOCK_FIREBASE:
            return f"https://storage.mock.com/{file_path}"
        else:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(file_data, content_type=content_type)
            blob.make_public()
            return blob.public_url
    
    async def delete_file(self, file_path: str) -> bool:
        if settings.USE_MOCK_FIREBASE:
            return True
        else:
            try:
                blob = self.bucket.blob(file_path)
                blob.delete()
                return True
            except Exception:
                return False