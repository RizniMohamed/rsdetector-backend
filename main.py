from fastapi import FastAPI,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from model import detection
import cv2
import numpy as np


app = FastAPI()

origins = [
    "http://localhost:3000",  # React
    "http://127.0.0.1:3000",  # React
    "https://rsdetector.netlify.app/", # netlify
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
    return {"status": True  if result else False}

