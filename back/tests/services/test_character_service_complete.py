# Tests complets pour CharacterService

import pytest
import json
from unittest.mock import Mock, patch

from back.services.character_service import CharacterService
from back.models.domain.character import Character


@pytest.fixture
def temp_data_dir(tmp_path):
    """
    Fixture qui crée un répertoire temporaire pour les données de test
    et le nettoie après utilisation
    """
    temp_dir = tmp_path / "test_data"
    temp_dir.mkdir()
    
    # Créer la structure de répertoires nécessaire
    characters_dir = temp_dir / "characters"
    characters_dir.mkdir()
    
    # Mock get_data_dir pour utiliser notre répertoire temporaire
    with patch('back.config.get_data_dir', return_value=str(temp_dir)):
        with patch('back.services.character_persistence_service.get_data_dir', return_value=str(temp_dir)):
            yield temp_dir


@pytest.fixture
def sample_character_data():
    """Données de test pour un personnage"""
    return {
        "name": "Test Hero",
        "race": "Humain",
        "culture": "Urbaine",
        
        "caracteristiques": {
            "Force": 15,
            "Constitution": 12,
            "Agilite": 10,
            "Rapidite": 11,
            "Volonte": 9,
            "Raisonnement": 8,
            "Intuition": 10,
            "Presence": 12
        },
        "competences": {
            "Athletisme": 8,
            "Combat": 10,
            "Esquive": 6
        },
        "hp": 100,
        "xp": 50,
        "gold": 150,
        "inventory": [],
        "spells": [],
        "equipment": [],
        "equipment_summary": {
            "total_weight": 0,
            "total_cost": 0,
            "remaining_money": 500
        }
    }


@pytest.fixture
def sample_item_data():
    """Données de test pour un objet"""
    return {
        "id": "sword_001",
        "name": "Épée courte",
        "item_type": "Arme",
        "price_pc": 50,
        "weight_kg": 1.5,
        "description": "Une épée courte basique",
        "category": "Épée",
        "damage": "1d6",
        "protection": None,
        "armor_type": None,
        "quantity": 1,
        "is_equipped": False,
        "crafting_time": None,
        "special_properties": None
    }


class TestCharacterServiceInit:
    """Tests pour l'initialisation du service"""
    
    def test_init_with_existing_character(self, temp_data_dir, sample_character_data):
        """Test d'initialisation avec un personnage existant"""
        character_id = "test_hero_001"
        
        # Créer le fichier de personnage
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        # Initialiser le service
        service = CharacterService(character_id)
        
        assert service.character_id == character_id
        assert isinstance(service.character_data, Character)
        assert service.character_data.name == "Test Hero"
        assert service.character_data.id == character_id
    
    def test_init_with_nonexistent_character(self, temp_data_dir):
        """Test d'initialisation avec un personnage inexistant"""
        character_id = "nonexistent_hero"
        
        with pytest.raises(FileNotFoundError):
            CharacterService(character_id)


class TestCharacterServiceLoading:
    """Tests pour le chargement des données"""
    
    def test_load_character_with_equipment_conversion(self, temp_data_dir):
        """Test de conversion de l'ancien format equipment vers inventory"""
        character_id = "test_conversion"
        character_data = {
            "name": "Test Conversion",
            "race": "Elfe",
            "culture": "Forestière",
            
            "caracteristiques": {"Force": 10, "Constitution": 10, "Agilite": 15},
            "competences": {"Tir": 8},
            "equipment": ["Arc long", "Flèches (20)"],  # Ancien format
            "hp": 80,
            "xp": 25,
            "gold": 75
        }
        
        # Créer le fichier
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(character_data))
        
        # Mock ItemService pour la conversion
        with patch('back.services.item_service.ItemService') as mock_item_service:
            mock_service_instance = Mock()
            mock_item_service.return_value = mock_service_instance
            
            # Mock de la conversion
            mock_item1 = Mock()
            mock_item1.model_dump.return_value = {"id": "arc_long", "name": "Arc long"}
            mock_item2 = Mock()
            mock_item2.model_dump.return_value = {"id": "fleches_20", "name": "Flèches (20)"}
            
            mock_service_instance.convert_equipment_list_to_inventory.return_value = [mock_item1, mock_item2]
            
            service = CharacterService(character_id)
            
            # Vérifier que la conversion a été effectuée
            assert hasattr(service.character_data, 'inventory')
            assert not hasattr(service.character_data, 'equipment') or not service.character_data.equipment
            mock_service_instance.convert_equipment_list_to_inventory.assert_called_once()
    
    def test_load_character_with_default_values(self, temp_data_dir):
        """Test de chargement avec ajout des valeurs par défaut"""
        character_id = "test_defaults"
        character_data = {
            "name": "Test Defaults",
            "race": "Nain",
            "culture": "Montagnarde",
            
            "caracteristiques": {"Force": 16, "Constitution": 14},
            "competences": {"Artisanat": 10}
            # Pas de hp, xp, gold
        }
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(character_data))
        
        service = CharacterService(character_id)
        
        # Vérifier les valeurs par défaut
        assert service.character_data.hp == 100
        assert service.character_data.xp == 0
        assert service.character_data.gold == 0
        assert service.character_data.inventory == []


class TestCharacterServiceSaving:
    """Tests pour la sauvegarde des données"""
    
    def test_save_character(self, temp_data_dir, sample_character_data):
        """Test de sauvegarde d'un personnage"""
        character_id = "test_save"
        
        # Créer le fichier initial
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Modifier les données
        service.character_data.hp = 85
        service.character_data.xp = 100
        
        # Sauvegarder
        service.save_character()
        
        # Vérifier que les modifications ont été sauvegardées
        saved_data = json.loads(character_file.read_text())
        assert saved_data["hp"] == 85
        assert saved_data["xp"] == 100
        assert "id" not in saved_data  # L'ID ne doit pas être dans le fichier


class TestCharacterServiceGetters:
    """Tests pour les méthodes de récupération des données"""
    
    def test_get_character(self, temp_data_dir, sample_character_data):
        """Test de récupération de l'objet Character"""
        character_id = "test_get"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        character = service.get_character()
        
        assert isinstance(character, Character)
        assert character.name == "Test Hero"
        assert character.id == character_id
    
    def test_get_character_json(self, temp_data_dir, sample_character_data):
        """Test de récupération des données JSON"""
        character_id = "test_get_json"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        json_data = service.get_character_json()
        
        assert isinstance(json_data, str)
        parsed_data = json.loads(json_data)
        assert parsed_data["name"] == "Test Hero"
        assert parsed_data["id"] == character_id


class TestCharacterServiceStaticMethods:
    """Tests pour les méthodes statiques"""
    
    def test_get_all_characters(self, temp_data_dir):
        """Test de récupération de tous les personnages"""
        # Créer plusieurs personnages
        characters_data = [
            {
                "name": "Hero 1",
                "race": "Humain",
                "culture": "Urbaine",
                
                "caracteristiques": {"Force": 15},
                "competences": {"Combat": 8},
                "hp": 100,
                "xp": 0,
                "gold": 0
            },
            {
                "name": "Hero 2",
                "race": "Elfe",
                "culture": "Forestière",
                
                "caracteristiques": {"Agilite": 16},
                "competences": {"Tir": 9},
                "hp": 90,
                "xp": 50,
                "gold": 120
            }
        ]
        
        characters_dir = temp_data_dir / "characters"
        for i, data in enumerate(characters_data):
            character_file = characters_dir / f"hero_{i+1}.json"
            character_file.write_text(json.dumps(data))
        
        characters = CharacterService.get_all_characters()
        
        assert len(characters) == 2
        assert all(isinstance(char, Character) for char in characters)
        assert characters[0].name == "Hero 1"
        assert characters[1].name == "Hero 2"
    
    def test_get_all_characters_with_incomplete_data(self, temp_data_dir):
        """Test de récupération avec des données incomplètes"""
        # Personnage complet
        complete_data = {
            "name": "Complete Hero",
            "race": "Humain",
            "culture": "Urbaine",
            
            "caracteristiques": {"Force": 15},
            "competences": {"Combat": 8}
        }
        
        # Personnage incomplet (manque des champs requis)
        incomplete_data = {
            "name": "Incomplete Hero",
            "race": "Elfe"
            # Manque culture, caracteristiques, competences
        }
        
        characters_dir = temp_data_dir / "characters"
        (characters_dir / "complete.json").write_text(json.dumps(complete_data))
        (characters_dir / "incomplete.json").write_text(json.dumps(incomplete_data))
        
        characters = CharacterService.get_all_characters()
        
        # Seul le personnage complet doit être retourné
        assert len(characters) == 1
        assert characters[0].name == "Complete Hero"
    
    def test_get_character_by_id(self, temp_data_dir, sample_character_data):
        """Test de récupération d'un personnage par ID"""
        character_id = "test_get_by_id"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        character_data = CharacterService.get_character_by_id(character_id)
        
        assert isinstance(character_data, dict)
        assert character_data["name"] == "Test Hero"
        assert character_data["id"] == character_id


class TestCharacterServiceXPManagement:
    """Tests pour la gestion de l'XP"""
    
    def test_apply_xp(self, temp_data_dir, sample_character_data):
        """Test d'ajout d'XP"""
        character_id = "test_xp"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        initial_xp = service.character_data.xp
        
        # Ajouter 25 XP
        service.apply_xp(25)
        
        assert service.character_data.xp == initial_xp + 25
        
        # Vérifier que la sauvegarde a été effectuée
        saved_data = json.loads(character_file.read_text())
        assert saved_data["xp"] == initial_xp + 25
    
    def test_apply_xp_with_zero_initial(self, temp_data_dir):
        """Test d'ajout d'XP avec XP initial à zéro"""
        character_id = "test_xp_zero"
        character_data = {
            "name": "Test Zero XP",
            "race": "Humain",
            "culture": "Urbaine",
            
            "caracteristiques": {"Force": 15},
            "competences": {"Combat": 8}
            # Pas de champ xp initial
        }
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter 30 XP
        service.apply_xp(30)
        
        assert service.character_data.xp == 30


class TestCharacterServiceGoldManagement:
    """Tests pour la gestion de l'or"""
    
    def test_add_gold(self, temp_data_dir, sample_character_data):
        """Test d'ajout d'or"""
        character_id = "test_gold"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        initial_gold = service.character_data.gold
        
        # Ajouter 100 pièces d'or
        service.add_gold(100)
        
        assert service.character_data.gold == initial_gold + 100
        
        # Vérifier la sauvegarde
        saved_data = json.loads(character_file.read_text())
        assert saved_data["gold"] == initial_gold + 100
    
    def test_add_gold_with_zero_initial(self, temp_data_dir):
        """Test d'ajout d'or avec or initial à zéro"""
        character_id = "test_gold_zero"
        character_data = {
            "name": "Test Zero Gold",
            "race": "Humain",
            "culture": "Urbaine",
            
            "caracteristiques": {"Force": 15},
            "competences": {"Combat": 8}
            # Pas de champ gold initial
        }
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter 50 pièces d'or
        service.add_gold(50)
        
        assert service.character_data.gold == 50


class TestCharacterServiceHealthManagement:
    """Tests pour la gestion des points de vie"""
    
    def test_take_damage(self, temp_data_dir, sample_character_data):
        """Test d'application de dégâts"""
        character_id = "test_damage"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        initial_hp = service.character_data.hp
        
        # Appliquer 20 points de dégâts
        service.take_damage(20)
        
        assert service.character_data.hp == initial_hp - 20
        
        # Vérifier la sauvegarde
        saved_data = json.loads(character_file.read_text())
        assert saved_data["hp"] == initial_hp - 20
    
    def test_take_damage_with_source(self, temp_data_dir, sample_character_data):
        """Test d'application de dégâts avec source"""
        character_id = "test_damage_source"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        initial_hp = service.character_data.hp
        
        # Appliquer 15 points de dégâts avec source
        service.take_damage(15, "spell")
        
        assert service.character_data.hp == initial_hp - 15
    
    def test_take_damage_not_below_zero(self, temp_data_dir, sample_character_data):
        """Test que les HP ne descendent pas en dessous de zéro"""
        character_id = "test_damage_zero"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        initial_hp = service.character_data.hp
        
        # Appliquer plus de dégâts que les HP actuels
        service.take_damage(initial_hp + 50)
        
        assert service.character_data.hp == 0


class TestCharacterServiceItemManagement:
    """Tests pour la gestion des objets"""
    
    def test_instantiate_item_by_id(self, temp_data_dir, sample_character_data):
        """Test d'instanciation d'un objet par ID"""
        character_id = "test_instantiate"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock ItemService
        with patch('back.services.item_service.ItemService') as mock_item_service:
            mock_service_instance = Mock()
            mock_item_service.return_value = mock_service_instance
            
            mock_item = Mock()
            mock_service_instance.create_item_from_name.return_value = mock_item
            
            result = service.instantiate_item_by_id("sword_001", 2)
            
            assert result == mock_item
            mock_service_instance.create_item_from_name.assert_called_once_with("sword_001", quantity=2)
    
    def test_add_item_object_new_item(self, temp_data_dir, sample_character_data):
        """Test d'ajout d'un nouvel objet"""
        character_id = "test_add_object"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Créer un mock item
        mock_item = Mock()
        mock_item.id = "sword_001"
        mock_item.quantity = 1
        mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "quantity": 1}
        
        result = service.add_item_object(mock_item)
        
        assert "inventory" in result
        assert len(service.character_data.inventory) == 1
        assert service.character_data.inventory[0] == mock_item
    
    def test_add_item_object_existing_item(self, temp_data_dir, sample_character_data):
        """Test d'ajout d'un objet existant (augmente la quantité)"""
        character_id = "test_add_existing"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter d'abord un objet
        mock_item1 = Mock()
        mock_item1.id = "sword_001"
        mock_item1.quantity = 1
        mock_item1.model_dump.return_value = {"id": "sword_001", "name": "Épée", "quantity": 1}
        
        service.character_data.inventory = [mock_item1]
        
        # Ajouter le même objet
        mock_item2 = Mock()
        mock_item2.id = "sword_001"
        mock_item2.quantity = 2
        
        result = service.add_item_object(mock_item2)
        
        assert len(service.character_data.inventory) == 1
        assert mock_item1.quantity == 3  # 1 + 2
    
    def test_item_exists(self, temp_data_dir, sample_character_data):
        """Test de vérification d'existence d'un objet"""
        character_id = "test_exists"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter un objet
        mock_item = Mock()
        mock_item.id = "sword_001"
        service.character_data.inventory = [mock_item]
        
        assert service.item_exists("sword_001") == True
        assert service.item_exists("shield_001") == False
    
    def test_item_exists_empty_inventory(self, temp_data_dir, sample_character_data):
        """Test de vérification d'existence avec inventaire vide"""
        character_id = "test_exists_empty"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        service.character_data.inventory = []
        
        assert service.item_exists("sword_001") == False
    
    def test_add_item_new(self, temp_data_dir, sample_character_data):
        """Test d'ajout d'un objet par ID (nouvel objet)"""
        character_id = "test_add_new"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock ItemService et l'objet créé
        with patch('back.services.item_service.ItemService') as mock_item_service:
            mock_service_instance = Mock()
            mock_item_service.return_value = mock_service_instance
            
            mock_item = Mock()
            mock_item.id = "sword_001"
            mock_item.quantity = 2
            mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "quantity": 2}
            mock_service_instance.create_item_from_name.return_value = mock_item
            
            result = service.add_item("sword_001", 2)
            
            assert "inventory" in result
            assert len(service.character_data.inventory) == 1
            assert service.character_data.inventory[0] == mock_item
    
    def test_add_item_existing(self, temp_data_dir, sample_character_data):
        """Test d'ajout d'un objet existant par ID"""
        character_id = "test_add_existing_id"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter d'abord un objet
        mock_item = Mock()
        mock_item.id = "sword_001"
        mock_item.quantity = 1
        mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "quantity": 1}
        
        service.character_data.inventory = [mock_item]
        
        # Ajouter le même objet par ID
        result = service.add_item("sword_001", 3)
        
        assert len(service.character_data.inventory) == 1
        assert mock_item.quantity == 4  # 1 + 3
    
    def test_remove_item(self, temp_data_dir, sample_character_data):
        """Test de suppression d'un objet"""
        character_id = "test_remove"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter un objet avec quantité 5
        mock_item = Mock()
        mock_item.id = "sword_001"
        mock_item.quantity = 5
        mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "quantity": 5}
        
        service.character_data.inventory = [mock_item]
        
        # Retirer 2 objets
        result = service.remove_item("sword_001", 2)
        
        assert len(service.character_data.inventory) == 1
        assert mock_item.quantity == 3  # 5 - 2
        assert "inventory" in result
    
    def test_remove_item_complete(self, temp_data_dir, sample_character_data):
        """Test de suppression complète d'un objet"""
        character_id = "test_remove_complete"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter un objet avec quantité 2
        mock_item = Mock()
        mock_item.id = "sword_001"
        mock_item.quantity = 2
        mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "quantity": 2}
        
        service.character_data.inventory = [mock_item]
        
        # Retirer 3 objets (plus que disponible)
        result = service.remove_item("sword_001", 3)
        
        assert len(service.character_data.inventory) == 0  # Objet supprimé
        assert "inventory" in result
    
    def test_equip_item(self, temp_data_dir, sample_character_data):
        """Test d'équipement d'un objet"""
        character_id = "test_equip"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter un objet
        mock_item = Mock()
        mock_item.id = "sword_001"
        mock_item.is_equipped = False
        mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "is_equipped": False}
        
        service.character_data.inventory = [mock_item]
        
        # Équiper l'objet
        result = service.equip_item("sword_001")
        
        assert mock_item.is_equipped == True
        assert "inventory" in result
    
    def test_unequip_item(self, temp_data_dir, sample_character_data):
        """Test de déséquipement d'un objet"""
        character_id = "test_unequip"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Ajouter un objet équipé
        mock_item = Mock()
        mock_item.id = "sword_001"
        mock_item.is_equipped = True
        mock_item.model_dump.return_value = {"id": "sword_001", "name": "Épée", "is_equipped": True}
        
        service.character_data.inventory = [mock_item]
        
        # Déséquiper l'objet
        result = service.unequip_item("sword_001")
        
        assert mock_item.is_equipped == False
        assert "inventory" in result


class TestCharacterServiceEquipmentManagement:
    """Tests pour la gestion de l'équipement (achat/vente)"""
    
    def test_buy_equipment(self, temp_data_dir, sample_character_data):
        """Test d'achat d'équipement"""
        character_id = "test_buy"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock EquipmentManager
        with patch('back.models.domain.equipment_manager.EquipmentManager') as mock_equipment_manager:
            mock_manager_instance = Mock()
            mock_equipment_manager.return_value = mock_manager_instance
            
            equipment_details = {
                "name": "Épée longue",
                "cost": 100,
                "weight": 3.0,
                "damage": "1d8",
                "category": "Épée"
            }
            mock_manager_instance.get_equipment_by_name.return_value = equipment_details
            
            result = service.buy_equipment("Épée longue")
            
            assert result["status"] == "success"
            assert result["remaining_money"] == 400  # 500 - 100
            assert result["total_weight"] == 3.0
            assert "Épée longue" in service.character_data.equipment
    
    def test_buy_equipment_insufficient_funds(self, temp_data_dir, sample_character_data):
        """Test d'achat d'équipement avec fonds insuffisants"""
        character_id = "test_buy_insufficient"
        
        # Modifier l'argent disponible
        sample_character_data["equipment_summary"]["remaining_money"] = 50
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock EquipmentManager
        with patch('back.models.domain.equipment_manager.EquipmentManager') as mock_equipment_manager:
            mock_manager_instance = Mock()
            mock_equipment_manager.return_value = mock_manager_instance
            
            equipment_details = {
                "name": "Épée longue",
                "cost": 100,
                "weight": 3.0
            }
            mock_manager_instance.get_equipment_by_name.return_value = equipment_details
            
            with pytest.raises(ValueError, match="Pas assez d'argent"):
                service.buy_equipment("Épée longue")
    
    def test_buy_equipment_nonexistent(self, temp_data_dir, sample_character_data):
        """Test d'achat d'équipement inexistant"""
        character_id = "test_buy_nonexistent"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock EquipmentManager
        with patch('back.models.domain.equipment_manager.EquipmentManager') as mock_equipment_manager:
            mock_manager_instance = Mock()
            mock_equipment_manager.return_value = mock_manager_instance
            
            mock_manager_instance.get_equipment_by_name.return_value = None
            
            with pytest.raises(ValueError, match="Équipement .* non trouvé"):
                service.buy_equipment("Arme inexistante")
    
    def test_sell_equipment(self, temp_data_dir, sample_character_data):
        """Test de vente d'équipement"""
        character_id = "test_sell"
        
        # Ajouter un équipement à vendre
        sample_character_data["equipment"] = ["Épée longue"]
        sample_character_data["equipment_summary"]["total_cost"] = 100
        sample_character_data["equipment_summary"]["total_weight"] = 3.0
        sample_character_data["equipment_summary"]["remaining_money"] = 400
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock EquipmentManager
        with patch('back.models.domain.equipment_manager.EquipmentManager') as mock_equipment_manager:
            mock_manager_instance = Mock()
            mock_equipment_manager.return_value = mock_manager_instance
            
            equipment_details = {
                "name": "Épée longue",
                "cost": 100,
                "weight": 3.0
            }
            mock_manager_instance.get_equipment_by_name.return_value = equipment_details
            
            result = service.sell_equipment("Épée longue")
            
            assert result["status"] == "success"
            assert result["remaining_money"] == 500  # 400 + 100
            assert result["total_weight"] == 0.0
            assert "Épée longue" not in service.character_data.equipment
    
    def test_sell_equipment_nonexistent(self, temp_data_dir, sample_character_data):
        """Test de vente d'équipement inexistant"""
        character_id = "test_sell_nonexistent"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Mock EquipmentManager
        with patch('back.models.domain.equipment_manager.EquipmentManager') as mock_equipment_manager:
            mock_manager_instance = Mock()
            mock_equipment_manager.return_value = mock_manager_instance
            
            mock_manager_instance.get_equipment_by_name.return_value = None
            
            with pytest.raises(ValueError, match="Équipement .* non trouvé"):
                service.sell_equipment("Arme inexistante")
    
    def test_update_money_positive(self, temp_data_dir, sample_character_data):
        """Test de mise à jour de l'argent (ajout)"""
        character_id = "test_update_money_positive"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        result = service.update_money(100)
        
        assert result["status"] == "success"
        assert result["remaining_money"] == 600  # 500 + 100
    
    def test_update_money_negative(self, temp_data_dir, sample_character_data):
        """Test de mise à jour de l'argent (soustraction)"""
        character_id = "test_update_money_negative"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        result = service.update_money(-200)
        
        assert result["status"] == "success"
        assert result["remaining_money"] == 300  # 500 - 200
    
    def test_update_money_not_below_zero(self, temp_data_dir, sample_character_data):
        """Test que l'argent ne descend pas en dessous de zéro"""
        character_id = "test_update_money_zero"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        result = service.update_money(-600)  # Plus que l'argent disponible
        
        assert result["status"] == "success"
        assert result["remaining_money"] == 0  # Ne descend pas en dessous de 0


class TestCharacterServiceConversion:
    """Tests pour la conversion de données"""
    
    def test_convert_equipment_to_inventory_with_items(self, temp_data_dir):
        """Test de conversion equipment vers inventory avec objets"""
        state_data = {
            "equipment": ["Épée courte", "Bouclier", "Armure de cuir"],
            "name": "Test Conversion"
        }
        
        # Mock ItemService
        with patch('back.services.item_service.ItemService') as mock_item_service:
            mock_service_instance = Mock()
            mock_item_service.return_value = mock_service_instance
            
            # Mock des objets convertis
            mock_items = [Mock(), Mock(), Mock()]
            for i, item in enumerate(mock_items):
                item.model_dump.return_value = {"id": f"item_{i}", "name": f"Item {i}"}
            
            mock_service_instance.convert_equipment_list_to_inventory.return_value = mock_items
            
            CharacterService._convert_equipment_to_inventory(state_data)
            
            assert "inventory" in state_data
            assert "equipment" not in state_data
            assert len(state_data["inventory"]) == 3
            mock_service_instance.convert_equipment_list_to_inventory.assert_called_once()
    
    def test_convert_equipment_to_inventory_empty_equipment(self, temp_data_dir):
        """Test de conversion avec équipement vide"""
        state_data = {
            "equipment": [],
            "name": "Test Empty Equipment"
        }
        
        CharacterService._convert_equipment_to_inventory(state_data)
        
        assert "inventory" in state_data
        assert state_data["inventory"] == []
        assert "equipment" not in state_data
    
    def test_convert_equipment_to_inventory_no_equipment(self, temp_data_dir):
        """Test de conversion sans champ equipment"""
        state_data = {
            "name": "Test No Equipment"
        }
        
        CharacterService._convert_equipment_to_inventory(state_data)
        
        assert "inventory" in state_data
        assert state_data["inventory"] == []
    
    def test_convert_equipment_to_inventory_existing_inventory(self, temp_data_dir):
        """Test de conversion avec inventaire existant (pas de conversion)"""
        state_data = {
            "equipment": ["Épée courte"],
            "inventory": [{"id": "existing_item", "name": "Existing Item"}],
            "name": "Test Existing Inventory"
        }
        
        CharacterService._convert_equipment_to_inventory(state_data)
        
        # L'inventaire existant ne doit pas être modifié
        assert len(state_data["inventory"]) == 1
        assert state_data["inventory"][0]["name"] == "Existing Item"
        assert "equipment" in state_data  # Equipment reste car inventory existe déjà


class TestCharacterServiceErrorHandling:
    """Tests pour la gestion des erreurs"""
    
    def test_character_service_with_corrupted_file(self, temp_data_dir):
        """Test avec un fichier corrompu"""
        character_id = "test_corrupted"
        
        # Créer un fichier avec du JSON invalide
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text("{invalid json content")
        
        with pytest.raises(json.JSONDecodeError):
            CharacterService(character_id)
    
    def test_get_all_characters_with_corrupted_file(self, temp_data_dir):
        """Test de get_all_characters avec un fichier corrompu"""
        # Créer un fichier valide
        valid_data = {
            "name": "Valid Hero",
            "race": "Humain",
            "culture": "Urbaine",
            
            "caracteristiques": {"Force": 15},
            "competences": {"Combat": 8}
        }
        
        characters_dir = temp_data_dir / "characters"
        (characters_dir / "valid.json").write_text(json.dumps(valid_data))
        
        # Créer un fichier corrompu
        (characters_dir / "corrupted.json").write_text("{invalid json")
        
        # La méthode doit retourner seulement les personnages valides
        characters = CharacterService.get_all_characters()
        
        assert len(characters) == 1
        assert characters[0].name == "Valid Hero"
    
    def test_operations_on_nonexistent_items(self, temp_data_dir, sample_character_data):
        """Test des opérations sur des objets inexistants"""
        character_id = "test_nonexistent_items"
        
        character_file = temp_data_dir / "characters" / f"{character_id}.json"
        character_file.write_text(json.dumps(sample_character_data))
        
        service = CharacterService(character_id)
        
        # Tenter d'équiper un objet inexistant
        result = service.equip_item("nonexistent_item")
        assert "inventory" in result  # Doit retourner un résultat même si l'objet n'existe pas
        
        # Tenter de déséquiper un objet inexistant
        result = service.unequip_item("nonexistent_item")
        assert "inventory" in result
        
        # Tenter de supprimer un objet inexistant
        result = service.remove_item("nonexistent_item")
        assert "inventory" in result
