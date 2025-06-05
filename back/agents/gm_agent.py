from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from dotenv import load_dotenv
from haystack.utils import Secret
from back.utils.logger import log_debug
from back.tools.character_tools import character_apply_xp_tool, character_add_gold_tool, character_take_damage_tool
from back.tools.skill_tools import skill_check_tool
from back.tools.combat_tools import roll_initiative, perform_attack, resolve_attack, calculate_damage, end_combat
from back.tools.inventory_tools import inventory_add_item_tool, inventory_remove_item_tool
from back.storage.jsonl_chat_store import JsonlChatMessageStore
from back.utils.logging_tool import wrap_tools_with_logging
import os
import pathlib

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_API_BASE_URL")
api_model = os.getenv("DEEPSEEK_API_MODEL")


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
        return scenario_path.read_text(encoding="utf-8")
    return ""

SYSTEM_PROMPT_TEMPLATE = '''
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
'''

def build_gm_agent(session_id: str = "default", scenario_name: str = None) -> Agent: 
    """
    ### build_gm_agent
    **Description :** Construit un agent Haystack avec persistance mémoire JSONL pour la session (via JsonlChatMessageStore), et injecte le prompt système enrichi avec le scénario. Le personnage JSON doit être ajouté à chaque message utilisateur pour le cache prompting.
    **Paramètres :**
    - `session_id` (str) : Identifiant unique de la session (utilisé pour le fichier d'historique).
    - `scenario_name` (str) : Nom du fichier scénario (pour injection dans le prompt système).
    **Retour :** Agent Haystack configuré avec mémoire persistante custom et prompt système enrichi.
    """    
    # Chemin corrigé : utilisation de pathlib pour pointer vers la racine du projet
    project_root = pathlib.Path(__file__).parent.parent.parent
    log_debug("Résolution du chemin projet", action="resolve_project_root", project_root=os.path.abspath(project_root))
    if not os.path.isabs(session_id):
        history_path = str(project_root / "data" / "sessions" / f"{session_id}.jsonl")
    else:
        history_path = session_id + ".jsonl"
    store = JsonlChatMessageStore(history_path)
    messages = store.load()
    generator = OpenAIChatGenerator(api_key=Secret.from_token(api_key), api_base_url=api_base_url, model=api_model, generation_kwargs={"temperature": 0.2})
      # Outils de jeu disponibles pour l'agent MJ
    base_tools = [
        # Outils de personnage
        character_apply_xp_tool,
        character_add_gold_tool,
        character_take_damage_tool,
        # Outils de compétences
        skill_check_tool,
        # Outils de combat
        roll_initiative,
        perform_attack,
        resolve_attack,
        calculate_damage,
        end_combat,
        # Outils d'inventaire
        inventory_add_item_tool,
        inventory_remove_item_tool
    ]
    
    # Envelopper les outils avec le système de logging
    tools = wrap_tools_with_logging(base_tools, store=store)
    
    scenario_content = _get_scenario_content(scenario_name) if scenario_name else ""
    rules_content = _get_rules_content()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(scenario_content=scenario_content, rules_content=rules_content)
    
    # Créer l'agent sans callback_manager (non compatible Haystack 3.x)
    agent = Agent(
        tools=tools,
        chat_generator=generator,
        system_prompt=system_prompt
    )
    agent._chat_history = messages  # Stockage custom de l'historique
    agent._store = store
      # Configurer la référence agent dans tous les outils logging
    for tool in tools:
        if hasattr(tool, 'set_agent'):
            tool.set_agent(agent)
    
    return agent


def enrich_user_message_with_character(message: str, character_json: str) -> str:
    """
    ### enrich_user_message_with_character
    **Description :** Ajoute la fiche personnage JSON à la fin du message utilisateur pour le cache prompting OpenAI.
    **Paramètres :**
    - `message` (str) : Message utilisateur original.
    - `character_json` (str) : Fiche personnage JSON sérialisée.
    **Retour :** Message enrichi (str).
    """
    return f"{message}\n\nPERSONNAGE_JSON:\n{character_json}"

def _get_rules_content() -> str:
    """
    ### _get_rules_content
    **Description :** Charge et combine le contenu des règles du jeu depuis le dossier docs.
    **Paramètres :** Aucun.
    **Retour :** Contenu combiné des règles (str).
    """
    rules_content = []
    docs_dir = pathlib.Path(__file__).parent.parent.parent / "docs"
    
    # Fichiers de règles dans l'ordre d'importance
    rules_files = [
        # "01 - Caractéristiques, Races, Professions et Cultures.md",
        # "02 - Guide Complet des Compétences.md",
        "section-6-combat.md"
    ]
    
    for rules_file in rules_files:
        rules_path = docs_dir / rules_file
        if rules_path.exists():
            try:
                with open(rules_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    rules_content.append(f"=== {rules_file} ===\n{content}\n")
            except Exception as e:
                log_debug("Erreur lors du chargement des règles", error=str(e), file=rules_file)
    
    return "\n".join(rules_content)
