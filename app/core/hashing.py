from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw: str): return pwd_context.hash(raw)
def verify_password(raw, hashed): return pwd_context.verify(raw, hashed)
def hash_pin(raw_pin): return pwd_context.hash(raw_pin)
def verify_pin(raw_pin, hashed_pin): return pwd_context.verify(raw_pin, hashed_pin)
