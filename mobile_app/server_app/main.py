from fastapi import FastAPI, Depends, Request, HTTPException, status, Cookie, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import JWTError, jwt
import os
from dotenv import load_dotenv 
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")

load_dotenv() # loading env variables

app = FastAPI()



#Configuration
SECRET_KEY = os.getenv("SECRET_KEY","Whatever") #string on which base we generate our token
ALGORITHM = os.getenv("ALGORITHM", "HS256") # algorithm which we are using to generate our token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30")) # time that our token is valid

#Hash Configuration (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # hashing and verifying password


#login endpoint is at .../token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # variable that contains our token

#users db
users = {
    "student": {
        "username": "student",
        "password_hash": "$2b$12$qtwy1y3k8S1fgUm9Zs9x9.b0gIwH95c7HJVnWRjjHY5FGGjvdcRlu", # student123
        "device": "H7x2m9Lp"
    },
     "kamil": {
        "username": "kamil",
        "password_hash": "$2b$12$W72NoajZlMaEKaVNcP6v8eb3PmOxwHdb6AHVPRuzh7H56pBeFcOki" # student123
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

def check_access_token(access_token : Annotated[str, Cookie()] = None):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    access_token = access_token.replace("Bearer ", "")
    #print (access_token)

    try:
        tokenData = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = tokenData["sub"]
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )

@app.post("/token")
async def login( response: Response ,form_data: OAuth2PasswordRequestForm = Depends()): # in form_data we have login and password that client type in
    user = users.get(form_data.username) # here we have data of our user, if exists


    if not user or not verify_password(form_data.password, user['password_hash']): # checking if user exitst and checking if password is correct
        raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Unvalid login or password",
           headers={"WWW_Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]}) # if everything is correct we are creating token of user
    response = RedirectResponse(url="/users/me", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True  # Ważne dla bezpieczeństwa
    )
    return response 

@app.get("/users/me")
async def read_users_me(token: str = Depends(check_access_token)):
    username : str = token
    
    return {"user": username, "message": "NICE!"}

class EventData(BaseModel):
    event: strDD
    confidence: float


class DeviceEvent(BaseModel):
    device_id: str
    timestamp: datetime
    data: EventData



@app.post("/api/device/event/{device_id}")
def receive_device_event(event: DeviceEvent, device_id: str, username: str = Depends(check_access_token)):
    user = users[username]
    if user["device"] != device_id:
       raise HTTPException(
           status_code= status.HTTP_401_UNAUTHORIZED
       )

    """
    Endpoint receiving data from Raspberry Pi
    """
    print("Received event:")
    print(event)

    return {
        "status": "ok",
        "message": "Event received successfully"
    }

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse(
        request= request,
        name="index.html"
    )