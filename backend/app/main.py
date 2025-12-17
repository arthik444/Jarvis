# FastAPI entry point - no business logic yet
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mini Jarvis API",
    description="Low-latency voice assistant backend",
    version="0.1.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Mini Jarvis API - Backend placeholder"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
