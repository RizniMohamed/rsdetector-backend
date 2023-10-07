from fastapi import FastAPI, Header, HTTPException,UploadFile,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from model import detection
import numpy as np
from jose import jwt
from jwt import SECRET_KEY,ALGORITHM,create_new_token
from database import store_image_metadata,update_processing_time
import datetime
from logger import log_error
from PIL import Image
import io

app = FastAPI() 

origins = [
    "http://localhost:3000",  # React 
    "http://127.0.0.1:3000",  # React
    "https://rsdetector.netlify.app", # netlify 
    "https://1c65-112-134-198-70.ngrok-free.app"
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
    img = Image.open(io.BytesIO(contents)).convert('RGB')
    
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
        img = Image.open(io.BytesIO(contents)).convert('RGB')

        
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
