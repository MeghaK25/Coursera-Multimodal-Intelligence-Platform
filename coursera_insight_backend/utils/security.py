from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from config import SECRET_KEY

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Hash a password before storing it in a database."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Check a login password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str, minutes: int = 60):
    """Create a signed JWT that can be used for authenticated API requests."""
    expiry = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": subject, "exp": expiry}, SECRET_KEY, algorithm=ALGORITHM)
