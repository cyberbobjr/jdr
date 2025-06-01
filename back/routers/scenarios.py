from fastapi import APIRouter, HTTPException
from back.services.scenario_service import ScenarioService
from back.models.schema import ScenarioList
from pydantic import BaseModel
from back.services.skill_service import perform_skill_check
from back.utils.logger import log_debug

router = APIRouter()

@router.get("/", response_model=ScenarioList)
async def list_scenarios():
    """
    ### list_scenarios
    **Description:** Endpoint pour lister les scénarios disponibles et en cours.
    **Parameters:** Aucun.
    **Returns:** `ScenarioList` contenant une liste de scénarios avec leurs états.
    """
    log_debug("Appel endpoint scenarios/list_scenarios")
    scenarios = ScenarioService.list_scenarios()
    return ScenarioList(scenarios=scenarios)

@router.get("/{scenario_file}")
async def get_scenario_details(scenario_file: str):
    """
    ### get_scenario_details
    **Description:** Récupère le contenu d'un scénario (fichier Markdown) à partir de son nom de fichier.
    **Parameters:**
    - `scenario_file` (str): Le nom du fichier du scénario (ex: Les_Pierres_du_Passe.md).
    **Returns:** Le contenu du fichier Markdown du scénario, ou une erreur 404 si le fichier n'existe pas.
    """
    log_debug("Appel endpoint scenarios/get_scenario_details", scenario_file=scenario_file)
    try:
        return ScenarioService.get_scenario_details(scenario_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Scénario '{scenario_file}' introuvable.")

class StartScenarioRequest(BaseModel):
    scenario_name: str
    character_id: str

@router.post("/start")
async def start_scenario(request: StartScenarioRequest):
    """
    ### start_scenario
    **Description:** Démarre un scénario avec un personnage spécifique et retourne l'id de session.
    **Parameters:**
    - `request` (StartScenarioRequest): Contient le nom du scénario et l'identifiant du personnage.
    **Returns:** Un objet JSON avec session_id, scenario_name, character_id et message.
    """
    log_debug("Appel endpoint scenarios/start_scenario")
    return ScenarioService.start_scenario(request.scenario_name, request.character_id)

class SkillCheckRequest(BaseModel):
    skill_level: int
    difficulty: int

@router.post("/skill-check")
async def skill_check_endpoint(request: SkillCheckRequest):
    """
    Endpoint pour effectuer un test de compétence.

    Parameters:
    - request (SkillCheckRequest): Contient le niveau de compétence et la difficulté.

    Returns:
    - dict: Résultat du test de compétence (réussi ou échoué).
    """
    log_debug("Appel endpoint scenarios/skill_check_endpoint")
    result = perform_skill_check(skill_level=request.skill_level, difficulty=request.difficulty)
    return {"success": result}
