import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.datasets import router as datasets_router
from app.api.query import router as query_router

app = FastAPI(
    title="Data Intelligence Workspace API",
    version="0.1.0",
)

configured_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "",
)

allowed_origins = [
    origin.strip()
    for origin in configured_origins.split(",")
    if origin.strip()
]

allowed_origins.extend(
    [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://data-intelligence-workspace-6mhs.vercel.app",
    ]
)

allowed_origins = list(dict.fromkeys(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets_router)
app.include_router(query_router)


@app.get("/health")
@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "data-intelligence-workspace",
    }