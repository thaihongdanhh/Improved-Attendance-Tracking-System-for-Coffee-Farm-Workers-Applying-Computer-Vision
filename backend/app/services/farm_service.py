from typing import List, Optional, Dict
from datetime import datetime
import math
from app.services.firebase_service import FirebaseService
from app.data.farms_data import FARMS_DATA

class FarmService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = "farms"
        # Initialize farms data on first run
        self._initialize_farms()
    
    def _normalize_farm_data(self, farm_data: Dict) -> Dict:
        """Add default values for missing fields to ensure schema compatibility"""
        defaults = {
            'plus_code': None,
            'established_year': None,
            'coffee_varieties': [],
            'fields': [],
            'coordinates': {'latitude': None, 'longitude': None},
            'area_hectares': None,
            'elevation': None,
            'owner': None,
            'contact': None
        }
        
        for key, default_value in defaults.items():
            if key not in farm_data:
                farm_data[key] = default_value
        
        return farm_data
    
    def _initialize_farms(self):
        """Initialize farms from data file if not already in database"""
        # This will be called once to populate the database
        pass
    
    async def get_all_farms(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict]:
        """Get all farms with optional search and pagination"""
        # Get farms from Firebase
        farms_ref = self.firebase.db.collection(self.collection)
        docs = farms_ref.stream()
        farms = []
        
        for doc in docs:
            farm_data = doc.to_dict()
            farm_data['id'] = doc.id
            farm_data = self._normalize_farm_data(farm_data)
            farms.append(farm_data)
        
        # If no farms in Firebase, fallback to FARMS_DATA for backwards compatibility
        if not farms:
            farms = FARMS_DATA.copy()
        
        # Apply search if provided
        if search:
            search_lower = search.lower()
            filtered_farms = []
            for farm in farms:
                if (search_lower in farm.get("name", "").lower() or 
                    search_lower in farm.get("location", "").lower() or
                    search_lower in farm.get("owner", "").lower()):
                    filtered_farms.append(farm)
            farms = filtered_farms
        
        # Apply pagination
        return farms[skip:skip + limit]
    
    async def get_farm(self, farm_id: str) -> Optional[Dict]:
        """Get a specific farm by ID"""
        # Try Firebase database first
        farm = await self.firebase.get_document(self.collection, farm_id)
        if farm:
            farm['id'] = farm_id
            farm = self._normalize_farm_data(farm)
            return farm
        
        # Fallback to FARMS_DATA
        for farm in FARMS_DATA:
            if farm["id"] == farm_id:
                return farm
                
        return None
    
    async def create_farm(self, farm_data: Dict) -> Dict:
        """Create a new farm"""
        farm_data["created_at"] = datetime.now().isoformat()
        farm_data["updated_at"] = datetime.now().isoformat()
        
        # Generate ID if not provided
        if "id" not in farm_data:
            farm_data["id"] = f"farm_{datetime.now().timestamp()}"
        
        await self.firebase.save_document(self.collection, farm_data["id"], farm_data)
        return farm_data
    
    async def update_farm(self, farm_id: str, update_data: Dict) -> Optional[Dict]:
        """Update a farm"""
        existing_farm = await self.get_farm(farm_id)
        if not existing_farm:
            return None
        
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Merge with existing data
        existing_farm.update(update_data)
        
        await self.firebase.save_document(self.collection, farm_id, existing_farm)
        return existing_farm
    
    async def delete_farm(self, farm_id: str) -> bool:
        """Delete a farm"""
        farm = await self.get_farm(farm_id)
        if not farm:
            return False
        
        # In production, would delete from database
        # For now, just return True for mock data
        return True
    
    async def get_nearby_farms(self, latitude: float, longitude: float, radius_km: float) -> List[Dict]:
        """Get farms within a certain radius using Haversine formula"""
        all_farms = await self.get_all_farms(limit=1000)
        nearby_farms = []
        
        for farm in all_farms:
            coords = farm.get("coordinates", {})
            farm_lat = coords.get("latitude")
            farm_lon = coords.get("longitude")
            
            if farm_lat and farm_lon:
                distance = self._calculate_distance(latitude, longitude, farm_lat, farm_lon)
                if distance <= radius_km:
                    farm_with_distance = farm.copy()
                    farm_with_distance["distance_km"] = round(distance, 2)
                    nearby_farms.append(farm_with_distance)
        
        # Sort by distance
        nearby_farms.sort(key=lambda x: x["distance_km"])
        return nearby_farms
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    async def populate_farms_data(self):
        """Populate database with initial farms data"""
        for farm_data in FARMS_DATA:
            farm_data["created_at"] = datetime.now().isoformat()
            farm_data["updated_at"] = datetime.now().isoformat()
            await self.firebase.save_document(self.collection, farm_data["id"], farm_data)
        return {"message": f"Populated {len(FARMS_DATA)} farms"}