"""
Tests pour le système d'inventaire refactorisé avec objets Item détaillés.
"""

from back.services.item_service import ItemService
from back.services.character_service import CharacterService
from back.models.schema import ItemType

class TestInventoryRefactoring:
    """Tests de la refactorisation du système d'inventaire"""
    
    def test_item_service_creation(self):
        """Test de création du service ItemService"""
        service = ItemService()
        assert service is not None
        assert service._items_data is not None
        
    def test_create_item_from_name_coutelas(self):
        """Test de création d'un Coutelas depuis le nom"""
        service = ItemService()
        item = service.create_item_from_name("Coutelas")
        
        assert item is not None
        assert item.name == "Coutelas"
        assert item.item_type == ItemType.ARME
        assert item.price_pc == 200
        assert item.weight_kg == 0.5
        assert item.description == "Lame courte large"
        assert item.category == "Couteau"
        assert item.damage == "1d4"  # Dégâts d'arme
        assert item.is_equipped == False  # Par défaut
        
    def test_create_item_from_name_material(self):
        """Test de création d'un objet matériel"""
        service = ItemService()
        item = service.create_item_from_name("Bottes de cuir")
        
        assert item is not None
        assert item.name == "Bottes de cuir"
        assert item.item_type == ItemType.MATERIEL
        assert item.price_pc == 50
        assert item.weight_kg == 1.0
        assert item.description == "Chaussures en cuir"
        assert item.category == "Vetement"
        assert item.damage is None  # Pas une arme
        
    def test_convert_equipment_list_to_inventory(self):
        """Test de conversion d'une liste d'équipement vers un inventaire"""
        service = ItemService()
        equipment_names = ["Coutelas", "Bottes de cuir", "Bandoulière"]
        
        inventory = service.convert_equipment_list_to_inventory(equipment_names)
        
        assert len(inventory) == 3
        assert all(item.is_equipped == True for item in inventory)  # Tous équipés par défaut
        
        # Vérifier les objets spécifiques
        coutelas = next((item for item in inventory if item.name == "Coutelas"), None)
        assert coutelas is not None
        assert coutelas.item_type == ItemType.ARME
        assert coutelas.damage == "1d4"
        
    def test_character_service_inventory_conversion(self):
        """Test que le CharacterService convertit automatiquement l'équipement"""
        characters = CharacterService.get_all_characters()
        
        assert len(characters) > 0
        char = characters[0]
        
        # Vérifier qu'on a un inventaire
        assert hasattr(char, 'inventory')
        assert isinstance(char.inventory, list)
        assert len(char.inventory) > 0
        
        # Vérifier qu'on n'a plus de champ equipment dans le JSON
        char_dict = char.model_dump()
        assert 'equipment' not in char_dict
        assert 'inventory' in char_dict
        
        # Vérifier la structure des objets
        first_item = char.inventory[0]
        assert hasattr(first_item, 'id')
        assert hasattr(first_item, 'name')
        assert hasattr(first_item, 'item_type')
        assert hasattr(first_item, 'price_pc')
        assert hasattr(first_item, 'weight_kg')
        assert hasattr(first_item, 'is_equipped')
        
    def test_calculate_inventory_totals(self):
        """Test des calculs de totaux d'inventaire"""
        service = ItemService()
        inventory = service.convert_equipment_list_to_inventory(["Coutelas", "Bottes de cuir"])
        
        total_weight = service.calculate_total_weight(inventory)
        total_value = service.calculate_total_value(inventory)
        
        assert total_weight == 1.5  # 0.5 + 1.0
        assert total_value == 250   # 200 + 50
        
    def test_get_equipped_items(self):
        """Test du filtrage des objets équipés"""
        service = ItemService()
        inventory = service.convert_equipment_list_to_inventory(["Coutelas", "Bottes de cuir"])
        
        # Tous équipés par défaut
        equipped = service.get_equipped_items(inventory)
        assert len(equipped) == len(inventory)
        
        # Déséquiper un objet
        inventory[0].is_equipped = False
        equipped = service.get_equipped_items(inventory)
        assert len(equipped) == len(inventory) - 1
        
    def test_item_unknown_creates_generic(self):
        """Test qu'un objet inconnu crée un objet générique"""
        service = ItemService()
        item = service.create_item_from_name("Objet Inexistant")
        
        assert item is not None
        assert item.name == "Objet Inexistant"
        assert item.item_type == ItemType.MATERIEL
        assert item.price_pc == 0
        assert item.weight_kg == 0.0
        assert "générique" in item.description.lower()
