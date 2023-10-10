from fastapi import FastAPI, Header, HTTPException,UploadFile,BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from model import detection
import cv2
import numpy as np
from jose import jwt
from jwt import SECRET_KEY,ALGORITHM,create_new_token,create_access_token
from database import store_image_metadata,update_processing_time, store_user,get_user
import datetime
from logger import log_error
from models import BaseModel,Token,TokenData,User,UserIn
from auth import authenticate_user

app = FastAPI() 

origins = [
    "http://localhost:3000",  # React 
    "http://127.0.0.1:3000",  # React
    "https://rsdetector.ngrok.app"
] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/V1/process") 
async def process(file: UploadFile,background_tasks: BackgroundTasks):
    file_size = file.size  # This gets the size of the file in bytes
    file.file.seek(0)
    
    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    upload_timestamp = datetime.datetime.utcnow()
    file_type = file.content_type

    image_id = store_image_metadata(upload_timestamp, None, file_size, file_type)

    start_time = datetime.datetime.now()

    result = detection(img,image_id)
    
    end_time = datetime.datetime.now()
    processing_time = end_time - start_time
    
    def update_db():
        update_processing_time(image_id, processing_time)
    background_tasks.add_task(update_db)

    
    if result:
        response = {"message": "{}".format(result)}
    else: 
        response = {"message": "No sign detected"}
    return response

@app.get("/V1/token")
async def get_new_token():
    token = create_new_token()
    return {"access_token": token, "token_type": "bearer"}

@app.post("/V1/secure-process")
async def get_secure_data(file: UploadFile, background_tasks: BackgroundTasks, authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=403, detail="Not authenticated")
        token = authorization.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")


        file_size = file.size  # This gets the size of the file in bytes
        file.file.seek(0)
        
        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        upload_timestamp = datetime.datetime.utcnow()
        file_type = file.content_type

        image_id = store_image_metadata(upload_timestamp, None, file_size, file_type)

        start_time = datetime.datetime.now()

        result = detection(img,image_id)
        
        end_time = datetime.datetime.now()
        processing_time = end_time - start_time
        
        def update_db():
            update_processing_time(image_id, processing_time)
        background_tasks.add_task(update_db)

        
        if result:
            response = {"message": "{}".format(result)}
        else: 
            response = {"message": "No sign detected"}
        return response

    except Exception as e:
        if hasattr(e,'detail'):
            error_message = f"Unexpected error: {str(e.detail)}"
        else:
            error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        raise HTTPException(status_code=500, detail=error_message)  # Internal Server Error

@app.post("/V1/register")
async def register_user(user: User):
    try:
        res = store_user(user.password,user.email)
        if res == 0:
            return {"status":0, "message": "User created successfully"}
        elif res == 1:
            return {"status":1,"message": "Email already in use"}
        elif res == 2:
            return {"status":2,"message": "Unable to create the user, contact rsdetector team"}
    except Exception as e :
        log_error("Unable to create user")
        print(e)
        raise HTTPException(status_code=500, detail="Unable to create user")  # Internal Server Error

@app.post("/V1/login")
async def login_for_access_token(form_data: UserIn):
    user = authenticate_user( form_data.email, form_data.password)
    if not user:
        return {"status": 1 , "message": "Username or Password mismtach"}
    access_token_expires = datetime.timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user[2]}, expires_delta=access_token_expires
    )
    return {"status": 0,"message": "Login success" ,"access_token": access_token, "token_type": "bearer"}