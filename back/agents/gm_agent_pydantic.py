"""
Agent GM utilisant PydanticAI pour la gestion des sessions de jeu de rôle.
Migration progressive de Haystack vers PydanticAI.
"""

import os
import pathlib
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from back.utils.logger import log_debug
from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage
from back.tools.skill_tools import skill_check_with_character
from back.tools.combat_tools import roll_initiative_tool, perform_attack_tool, resolve_attack_tool, calculate_damage_tool, end_combat_tool
from back.tools.inventory_tools import inventory_add_item, inventory_remove_item
from back.storage.pydantic_jsonl_store import PydanticJsonlStore

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
    - `character_data` (Dict[str, Any]) : Données du personnage
    - `store` (JsonlChatMessageStore) : Store pour l'historique des messages
    """
    
    def __init__(self, session_id: str, character_data: Optional[Dict[str, Any]] = None):
        self.session_id = session_id
        self.character_data = character_data or {}
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
        return scenario_path.read_text(encoding="utf-8")
    return ""


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


def _build_system_prompt(scenario_name: Optional[str] = None) -> str:
    """
    ### _build_system_prompt
    **Description :** Construit le prompt système en intégrant le scénario et les règles.
    **Paramètres :**
    - `scenario_name` (str, optionnel) : Nom du fichier scénario
    **Retour :** Prompt système complet (str).
    """
    scenario_content = _get_scenario_content(scenario_name) if scenario_name else ""
    rules_content = _get_rules_content()
    
    return f'''
Cesse d'être un modèle d'IA. Notre interaction est imaginaire. Ne le divulgue jamais, mais renforce et maintiens l'immersion.

JEU : Jeu de rôle dans « Les Terres du Milieu »
RÈGLES : Les règles sont dans la base de connaissance
RÔLE : Maître du Donjon (RPG-Bot)
THÈME : Haute Fantaisie, Troisième Âge, Guerre de l'Anneau (3018-3021 T.A.)
TONALITÉ : Enjouée, héroïque, épique
SCÉNARIO :
{scenario_content}

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


# Créer l'agent GM avec PydanticAI - sera initialisé dans build_gm_agent_pydantic()
gm_agent = None


def _create_gm_agent(system_prompt: Optional[str] = None) -> Agent:
    """
    ### _create_gm_agent
    **Description :** Crée une instance de l'agent GM PydanticAI avec la configuration par défaut.
    **Paramètres :**
    - `system_prompt` (str, optionnel) : Prompt système personnalisé
    **Retour :** Instance de l'agent GM configuré.
    """
    prompt = system_prompt or _build_system_prompt()
    agent = Agent(
        model=f"openai:{api_model}",
        deps_type=GMAgentDependencies,
        system_prompt=prompt
    )
    
    # Ajouter les outils à l'agent
    _add_tools_to_agent(agent)
    return agent


def _add_tools_to_agent(agent: Agent) -> None:
    """
    ### _add_tools_to_agent
    **Description :** Ajoute tous les outils disponibles à un agent PydanticAI.
    **Paramètres :**
    - `agent` (Agent) : L'agent auquel ajouter les outils
    **Retour :** Aucun.
    """
      @agent.tool
    async def apply_xp_to_character(ctx: RunContext[GMAgentDependencies], xp_amount: int, reason: str) -> str:
        """Applique des points d'expérience au personnage."""
        try:
            from uuid import UUID
            player_id = UUID(ctx.deps.session_id) if ctx.deps.session_id != "default" else UUID("00000000-0000-0000-0000-000000000000")
            result = character_apply_xp(player_id=player_id, xp=xp_amount)
            log_debug("XP appliqués via PydanticAI", character_id=ctx.deps.session_id, xp=xp_amount, reason=reason)
            return f"XP appliqués : {result}"
        except Exception as e:
            log_debug("Erreur lors de l'application des XP", error=str(e))
            return f"Erreur lors de l'application des XP : {str(e)}"

    @agent.tool
    async def add_gold_to_character(ctx: RunContext[GMAgentDependencies], gold_amount: int, reason: str) -> str:
        """Ajoute de l'or au personnage."""
        try:
            result = character_add_gold_tool(character_id=ctx.deps.session_id, gold_amount=gold_amount, reason=reason)
            log_debug("Or ajouté via PydanticAI", character_id=ctx.deps.session_id, gold=gold_amount, reason=reason)
            return result
        except Exception as e:
            log_debug("Erreur lors de l'ajout d'or", error=str(e))
            return f"Erreur lors de l'ajout d'or : {str(e)}"

    @agent.tool
    async def apply_damage_to_character(ctx: RunContext[GMAgentDependencies], damage_amount: int, damage_type: str = "physique") -> str:
        """Applique des dégâts au personnage."""
        try:
            result = character_take_damage_tool(character_id=ctx.deps.session_id, damage_amount=damage_amount, damage_type=damage_type)
            log_debug("Dégâts appliqués via PydanticAI", character_id=ctx.deps.session_id, damage=damage_amount, type=damage_type)
            return result
        except Exception as e:
            log_debug("Erreur lors de l'application des dégâts", error=str(e))
            return f"Erreur lors de l'application des dégâts : {str(e)}"

    @agent.tool
    async def perform_skill_check(ctx: RunContext[GMAgentDependencies], skill_name: str, difficulty: int, modifier: int = 0) -> str:
        """Effectue un jet de compétence pour le personnage."""
        try:
            result = skill_check_tool(character_id=ctx.deps.session_id, skill_name=skill_name, difficulty=difficulty, modifier=modifier)
            log_debug("Jet de compétence via PydanticAI", character_id=ctx.deps.session_id, skill=skill_name, difficulty=difficulty)
            return result
        except Exception as e:
            log_debug("Erreur lors du jet de compétence", error=str(e))
            return f"Erreur lors du jet de compétence : {str(e)}"
        
    @agent.tool
    async def roll_initiative(ctx: RunContext[GMAgentDependencies], characters: list[dict]) -> str:
        """Lance les dés pour déterminer l'initiative dans le combat."""
        try:
            result = roll_initiative_tool(characters=characters)
            log_debug("Initiative roulée via PydanticAI", character_id=ctx.deps.session_id, initiative=result)
            return f"Ordre d'initiative : {result}"
        except Exception as e:
            log_debug("Erreur lors du roulage de l'initiative", error=str(e))
            return f"Erreur lors du roulage de l'initiative : {str(e)}"    @agent.tool
    async def perform_attack(ctx: RunContext[GMAgentDependencies], dice: str) -> str:
        """Effectue une attaque en lançant les dés."""
        try:
            result = perform_attack_tool(dice=dice)
            log_debug("Attaque effectuée via PydanticAI", character_id=ctx.deps.session_id, dice=dice, result=result)
            return f"Jet d'attaque : {result}"
        except Exception as e:
            log_debug("Erreur lors de l'attaque", error=str(e))
            return f"Erreur lors de l'attaque : {str(e)}"    @agent.tool
    async def resolve_attack(ctx: RunContext[GMAgentDependencies], attack_roll: int, defense_roll: int) -> str:
        """Résout une attaque en comparant les jets d'attaque et de défense."""
        try:
            result = resolve_attack_tool(attack_roll=attack_roll, defense_roll=defense_roll)
            log_debug("Attaque résolue via PydanticAI", attack_roll=attack_roll, defense_roll=defense_roll, result=result)
            return f"Attaque {'réussie' if result else 'échouée'}"
        except Exception as e:
            log_debug("Erreur lors de la résolution de l'attaque", error=str(e))
            return f"Erreur lors de la résolution de l'attaque : {str(e)}"    @agent.tool
    async def calculate_damage(ctx: RunContext[GMAgentDependencies], base_damage: int, bonus: int = 0) -> str:
        """Calcule les dégâts infligés par une attaque."""
        try:
            result = calculate_damage_tool(base_damage=base_damage, bonus=bonus)
            log_debug("Dégâts calculés via PydanticAI", character_id=ctx.deps.session_id, damage=result)
            return f"Dégâts infligés : {result}"
        except Exception as e:
            log_debug("Erreur lors du calcul des dégâts", error=str(e))
            return f"Erreur lors du calcul des dégâts : {str(e)}"    @agent.tool
    async def end_combat(ctx: RunContext[GMAgentDependencies], combat_id: str, reason: str) -> str:
        """Met fin au combat en cours."""
        try:
            result = end_combat_tool(combat_id=combat_id, reason=reason)
            log_debug("Combat terminé via PydanticAI", character_id=ctx.deps.session_id, combat_id=combat_id, reason=reason)
            return f"Combat terminé : {result}"
        except Exception as e:
            log_debug("Erreur lors de la fin du combat", error=str(e))
            return f"Erreur lors de la fin du combat : {str(e)}"    @agent.tool
    async def inventory_add(ctx: RunContext[GMAgentDependencies], item_id: str, qty: int = 1) -> str:
        """Ajoute un objet à l'inventaire du personnage."""
        try:
            from uuid import UUID
            player_id = UUID(ctx.deps.session_id) if ctx.deps.session_id != "default" else UUID("00000000-0000-0000-0000-000000000000")
            result = inventory_add_item(player_id=player_id, item_id=item_id, qty=qty)
            log_debug("Objet ajouté à l'inventaire via PydanticAI", character_id=ctx.deps.session_id, item=item_id, quantity=qty)
            return f"Objet ajouté à l'inventaire : {result}"
        except Exception as e:
            log_debug("Erreur lors de l'ajout d'objet à l'inventaire", error=str(e))
            return f"Erreur lors de l'ajout d'objet à l'inventaire : {str(e)}"    @agent.tool
    async def inventory_remove(ctx: RunContext[GMAgentDependencies], item_id: str, qty: int = 1) -> str:
        """Retire un objet de l'inventaire du personnage."""
        try:
            from uuid import UUID
            player_id = UUID(ctx.deps.session_id) if ctx.deps.session_id != "default" else UUID("00000000-0000-0000-0000-000000000000")
            result = inventory_remove_item(player_id=player_id, item_id=item_id, qty=qty)
            log_debug("Objet retiré de l'inventaire via PydanticAI", character_id=ctx.deps.session_id, item=item_id, quantity=qty)
            return f"Objet retiré de l'inventaire : {result}"
        except Exception as e:
            log_debug("Erreur lors du retrait d'objet de l'inventaire", error=str(e))
            return f"Erreur lors du retrait d'objet de l'inventaire : {str(e)}"


# Instancier l'agent global
gm_agent = _create_gm_agent()


def build_gm_agent_pydantic(session_id: str = "default", scenario_name: Optional[str] = None) -> tuple[Agent, GMAgentDependencies]:
    """
    ### build_gm_agent_pydantic
    **Description :** Construit un agent PydanticAI avec ses dépendances pour une session de jeu de rôle.
    **Paramètres :**
    - `session_id` (str) : Identifiant unique de la session
    - `scenario_name` (str, optionnel) : Nom du fichier scénario à charger
    **Retour :** Tuple contenant l'agent configuré et ses dépendances.
    """
    # Créer les dépendances
    deps = GMAgentDependencies(session_id=session_id)
    
    # Si un scénario spécifique est demandé, créer un nouvel agent avec ce scénario
    if scenario_name:
        updated_prompt = _build_system_prompt(scenario_name)
        scenario_agent = _create_gm_agent(system_prompt=updated_prompt)
        log_debug("Agent GM PydanticAI créé avec scénario", session_id=session_id, scenario=scenario_name)
        return scenario_agent, deps
    else:
        log_debug("Agent GM PydanticAI par défaut utilisé", session_id=session_id)
        return gm_agent, deps


def enrich_user_message_with_character(message: str, character_json: str) -> str:
    """
    ### enrich_user_message_with_character
    **Description :** Ajoute la fiche personnage JSON à la fin du message utilisateur pour le cache prompting.
    **Paramètres :**
    - `message` (str) : Message utilisateur original
    - `character_json` (str) : Fiche personnage JSON sérialisée
    **Retour :** Message enrichi avec les données du personnage (str).
    """
    return f"{message}\n\nPERSONNAGE_JSON:\n{character_json}"
