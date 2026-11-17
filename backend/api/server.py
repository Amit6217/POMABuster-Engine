"""
FastAPI Server Setup for POMABuster Backend & Dashboard UI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.api.routes import router

app = FastAPI(
    title="POMABuster Detection Engine",
    description="Full-Stack Detection Engine & Dashboard for 'POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance' (IEEE S&P 2024)",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Mount Frontend Production Build if present
dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
assets_path = os.path.join(dist_path, "assets")

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

@app.get("/{full_path:path}")
def serve_spa_or_root(full_path: str = ""):
    # If API call, fall through
    if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        return {"error": "Not found"}
    index_html = os.path.join(dist_path, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {
        "message": "POMABuster Detection Engine API is running.",
        "documentation": "/docs",
        "health": "/api/health"
    }
