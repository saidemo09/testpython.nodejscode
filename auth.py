from datetime import timedelta, datetime
from typing import Annotated,List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from starlette import status
from models import User
import json
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.responses import JSONResponse

# from database import AzureTableStorage

import os
from dotenv import load_dotenv

load_dotenv()

# table_storage = AzureTableStorage("loginDetails")

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = os.getenv("AUTH_ALGORITHM")

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated=['auto'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    password: str
    access: List[str]
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

# AZURE setup for later
# def get_db():
#     users = table_storage.get_all_users()
#     return [{"email": user["email"], "password": user["password"], "role": user.get("role", "User")} for user in users]

# def save_db(data):
#     for user in data:
#         user_entity = {
#             "PartitionKey": "UserData",
#             "RowKey": user["email"],
#             "email": user["email"],
#             "password": user["password"],
#             "role": user.get("role", "User")
#         }
#         table_storage.save_user(user_entity)

def get_db():
    with open("db.json", "r+") as file:
        data = json.load(file)
    return data

def save_db(data):
    with open("db.json", "w") as file:
        json.dump(data, file, indent=4)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    create_user_model = User(
        username=create_user_request.username,
        password=bcrypt_context.hash(create_user_request.password),
        access=create_user_request.access,
        is_active=create_user_request.is_active
    )

    db = get_db()
    if any(u['username'] == create_user_model.username for u in db):
        return JSONResponse(                
                status_code=500,
                content={
                    "message": "Username already registered",
                    "status_code": "500"
                }
            )
    db.append(create_user_model.dict())
    save_db(db)
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:       
        return JSONResponse(                
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "message": "Could not validate user",
                    "headers":{"WWW-Authenticate": "bearer"},
                    "status_code": "401"
                }
            )
    token = create_access_token(user['username'], timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(username, password:str, db):
    user = next((u for u in db if u['username'] == username), None)
    if user is None or not bcrypt_context.verify(password, user['password']):
        return False
            
    return user

def create_access_token(username, expires_delta:timedelta):
    encode = {'sub':username} 
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:  
            return JSONResponse(                
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "message": "Could not validate user",
                    "status_code": "401"
                }
            )
        db = get_db()
        user = next((u for u in db if u['username'] == username), None)
        if user is None:
            return JSONResponse(                
                status_code=401,
                content={
                    "message": "User not found",
                    "status_code": "401"
                }
            )
        return {'username': username, 'access': user.get('access')}

    except JWTError:       
        return JSONResponse(                
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "message": "Could not validate user",
                    "status_code": "401"
                }
        )