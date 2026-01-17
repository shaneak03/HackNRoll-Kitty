from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

origins = [
    "http://localhost:3000",  # frontend
    "http://127.0.0.1:3000",  # sometimes needed
    "*",  # allow all origins (optional, not recommended for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # or ["*"] for all methods
    allow_headers=["*"],
)

@app.get("/video")
def get_video():
    filename = "kitty_explains.mp4"
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Video not found at {path}")
    return FileResponse(path, media_type="video/mp4", filename=filename)