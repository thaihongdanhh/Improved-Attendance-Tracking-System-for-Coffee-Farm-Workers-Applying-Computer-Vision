from app.core.security import get_password_hash

# Generate password hash for admin123
password = "admin123"
hashed = get_password_hash(password)
print(f"Password: {password}")
print(f"Hash: {hashed}")

# Test verify
from app.core.security import verify_password
print(f"Verify: {verify_password(password, hashed)}")