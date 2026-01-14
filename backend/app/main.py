from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

# Imports relatifs (ajoutez un point devant)
from .database import Base, engine, get_db
from .views import router as views_router
from .urls import router as api_router
from . import models  # ou import .models

# Crée toutes les tables dans la base de données
Base.metadata.create_all(bind=engine)

# Initialiser l'application FastAPI
app = FastAPI()

# Configurer les modèles
templates = Jinja2Templates(directory="app/templates")

# Inclure les routeurs
app.include_router(views_router)
app.include_router(api_router, prefix="/api")

# Monte le dossier static pour servir CSS, JS, images
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})