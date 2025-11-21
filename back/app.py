# back/app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from back.routers import characters, scenarios, creation, gamesession, user
from fastapi.openapi.utils import get_openapi
from back.utils.exceptions import InternalServerError
import logfire

app = FastAPI(title="JdR – Terres du Milieu")

def scrubbing_callback(m: logfire.ScrubMatch):
    return m.value

logfire.configure(scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback))
logfire.instrument_fastapi(app)
logfire.instrument_pydantic_ai()

@app.exception_handler(InternalServerError)
async def internal_server_error_handler(request: Request, exc: InternalServerError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

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
app.include_router(gamesession.router, prefix="/api/gamesession")
app.include_router(user.router)

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
