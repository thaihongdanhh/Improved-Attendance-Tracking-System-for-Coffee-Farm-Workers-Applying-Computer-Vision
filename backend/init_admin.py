import asyncio
from app.services.firebase_service import FirebaseService
from app.core.security import get_password_hash

async def create_admin_user():
    """Create default admin user"""
    firebase = FirebaseService()
    
    # Check if admin already exists
    existing_admin = await firebase.get_user_by_email("admin@aicoffee.com")
    if existing_admin:
        print("Admin user already exists")
        return
    
    # Create admin user
    admin_data = {
        "id": "admin_1",
        "email": "admin@aicoffee.com",
        "password": get_password_hash("admin123"),
        "name": "Admin User",
        "role": "admin",
        "is_active": True
    }
    
    await firebase.create_user(admin_data)
    print("Admin user created successfully!")
    print("Email: admin@aicoffee.com")
    print("Password: admin123")

if __name__ == "__main__":
    asyncio.run(create_admin_user())