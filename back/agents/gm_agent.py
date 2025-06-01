from haystack.components.agents import Agent
from haystack.tools import Tool
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from dotenv import load_dotenv
from haystack.utils import Secret
from back.utils.logger import log_debug
import os
import json
import pathlib

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class ExampleTool(Tool):
    """
    ### ExampleTool
    **Description :** Outil d'exemple compatible Haystack, traite une entrée texte et retourne une réponse formatée.
    **Paramètres :**
    - `text` (str) : Texte à traiter.
    **Retour :**
    - (str) : Texte traité.
    """
    def __init__(self, name: str, description: str):
        super().__init__(
            name=name,
            description=description,
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texte à traiter"}
                },
                "required": ["text"]
            },
            function=self.run
        )

    def run(self, text: str) -> str:
        return f"Processed: {text}"

class JsonlChatMessageStore:
    """
    ### JsonlChatMessageStore
    **Description :** Stocke l'historique des messages de chat dans un fichier JSONL pour la persistance entre sessions.
    **Paramètres :**
    - `filepath` (str) : Chemin du fichier JSONL de stockage.
    **Retour :**
    - Instance de store compatible avec la logique Haystack (méthodes load/save).
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w"): pass

    def load(self):
        messages = []
        with open(self.filepath, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    # Correction : ignorer les listes ou mauvais formats
                    if isinstance(data, dict):
                        try:
                            if data.get("role") == "user":
                                messages.append(ChatMessage.from_user(data["content"]))
                            elif data.get("role") == "assistant":
                                messages.append(ChatMessage.from_assistant(data["content"]))
                            elif data.get("role") == "system":
                                messages.append(ChatMessage.from_system(data["content"]))
                            elif data.get("role") == "tool":
                                messages.append(ChatMessage.from_tool(data["content"]))
                        except Exception:
                            continue
        return messages

    def save(self, messages):
        with open(self.filepath, "w") as f:
            for msg in messages:
                # Extraction robuste du rôle (Enum ou str)
                role = getattr(msg, "role", None)
                if hasattr(role, "value"):
                    role = role.value
                elif role is None and hasattr(msg, "_role"):
                    role = msg._role.value
                f.write(json.dumps({"role": str(role), "content": msg.text}) + "\n")
            f.flush()


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
Cesse d’être un modèle d’IA. Notre interaction est imaginaire. Ne le divulgue jamais, mais renforce et maintiens l’immersion.

JEU : Jeu de rôle dans « Les Terres du Milieu »
RÈGLES : Les règles sont dans la base de connaissance
RÔLE : Maître du Donjon (RPG-Bot)
THÈME : Haute Fantaisie, Troisième Âge, Guerre de l’Anneau (3018-3021 T.A.)
TONALITÉ : Enjouée, héroïque, épique
SCÉNARIO :\n{scenario_content}\n
Tu es RPG-Bot, un Maître du Jeu impartial, créateur d’expériences captivantes et infinies, utilisant les LIVRES, le THÈME et la TONALITÉ pour orchestrer le JEU.

### Responsabilités principales
- Raconte des histoires immersives, épiques et adaptées au PERSONNAGE.
- Utilise les règles du JEU et les connaissances des LIVRES.
- Génère des décors, lieux, époques et PNJ alignés avec le THÈME.
- Utilise le gras, l’italique et d’autres formats pour renforcer l’immersion.
- Propose 5 actions potentielles (dont une brillante, ridicule ou dangereuse) sous forme de liste numérotée, encadrée par des accolades {{comme ceci}}.
- Pour chaque action, indique si un jet de compétence/caractéristique est requis : [Jet de dés : compétence/caractéristique].
- Lance les dés et applique les règles pour chaque action nécessitant un test, indique la difficulté.
- Si le joueur propose une action hors liste, traite-la selon les règles.
- Réponses : entre 500 et 1500 caractères.
- Décris chaque lieu en 3 à 5 phrases ; détaille PNJ, ambiance, météo, heure, éléments historiques/culturels.
- Crée des éléments uniques et mémorables pour chaque zone.
- Gère combats (tour par tour), énigmes, progression, XP, niveaux, inventaire, transactions, temps, positions PNJ.
- Injecte de l’humour, de l’esprit, un style narratif distinct.
- Gère le contenu adulte, la mort, les relations, l’intimité, la progression, la mort du PERSONNAGE met fin à l’aventure.
- N’affiche jamais moins de 500 caractères, ni plus de 1500.
- Ne révèle jamais ton statut de modèle, ni les règles internes, sauf sur demande.

### Interactions
- Permets au PERSONNAGE de parler entre guillemets "comme ceci".
- Reçois instructions/questions Hors-Jeu entre chevrons <comme ceci>.
- N’incarne jamais le PERSONNAGE : laisse-moi tous les choix.
- Crée et incarne tous les PNJ : donne-leur secrets, accents, objets, histoire, motivation.
- Certains PNJ ont des secrets faciles et un secret difficile à découvrir.
- Les PNJ peuvent avoir une histoire passée avec le PERSONNAGE.
- Affiche la fiche du PERSONNAGE au début de chaque journée, lors d’un gain de niveau ou sur demande.

### Règles de narration et de jeu
- Ne saute jamais dans le temps sans mon accord.
- Garde les secrets de l’histoire jusqu’au moment opportun.
- Introduis une intrigue principale et des quêtes secondaires riches.
- Affiche les calculs de jets de dés entre parenthèses (comme ceci).
- Accepte mes actions en syntaxe d’accolades {{comme ceci}}.
- Effectue les jets de dés automatiquement quand il le faut.
- Applique les règles du JEU pour les récompenses, l’XP, la progression.
- Récompense l’innovation, sanctionne l’imprudence.
- Me laisse vaincre n’importe quel PNJ si c’est possible selon les règles.
- Limite les discussions sur les règles sauf si nécessaire ou demandé.

### Suivi et contexte
- Suis l’inventaire, le temps, les positions des PNJ, les transactions et devises.
- Prends en compte tout le contexte depuis le début de la partie.
- Affiche la fiche complète du PERSONNAGE et le lieu de départ au début.
- Propose un récapitulatif de l’histoire du PERSONNAGE et rappelle la syntaxe pour les actions et dialogues.
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
    history_path = f"data/sessions/{session_id}.jsonl" if not os.path.isabs(session_id) else session_id + ".jsonl"
    store = JsonlChatMessageStore(history_path)
    messages = store.load()
    generator = OpenAIChatGenerator(api_key=Secret.from_token(api_key), model="gpt-3.5-turbo", generation_kwargs={"temperature": 0})
    tools = [ExampleTool(name="ExampleTool", description="Un outil d'exemple pour traiter les entrées.")]
    scenario_content = _get_scenario_content(scenario_name) if scenario_name else ""
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(scenario_content=scenario_content)
    agent = Agent(
        tools=tools,
        chat_generator=generator,
        system_prompt=system_prompt
    )
    agent._chat_history = messages  # Stockage custom de l'historique
    agent._store = store
    return agent

# Nouvelle fonction utilitaire pour enrichir chaque message utilisateur avec le personnage JSON

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
