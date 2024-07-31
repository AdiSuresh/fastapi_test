from datetime import timedelta
from typing import Annotated, List, Optional
from fastapi import Depends, FastAPI, HTTPException
import pytz
from auth import auth
from core.security import verify_password
from core.settings import settings
from crud.user import get_user_by_username
import crud.user as user
from crud.token import delete_user_tokens, get_token, store_token
from database import SessionLocal, init_db
from models.token import Token
from schemas.user import DeleteRequest, LoginRequest, LogoutRequest, UserCreate, UserResponse, UserUpdate
from sqlalchemy.orm import Session
from utils import dt


app = FastAPI()
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get('/')
def root():
    return {'message': 'Server is active'}

@app.get('/echo/')
def echo(value: Optional[str]):
    return {'message': value}

@app.get('/profile/')
def get_profile():
    return {'message': 'value'}

@app.post("/users/", response_model=UserResponse)
def create_user(request: UserCreate, db: db_dependency):
    db_user = get_user_by_username(db, username=request.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            message="User is already registered"
        )
    db_user = user.create_user(db, request)
    return db_user

@app.post("/login/")
def login(request: LoginRequest, db: db_dependency):
    db_user = get_user_by_username(db, username=request.username)
    if db_user is None or not verify_password(request.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    delete_user_tokens(db, user_id=db_user.id)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expires_in = auth.create_access_token(
        data={"sub": request.username}, expires_delta=access_token_expires
    )
    store_token(db, access_token, db_user.id, expires_in)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expiry": expires_in,
    }

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: db_dependency):
    db_user = user.get_user_by_id(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=400, message="User not found")
    access_token = get_token(db, access_token=user_update.access_token)
    if access_token is None or access_token.hasExpired():
        raise HTTPException(status_code=400, message="Invalid token")
    updated_user = user.update_user(db, user_id=user_id, user_update=user_update)
    return updated_user

@app.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    token = get_token(db, request.access_token)
    if token is None or token.hasExpired():
        raise HTTPException(status_code=400, detail="Invalid token")
    delete_user_tokens(db, request.user_id)
    return {"message": "Logout successful"}

@app.post("/delete")
def delete_user(request: DeleteRequest, db: Session = Depends(get_db)):
    token = get_token(db, request.access_token)
    if token is None or token.hasExpired():
        raise HTTPException(status_code=400, detail="Invalid token")
    delete_user_tokens(db, request.user_id)
    db_user = user.delete_user(db, request.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, message="User not found")
    return {"message": "Deleted successfully"}

@app.get('/users/', response_model=List[UserResponse])
def get_users(db=Depends(get_db)):
    print('fetching users...')
    users = user.get_users(db)
    return users
