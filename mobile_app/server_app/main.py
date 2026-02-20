from fastapi import FastAPI, Depends, Request, HTTPException, status, Cookie, Response, WebSocket, WebSocketDisconnect, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Annotated, Dict
from jose import JWTError, jwt
import os
from dotenv import load_dotenv 
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlmodel import Session, select
from contextlib import asynccontextmanager
from db import create_db_and_tables, get_session
from models import Users, Devices

templates = Jinja2Templates(directory="templates")

load_dotenv() # loading env variables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # Tworzymy tabele
    yield

app = FastAPI(lifespan=lifespan)

class EventData(BaseModel):
    event: str
    confidence: float


class DeviceEvent(BaseModel):
    device_id: str
    timestamp: datetime
    data: EventData

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
        "device": "1"
    },
     "kamil": {
        "username": "kamil",
        "password_hash": "$2b$12$W72NoajZlMaEKaVNcP6v8eb3PmOxwHdb6AHVPRuzh7H56pBeFcOki", # student123
        "device": "2"
    }
}
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str): #creating websocket
        await websocket.accept()
        self.active_connections[username] = websocket
    def disconnect(self, username: str):
        self.active_connections.pop(username)
    async def broadcast(self, message: DeviceEvent, username: str): #sending message to websocket that has logged in
            if username in self.active_connections:
                connection = self.active_connections[username]
                await connection.send_text(message.model_dump_json()) # sending string
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

manager = ConnectionManager()

#verifying if user gave correct password
def verify_password(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass, hashed_pass)

#creating token, in data we have login in field sub
def create_access_token(data: dict):
    to_encode = data.copy() 

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #date that our token expires

    to_encode.update({"exp": expire}) # adding this date to our token data, now we have fields "sub" and "exp"

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # generating our token
    return encoded_jwt  # returning token

def check_access_token(access_token : Annotated[str, Cookie()] = None, session: Session = Depends(get_session)):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    access_token = access_token.replace("Bearer ", "")
    try:
        tokenData = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = tokenData["sub"]
        query = select(Users).where(Users.username == username)
        user = session.exec(query).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    

#####################################################################################################################
#ENDPOINTS#
@app.get("/") # main page with login form
def main(request: Request):
    return templates.TemplateResponse(
        request= request,
        name="index.html"
    )

@app.post("/token") 
async def login( response: Response ,form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)): # in form_data we have login and password that client type in
    # user = users.get(form_data.username) # here we have data of our user, if exists
    query = select(Users).where(Users.username == form_data.username)
    user = session.exec(query).first()

    if not user or not verify_password(form_data.password, user.password_hash): # checking if user exitst and checking if password is correct
        raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Invalid login or password",
           headers={"WWW_Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username}) # if everything is correct we are creating token of user
    response = RedirectResponse(url="/users/me", status_code=status.HTTP_303_SEE_OTHER) #redirecting to users/me
    response.set_cookie( #sending our token to cookies
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True # that can't be reached by js
    )
    return response 



@app.websocket("/ws/{username}") # websocket that allows us to be connected in real-time with server
async def websocket_endpoint(websocket: WebSocket, username:str):
    await manager.connect( websocket, username) #creating websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(username)

@app.post("/trigger-alert") # endpoints that receives data from AI
async def trigger_alert(message: DeviceEvent, session: Session = Depends(get_session)):

    # searching for user that has assigned device that is sending message
    # for username, user_data in users.items():
    #     if user_data["device"] == message.device_id:
    #         await manager.broadcast(message,username)
    #         break

    query = select(Devices).where(Devices.id == message.device_id)
    device = session.exec(query).first()
    users = device.users
    for user in users:
        await manager.broadcast(message, user.username)
    return {"message": "Alert send"}

@app.post("/create_user")
async def create_user(username: str = Form(...), password: str = Form(...), device_id: str = Form(...), session: Session = Depends(get_session)):
    hashPass = pwd_context.hash(password)
    data = Users(username=username, password_hash=hashPass, device_id=device_id)
    device_temp = Devices(id = device_id)

    session.add(device_temp)
    session.commit()
    session.refresh(device_temp)
    session.add(data)
    session.commit()
    session.refresh(data)
    return data.username

@app.get("/users/me") # endpoint that receives alerts from AI in real-time
async def read_users_me(request: Request, token: Users = Depends(check_access_token)):
    return templates.TemplateResponse(
        request=request,
        name="user.html"
    )

@app.get("/me") # endpoint that returns username from token
async def getMe(token: Users = Depends(check_access_token)):
    print(token)
    return token.username

