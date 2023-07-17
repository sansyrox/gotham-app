from sqlalchemy.orm import Session
from .models import User, Crime


def get_crime(db: Session, crime_id: int):
    return db.query(Crime).filter(Crime.id == crime_id).first()

def get_crimes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Crime).offset(skip).limit(limit).all()

def create_crime(db: Session, crime):
    db_crime = Crime(**crime)
    db.add(db_crime)
    db.commit()
    db.refresh(db_crime)
    return db_crime

def update_crime(db: Session, crime_id: int, crime):
    db_crime = get_crime(db, crime_id)
    if db_crime is None:
        return None
    for key, value in crime.items():
        setattr(db_crime, key, value)
    db.commit()
    db.refresh(db_crime)
    return db_crime

def delete_crime(db: Session, crime_id: int):
    db_crime = get_crime(db, crime_id)
    if db_crime is None:
        return False
    db.delete(db_crime)
    db.commit()
    return True


from sqlalchemy.orm import Session
from .models import User

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: User):
    hashed_password = get_password_hash(user["password"])
    db_user = User(username=user["username"], hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

from passlib.context import CryptContext
from jose import JWTError, jwt

from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

ALGORITHM = "HS256"
SECRET_KEY = "your_secret_key"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    created_token = create_access_token(data={"sub": user.username})
    return created_token

