from fastapi import FastAPI, Header, HTTPException,UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from model import detection
import cv2
import numpy as np
from jose import jwt
from jwt import SECRET_KEY,ALGORITHM,create_new_token

app = FastAPI() 

origins = [
    "http://localhost:3000",  # React 
    "http://127.0.0.1:3000",  # React
    "https://rsdetector.netlify.app", # netlify 
    "https://ab05-112-134-197-76.ngrok-free.app"
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
async def process(file: UploadFile):
    
    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = detection(img)
    if result:
        response = {"message": "{}".format(result)}
    else: 
        response = {"message": "No sign detected"}
    return response


@app.get("/V1/token")
async def get_new_token():
    token = create_new_token()
    return {"access_token": token, "token_type": "bearer"}

@app.post("/V1/secure-data")
async def get_secure_data(file: UploadFile, authorization: str = Header(None)):
    
    if not authorization:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")



    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = detection(img)
    if result:
        response = {"message": "{}".format(result)}
    else: 
        response = {"message": "No sign detected"}
    return response