from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.api.routes import router as api_router

app = FastAPI(
    title="InvisiGuard API",
    description="Invisible Watermarking & Geometric Correction API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for processed images
os.makedirs("static/processed", exist_ok=True)
os.makedirs("static/debug", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "InvisiGuard API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
