from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from sqlmodel import Session, select
from app.database import get_db
from app.models import User
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class UserSignInRequest(BaseModel):
    email: str
    password: str

@router.post("/signin")
def signin(request: UserSignInRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(request.password)
    
    # Create new user
    new_user = User(
        email=request.email,
        password=hashed_password,
        created_at=datetime.now(timezone.utc)  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": new_user.id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Login endpoint (authenticate existing user and return access token)
@router.post("/login")
def login(request: UserSignInRequest, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.email == request.email)).first()
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}