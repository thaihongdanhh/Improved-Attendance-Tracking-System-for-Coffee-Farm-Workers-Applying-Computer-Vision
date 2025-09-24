import asyncio
from app.services.firebase_service import FirebaseService
from app.core.security import verify_password, get_password_hash

async def check_admin():
    """Check admin user"""
    firebase = FirebaseService()
    
    # Get admin user
    admin = await firebase.get_user_by_email("admin@aicoffee.com")
    if admin:
        print("Admin user found:")
        print(f"ID: {admin.get('id')}")
        print(f"Email: {admin.get('email')}")
        print(f"Name: {admin.get('name')}")
        print(f"Role: {admin.get('role')}")
        print(f"Has password: {'password' in admin}")
        
        # Test password
        if 'password' in admin:
            is_valid = verify_password("admin123", admin['password'])
            print(f"Password 'admin123' is valid: {is_valid}")
            
            # If not valid, update password
            if not is_valid:
                print("\nUpdating password...")
                admin['password'] = get_password_hash("admin123")
                await firebase.save_document("users", admin['id'], admin)
                print("Password updated to 'admin123'")
    else:
        print("Admin user not found")

if __name__ == "__main__":
    asyncio.run(check_admin())