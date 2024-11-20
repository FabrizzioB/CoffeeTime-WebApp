"""
from passlib.context import CryptContext  # For password hashing
from backend.src.app.models import user  # User model for authentication

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
"""