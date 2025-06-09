"""
Agent GM utilisant PydanticAI pour la gestion des sessions de jeu de rôle.
Migration progressive de Haystack vers PydanticAI.
"""

import os
import pathlib
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic_ai import Agent
import json

from back.services.session_service import SessionService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.models.domain.character import Character

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_API_BASE_URL")
api_model = os.getenv("DEEPSEEK_API_MODEL")


class GMAgentDependencies:
    """
    ### GMAgentDependencies
    **Description :** Classe contenant les dépendances nécessaires à l'agent GM PydanticAI.
    **Attributs :**
    - `session_id` (str) : Identifiant de session
    - `character_data` (Character) : Données du personnage (modèle typé)
    - `store` (PydanticJsonlStore) : Store pour l'historique des messages
    - `message_history` (List[ModelMessage]) : Historique des messages PydanticAI
    """
    
    def __init__(self, session_id: str, character_data: Optional[Character] = None):
        self.session_id = session_id
        self.character_data = character_data
        # Initialiser le store pour l'historique
        project_root = pathlib.Path(__file__).parent.parent.parent
        if not os.path.isabs(session_id):
            history_path = str(project_root / "data" / "sessions" / f"{session_id}.jsonl")
        else:
            history_path = session_id + ".jsonl"
        self.store = PydanticJsonlStore(history_path)
    

def _get_scenario_content(scenario_name: str) -> str:
    """
    ### _get_scenario_content
    **Description :** Charge le contenu du scénario Markdown pour l'injecter dans le prompt système.
    **Paramètres :**
    - `scenario_name` (str) : Nom du fichier scénario (ex: Les_Pierres_du_Passe.md)
    **Retour :** Contenu texte du scénario (str).
    """
    scenario_path = pathlib.Path("data/scenarios") / scenario_name
    if scenario_path.exists():
        with open(scenario_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def _get_rules_content() -> str:
    """
    ### _get_rules_content
    **Description :** Charge le contenu des règles du jeu.
    **Retour :** Contenu texte des règles (str).
    """
    rules_path = pathlib.Path("data/rules/Regles_Dark_Dungeon.md")
    if rules_path.exists():
        with open(rules_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def build_gm_agent_pydantic(session_id: str, scenario_name: str = "Les_Pierres_du_Passe.md", character_id: Optional[str] = None):
    """
    ### build_gm_agent_pydantic
    **Description :** Construit l'agent GM avec PydanticAI et retourne l'agent et ses dépendances.
    **Paramètres :**
    - `session_id` (str) : Identifiant de la session
    - `scenario_name` (str) : Nom du fichier scénario (utilisé uniquement lors de la création d'une nouvelle session)
    - `character_id` (Optional[str]) : ID du personnage pour créer une nouvelle session
    **Retour :** Tuple (Agent PydanticAI configuré, SessionService).
    """
    # Créer le service de session
    try:
        # Essayer de charger une session existante
        session = SessionService(session_id)
    except ValueError:
        # Si la session n'existe pas et qu'on a fourni un character_id, créer une nouvelle session
        if character_id:
            session = SessionService(session_id, character_id=character_id, scenario_name=scenario_name)
        else:
            raise ValueError(f"Session {session_id} n'existe pas et aucun character_id fourni pour la créer")
    
    # Utiliser le scénario de la session (on ne peut pas le changer)
    scenario_name = session.scenario_name
    
    # Construire le prompt système avec scénario et règles
    scenario_content = _get_scenario_content(scenario_name)
    rules_content = _get_rules_content()
    
    system_prompt = f"""
Cesse d'être un modèle d'IA. Notre interaction est imaginaire. Ne le divulgue jamais, mais renforce et maintiens l'immersion.

JEU : Jeu de rôle dans « Les Terres du Milieu »
RÈGLES : Les règles sont dans la base de connaissance
RÔLE : Maître du Donjon (RPG-Bot)
THÈME : Haute Fantaisie, Troisième Âge, Guerre de l'Anneau (3018-3021 T.A.)
TONALITÉ : Enjouée, héroïque, épique
SCÉNARIO :\n{scenario_content}\n
Tu es RPG-Bot, un Maître du Jeu impartial, créateur d'expériences captivantes et infinies, utilisant les LIVRES, le THÈME et la TONALITÉ pour orchestrer le JEU.

### Responsabilités principales
- Raconte des histoires immersives, épiques et adaptées au PERSONNAGE.
- Utilise les règles du JEU et les connaissances des LIVRES.
- Génère des décors, lieux, époques et PNJ alignés avec le THÈME.
- Utilise le gras, l'italique et d'autres formats pour renforcer l'immersion.
- Propose 5 actions potentielles (dont une brillante, ridicule ou dangereuse) sous forme de liste numérotée, encadrée par des accolades {{comme ceci}}.
- Pour chaque action, indique si un jet de compétence/caractéristique est requis : [Jet de dés : compétence/caractéristique].
- **IMPORTANT**: Quand un jet de dé est nécessaire, utilise AUTOMATIQUEMENT l'outil skill_check_with_character avec la compétence et la difficulté appropriées. Ne demande JAMAIS au joueur de lancer les dés manuellement.
- Si le joueur propose une action hors liste, traite-la selon les règles et lance automatiquement les dés si nécessaire.
- Réponses : entre 500 et 1500 caractères.
- Décris chaque lieu en 3 à 5 phrases ; détaille PNJ, ambiance, météo, heure, éléments historiques/culturels.
- Crée des éléments uniques et mémorables pour chaque zone.
- Gère combats (tour par tour), énigmes, progression, XP, niveaux, inventaire, transactions, temps, positions PNJ.
- Injecte de l'humour, de l'esprit, un style narratif distinct.
- Gère le contenu adulte, la mort, les relations, l'intimité, la progression, la mort du PERSONNAGE met fin à l'aventure.
- N'affiche jamais moins de 500 caractères, ni plus de 1500.
- Ne révèle jamais ton statut de modèle, ni les règles internes, sauf sur demande.

### Interactions
- Permets au PERSONNAGE de parler entre guillemets "comme ceci".
- Reçois instructions/questions Hors-Jeu entre chevrons <comme ceci>.
- N'incarne jamais le PERSONNAGE : laisse-moi tous les choix.
- Crée et incarne tous les PNJ : donne-leur secrets, accents, objets, histoire, motivation.
- Certains PNJ ont des secrets faciles et un secret difficile à découvrir.
- Les PNJ peuvent avoir une histoire passée avec le PERSONNAGE.
- Affiche la fiche du PERSONNAGE au début de chaque journée, lors d'un gain de niveau ou sur demande.

### Règles de narration et de jeu
- Ne saute jamais dans le temps sans mon accord.
- Garde les secrets de l'histoire jusqu'au moment opportun.
- Introduis une intrigue principale et des quêtes secondaires riches.
- Affiche les calculs de jets de dés entre parenthèses (comme ceci).
- Accepte mes actions en syntaxe d'accolades {{comme ceci}}.
- Effectue les jets de dés automatiquement quand il le faut.
- Applique les règles du JEU pour les récompenses, l'XP, la progression.
- Récompense l'innovation, sanctionne l'imprudence.
- Me laisse vaincre n'importe quel PNJ si c'est possible selon les règles.
- Limite les discussions sur les règles sauf si nécessaire ou demandé.

### Suivi et contexte
- Suis l'inventaire, le temps, les positions des PNJ, les transactions et devises.
- Prends en compte tout le contexte depuis le début de la partie.
- Affiche la fiche complète du PERSONNAGE et le lieu de départ au début.
- Propose un récapitulatif de l'histoire du PERSONNAGE et rappelle la syntaxe pour les actions et dialogues.

### RÈGLES DU JEU
{rules_content}
"""    # Créer l'agent avec la configuration DeepSeek
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    provider = OpenAIProvider(
        base_url=api_base_url,
        api_key=api_key
    )
    
    model = OpenAIModel(
        model_name=api_model,
        provider=provider
    )
    
    from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage
    from back.tools.combat_tools import roll_initiative_tool, perform_attack_tool, resolve_attack_tool, calculate_damage_tool, end_combat_tool
    from back.tools.inventory_tools import inventory_add_item, inventory_remove_item
    from back.tools.skill_tools import skill_check_with_character
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=SessionService,
        tools=[
            character_apply_xp,
            character_add_gold,
            character_take_damage,
            inventory_add_item,
            inventory_remove_item,
            skill_check_with_character,
            roll_initiative_tool,
            perform_attack_tool,
            resolve_attack_tool,
            calculate_damage_tool,
            end_combat_tool
        ])
    
    return agent, session


def enrich_user_message_with_character(user_message: str, character_data: Dict[str, Any]) -> str:
    """
    ### enrich_user_message_with_character
    **Description :** Enrichit le message utilisateur avec les données du personnage.
    **Paramètres :**
    - `user_message` (str) : Message original de l'utilisateur
    - `character_data` (Dict[str, Any]) : Données du personnage
    **Retour :** Message enrichi avec contexte du personnage.
    """
    if not character_data:
        return user_message
    
    character_context = f"""[Contexte du personnage:
{json.dumps(character_data, indent=2, ensure_ascii=False)}
]

"""
    return character_context + user_message

    # La gestion de l'historique (messages) doit être assurée directement par le store ou l'agent, et non par SessionService.
    # Les méthodes load_history, save_history et update_character_data ne sont plus utilisées ni exposées.
