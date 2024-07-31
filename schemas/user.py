from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UseApi(BaseModel):
    access_token: str

class UserUpdate(UseApi):
    name: str
    email: EmailStr

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LogoutRequest(UseApi):
    user_id: int

class DeleteRequest(LogoutRequest):
    pass