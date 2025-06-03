# back/app.py
from fastapi import FastAPI, Body
from routers import characters, inventory, combat, scenarios
from back.agents.gm_agent import build_gm_agent, JsonlChatMessageStore, enrich_user_message_with_character
from haystack.dataclasses import ChatMessage
from uuid import UUID
from fastapi.openapi.utils import get_openapi
from back.services.character_service import CharacterService
from back.utils.logger import log_debug

app = FastAPI(title="JdR – Terres du Milieu")

# Routers REST
app.include_router(characters.router, prefix="/api/characters")
app.include_router(inventory.router,  prefix="/api/inventory")
app.include_router(combat.router,     prefix="/api/combat")
app.include_router(scenarios.router,  prefix="/api/scenarios")

# Agent LangChain
gm_agent = build_gm_agent()

# Old route removed - use /api/scenarios/play instead
# The new route automatically retrieves character and scenario info from session_id

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
