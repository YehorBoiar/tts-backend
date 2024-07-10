from pydantic import BaseModel

class TextResponseModel(BaseModel):
    text: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    role: str 

class UserInDB(User):
    hashed_password: str