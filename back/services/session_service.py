"""
Service de gestion des sessions de jeu de rôle.
Gère le chargement et la sauvegarde de l'historique, ainsi que les données de personnage et de scénario.
Refactoré pour utiliser les services spécialisés (Phase 3).
"""

import os
import pathlib
from typing import Dict, Any, Optional, List

from back.models.domain.character import Character
from back.services.character_data_service import CharacterDataService
from back.services.character_business_service import CharacterBusinessService
from back.services.inventory_service import InventoryService
from back.services.equipment_service import EquipmentService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.config import get_data_dir


class SessionService:
    """
    ### SessionService
    **Description :** Service de gestion des sessions de jeu, incluant l'historique des messages,
    les données du personnage et du scénario.
    **Attributs :**
    - `session_id` (str) : Identifiant de la session
    - `character_data` (Character) : Données du personnage de la session (objet typé)
    - `scenario_name` (str) : Nom du scénario associé à la session
    - `store` (PydanticJsonlStore) : Store pour l'historique des messages
    - `data_service` (CharacterDataService) : Service de données pour le personnage
    - `business_service` (CharacterBusinessService) : Service de logique métier
    - `inventory_service` (InventoryService) : Service d'inventaire
    - `equipment_service` (EquipmentService) : Service d'équipement
    """
    
    def __init__(self, session_id: str, character_id: Optional[str] = None, scenario_name: Optional[str] = None):
        """
        ### __init__
        **Description :** Initialise le service de session avec un identifiant.
        **Paramètres :**
        - `session_id` (str) : Identifiant unique de la session
        - `character_id` (Optional[str]) : ID du personnage pour créer une nouvelle session
        - `scenario_name` (Optional[str]) : Nom du scénario pour créer une nouvelle session
        """
        self.session_id = session_id
        self.character_id = character_id
        self.character_data: Optional[Character] = None
        self.scenario_name: str = ""
        
        # Services spécialisés
        self.data_service: Optional[CharacterDataService] = None
        self.business_service: Optional[CharacterBusinessService] = None
        self.inventory_service: Optional[InventoryService] = None
        self.equipment_service: Optional[EquipmentService] = None
        
        # Initialiser le store pour l'historique
        if not os.path.isabs(session_id):
            history_path = os.path.join(get_data_dir(), "sessions", f"{session_id}.jsonl")
        else:
            history_path = session_id + ".jsonl"
        self.store = PydanticJsonlStore(history_path)
        
        # Charger les données de session ou créer une nouvelle session
        if not self._load_session_data():
            # Si la session n'existe pas et qu'on a fourni les paramètres, créer une nouvelle session
            if character_id and scenario_name:
                self._create_session(character_id, scenario_name)
            else:
                raise ValueError(f"Session {session_id} n'existe pas et les paramètres de création ne sont pas fournis")
            
    def _load_session_data(self) -> bool:
        """
        ### _load_session_data
        **Description :** Charge les données de session (personnage et scénario) depuis les fichiers.
        **Retour :** True si la session existe, False sinon.
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id
        if session_dir.exists() and session_dir.is_dir():
            # Charger l'ID du personnage
            character_file = session_dir / "character.txt"
            if character_file.exists():
                character_id = character_file.read_text(encoding='utf-8').strip()
                
                self.character_id = character_id  # Important: définir l'attribut character_id
                
                # Initialiser les services spécialisés pour ce personnage
                try:
                    self._initialize_services(character_id)
                    if self.data_service:
                        self.character_data = self.data_service.load_character(character_id)
                    else:
                        raise ValueError("Service de données non initialisé")
                except FileNotFoundError:
                    raise ValueError(f"Personnage {character_id} introuvable")
            
            # Charger le nom du scénario
            scenario_file = session_dir / "scenario.txt"
            if scenario_file.exists():
                self.scenario_name = scenario_file.read_text(encoding='utf-8').strip()
            else:
                self.scenario_name = 'Les_Pierres_du_Passe.md'  # Scénario par défaut
            
            return True
        
        return False
    
    def _create_session(self, character_id: str, scenario_name: str):
        """
        ### _create_session
        **Description :** Crée une nouvelle session avec l'ID du personnage et le nom du scénario.
        **Paramètres :**
        - `character_id` (str) : ID du personnage
        - `scenario_name` (str) : Nom du scénario
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id
        
        # Créer le répertoire de session
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder l'ID du personnage
        character_file = session_dir / "character.txt"
        character_file.write_text(character_id, encoding='utf-8')
        
        # Sauvegarder le nom du scénario
        scenario_file = session_dir / "scenario.txt"
        scenario_file.write_text(scenario_name, encoding='utf-8')
        
        # Définir l'attribut character_id
        self.character_id = character_id
        
        # Initialiser les services spécialisés pour ce personnage
        try:
            self._initialize_services(character_id)
            if self.data_service:
                self.character_data = self.data_service.load_character(character_id)
            else:
                raise ValueError("Service de données non initialisé")
        except FileNotFoundError:
            raise ValueError(f"Personnage {character_id} introuvable")
        
        self.scenario_name = scenario_name
    
    def _initialize_services(self, character_id: str):
        """
        ### _initialize_services
        **Description :** Initialise les services spécialisés pour un personnage donné.
        **Paramètres :**
        - `character_id` (str) : ID du personnage
        """
        # Service de données
        self.data_service = CharacterDataService(character_id)
        
        # Service de logique métier (dépend du service de données)
        self.business_service = CharacterBusinessService(self.data_service)
        
        # Service d'inventaire (dépend du service de données)
        self.inventory_service = InventoryService(self.data_service)
        
        # Service d'équipement (dépend du service de données)
        self.equipment_service = EquipmentService(self.data_service)
    
    def save_character(self) -> None:
        """
        ### save_character
        **Description :** Sauvegarde les données du personnage actuel.
        **Retour :** Aucun
        """
        if self.character_data and self.data_service:
            self.data_service.save_character(self.character_data)
    
    def apply_xp(self, xp: int) -> Character:
        """
        ### apply_xp
        **Description :** Applique de l'XP au personnage.
        **Paramètres :**
        - `xp` (int) : Points d'expérience à ajouter
        **Retour :** Personnage modifié
        """
        if self.character_data and self.business_service:
            self.character_data = self.business_service.apply_xp(self.character_data, xp)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    def add_gold(self, gold: float) -> Character:
        """
        ### add_gold
        **Description :** Ajoute de l'or au personnage.
        **Paramètres :**
        - `gold` (float) : Montant d'or à ajouter
        **Retour :** Personnage modifié
        """
        if self.character_data and self.business_service:
            self.character_data = self.business_service.add_gold(self.character_data, gold)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    def take_damage(self, amount: int, source: str = "combat") -> Character:
        """
        ### take_damage
        **Description :** Applique des dégâts au personnage.
        **Paramètres :**
        - `amount` (int) : Points de dégâts à appliquer
        - `source` (str) : Source des dégâts (optionnel)
        **Retour :** Personnage modifié
        """
        if self.character_data and self.business_service:
            self.character_data = self.business_service.take_damage(self.character_data, amount, source)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    def add_item(self, item_id: str, quantity: int = 1) -> Character:
        """
        ### add_item
        **Description :** Ajoute un objet à l'inventaire du personnage.
        **Paramètres :**
        - `item_id` (str) : Identifiant de l'objet
        - `quantity` (int) : Quantité à ajouter (défaut: 1)
        **Retour :** Personnage modifié
        """
        if self.character_data and self.inventory_service:
            self.character_data = self.inventory_service.add_item(self.character_data, item_id, quantity)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    def remove_item(self, item_id: str, quantity: int = 1) -> Character:
        """
        ### remove_item
        **Description :** Retire un objet de l'inventaire du personnage.
        **Paramètres :**
        - `item_id` (str) : Identifiant de l'objet
        - `quantity` (int) : Quantité à retirer (défaut: 1)
        **Retour :** Personnage modifié
        """
        if self.character_data and self.inventory_service:
            self.character_data = self.inventory_service.remove_item(self.character_data, item_id, quantity)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    def buy_equipment(self, equipment_name: str) -> Character:
        """
        ### buy_equipment
        **Description :** Achète un équipement pour le personnage.
        **Paramètres :**
        - `equipment_name` (str) : Nom de l'équipement
        **Retour :** Personnage modifié
        """
        if self.character_data and self.equipment_service:
            self.character_data = self.equipment_service.buy_equipment(self.character_data, equipment_name)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    def sell_equipment(self, equipment_name: str) -> Character:
        """
        ### sell_equipment
        **Description :** Vend un équipement du personnage.
        **Paramètres :**
        - `equipment_name` (str) : Nom de l'équipement
        **Retour :** Personnage modifié
        """
        if self.character_data and self.equipment_service:
            self.character_data = self.equipment_service.sell_equipment(self.character_data, equipment_name)
            return self.character_data
        raise ValueError("Services non initialisés")
    
    @staticmethod
    def list_all_sessions() -> List[Dict[str, Any]]:
        """
        ### list_all_sessions
        **Description :** Récupère la liste de toutes les sessions avec les informations du scénario et du personnage.
        **Retour :** Liste de dictionnaires contenant les informations de chaque session
        """
        sessions_dir = pathlib.Path(get_data_dir()) / "sessions"
        
        all_sessions = []
        
        if sessions_dir.exists() and sessions_dir.is_dir():
            for session_path in sessions_dir.iterdir():
                if session_path.is_dir():
                    # Charger l'ID du personnage
                    character_file = session_path / "character.txt"
                    if character_file.exists():
                        character_id = character_file.read_text(encoding='utf-8').strip()
                    else:
                        character_id = "Inconnu"
                    
                    # Charger le nom du scénario
                    scenario_file = session_path / "scenario.txt"
                    if scenario_file.exists():
                        scenario_name = scenario_file.read_text(encoding='utf-8').strip()
                    else:
                        scenario_name = "Inconnu"
                    
                    all_sessions.append({
                        "session_id": session_path.name,
                        "character_id": character_id,
                        "scenario_name": scenario_name
                    })
        
        return all_sessions

    # Les méthodes suivantes sont supprimées car elles ne sont utilisées que dans les tests :
    # - load_history
    # - save_history
    # - update_character_data
