"""
Point d'entrée principal de l'application FastAPI pour les Mystères de l'UNIL 2025.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Mystères de l'UNIL 2025 - Déjouez l'IA",
    description="Plateforme interactive d'expérimentation avec l'intelligence artificielle",
    version="0.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")

# Point de santé
@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'application."""
    return {"status": "healthy"}

# Importation des routes
# TODO: Ajouter les routes au fur et à mesure de leur création
# from src.backend.api import router as api_router
# app.include_router(api_router, prefix="/api/v1") 