from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import JWTError, jwt
import os
from dotenv import load_dotenv 

load_dotenv() # loading env variables

app = FastAPI()

#Configuration
SECRET_KEY = os.getenv("SECRET_KEY") #string on which base we generate our token
ALGORITHM = os.getenv("ALGORITHM") # algorithm which we are using to generate our token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) # time that our token is valid

#Hash Configuration (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # hashing and verifying password


#login endpoint is at .../token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # variable that contains our token

#users db
users = {
    "student": {
        "username": "student",
        "password_hash": "$2b$12$qtwy1y3k8S1fgUm9Zs9x9.b0gIwH95c7HJVnWRjjHY5FGGjvdcRlu" # student123
    }
}
#verifying if user gave correct password
def verify_password(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass, hashed_pass)

#creating token, in data we have login in field sub
def create_access_token(data: dict):
    to_encode = data.copy() 

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #date that our token expires

    to_encode.update({"exp": expire}) # adding this date to our token data, now we have fields "sub" and "exp"

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # generating our token
    return encoded_jwt 

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()): # in form_data we have login and password that client type in
    user = users.get(form_data.username) # here we have data of our user, if exists


    if not user or not verify_password(form_data.password, user['password_hash']): # checking if user exitst and checking if password is correct
        raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Unvalid login or password",
           headers={"WWW_Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]}) # if everything is correct we are creating token of user
    return {"access_token": access_token, "token_type": "bearer"} # and give it to oauth2_scheme

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # we decode our token

        username: str = payload.get("sub") # now we have dict with sub and exp so we can get our username

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user": username, "message": "NICE!"}

class EventData(BaseModel):
    event: str
    confidence: float


class DeviceEvent(BaseModel):
    device_id: str
    timestamp: datetime
    data: EventData



@app.post("/api/device/event")
def receive_device_event(event: DeviceEvent):
    """
    Endpoint receiving data from Raspberry Pi
    """
    print("Received event:")
    print(event)

    return {
        "status": "ok",
        "message": "Event received successfully"
    }