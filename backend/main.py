from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, parents, admin, campers

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Camp Management System API", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Durante desarrollo es más seguro usar "*" si hay líos de puertos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Routers
# Nota: Ya tienen el prefix /api, por lo que auth.router (que es /auth) será /api/auth
app.include_router(auth.router, prefix="/api")
app.include_router(parents.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(campers.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Camp Management System API", "version": "1.0.0"}

# --- NUEVOS ENDPOINTS PARA EVITAR EL 404 ---

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