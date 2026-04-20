from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, parents, admin, campers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Camp Management System API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(parents.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(campers.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Camp Management System API", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    """Endpoint que busca el frontend para verificar estado"""
    return {"status": "healthy"}

@app.get("/api/metrics")
def get_metrics():
    # He añadido 'total_users' y 'campers' por si el JS busca esos nombres
    return {
        "status": "online",
        "total_users": 0,
        "total_campers": 0,
        "active_sessions": 0,
        "metrics": [] 
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)