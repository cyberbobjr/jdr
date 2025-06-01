# back/app.py
from fastapi import FastAPI, Body
from .routers import characters, inventory, combat, scenarios
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

@app.post("/api/agent/respond")
async def agent_respond(session_id: UUID, body: dict = Body(...)):
    """
    ### agent_respond
    **Description:** Reçoit un message utilisateur, charge l'agent MJ et l'historique, exécute le LLM, sauvegarde la mémoire et retourne la réponse.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu.
    - `message` (str) : Message du joueur (dans le body JSON).
    - `character_id` (str, optionnel) : Identifiant du personnage (pour enrichir le prompt).
    - `scenario_name` (str, optionnel) : Nom du scénario (pour enrichir le prompt).
    **Retour :** Réponse générée par le LLM (str).
    """
    message = body.get("message")
    character_id = body.get("character_id")
    scenario_name = body.get("scenario_name")
    if not message:
        return {"error": "Le champ 'message' est requis dans le body JSON."}
    character_json = ""
    if character_id:
        try:
            character = CharacterService.get_character(character_id)
            character_json = character.json(ensure_ascii=False)
        except Exception:
            character_json = ""
    # 1. Charger l'agent et la mémoire de la session
    agent = build_gm_agent(str(session_id), scenario_name)
    store = agent._store
    messages = store.load()
    # 2. Ajouter le message utilisateur enrichi
    if character_json:
        enriched_message = enrich_user_message_with_character(message, character_json)
        messages.append(ChatMessage.from_user(enriched_message))
    else:
        messages.append(ChatMessage.from_user(message))
    # 3. Appeler l'agent Haystack (run est synchrone)
    result = agent.run(messages=messages)
    # 4. Sauvegarder l'historique (incluant la réponse du LLM)
    store.save(result["messages"])
    # 5. Retourner la dernière réponse générée
    log_debug("Appel à l'agent LLM", action="agent_respond", session_id=str(session_id), character_id=character_id, scenario_name=scenario_name, message=message)
    return {"response": result["messages"][-1].text}

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
