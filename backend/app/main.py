
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analyze import router as analyze_router

app = FastAPI(
    title="ScamShield API",
    description="Scam message classification and suspicious URL analysis.",
    version="1.0.0",
)

# Development configuration. Restrict origins before public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "ScamShield API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(analyze_router)
