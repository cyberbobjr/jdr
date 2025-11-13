# back/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from back.routers import characters, scenarios, creation
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="JdR – Terres du Milieu")

# CORS configuration (kept for potential future frontend/dev tools)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],  # Common dev ports
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Routers REST
app.include_router(characters.router, prefix="/api/characters")
app.include_router(scenarios.router,  prefix="/api/scenarios")
app.include_router(creation.router,   prefix="/api/creation")

# Ajout de la documentation Swagger personnalisée
@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="JdR – Terres du Milieu",
        version="1.0.0",
        description="API pour le jeu de rôle orchestré par un LLM.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
