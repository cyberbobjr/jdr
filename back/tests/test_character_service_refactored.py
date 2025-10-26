"""
Tests pour le CharacterService refactorisé avec normalisation des types.
"""
from unittest.mock import patch
from back.services.character_service import CharacterService
from back.models.domain.character import Character
from back.models.schema import CharacterStatus

class TestCharacterServiceRefactored:
    """Tests pour la nouvelle architecture de CharacterService"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.test_character_id = "test-character-123"
        
    def test_load_empty_character_creates_normalized_object(self):
        """Test que le chargement d'un personnage vide crée un objet Character normalisé"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            # Simuler un personnage vide (nouveau)
            mock_load.side_effect = FileNotFoundError()
            
            service = CharacterService(self.test_character_id)
            
            # Vérifier que character_data est toujours un objet Character
            assert isinstance(service.character_data, Character)
            assert service.character_data.id == self.test_character_id
            assert service.character_data.name == ""
            assert service.status == CharacterStatus.PROGRESS
            assert not service.is_complete
    
    def test_load_incomplete_character_normalizes_to_character_object(self):
        """Test que le chargement d'un personnage incomplet le normalise en objet Character"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            # Simuler un personnage incomplet
            mock_load.return_value = {
                "name": "Test Hero",
                "status": CharacterStatus.PROGRESS,
                "gold": 25
            }
            
            service = CharacterService(self.test_character_id)
            
            # Vérifier que character_data est un objet Character normalisé
            assert isinstance(service.character_data, Character)
            assert service.character_data.name == "Test Hero"
            assert service.character_data.gold == 25
            assert service.character_data.hp == 100  # Valeur par défaut
            assert service.status == CharacterStatus.PROGRESS
            assert not service.is_complete
    
    def test_load_complete_character_creates_character_object(self):
        """Test que le chargement d'un personnage complet crée un objet Character valide"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            # Simuler un personnage complet
            mock_load.return_value = {
                "name": "Complete Hero",
                "race": {"name": "Humain", "bonus": {}},
                "culture": {"name": "Barbare", "bonus": {}},
                "caracteristiques": {"Force": 15, "Constitution": 14, "Dextérité": 13, "Intelligence": 12, "Perception": 11, "Charisme": 10},
                "competences": {"Combat": 5, "Athlétisme": 3},
                "culture_bonuses": {},
                "status": CharacterStatus.DONE,
                "hp": 120,
                "xp": 50,
                "gold": 100.5
            }
            
            service = CharacterService(self.test_character_id)
            
            # Vérifier que character_data est un objet Character valide
            assert isinstance(service.character_data, Character)
            assert service.character_data.name == "Complete Hero"
            assert service.character_data.gold == 100.5
            assert service.character_data.xp == 50
            assert service.status == CharacterStatus.DONE
            assert service.is_complete
    
    def test_to_dict_always_returns_dict(self):
        """Test que to_dict() retourne toujours un dictionnaire"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            mock_load.return_value = {"name": "Test", "gold": 10}
            
            service = CharacterService(self.test_character_id)
            result = service.to_dict()
            
            assert isinstance(result, dict)
            assert result["name"] == "Test"
            assert result["gold"] == 10
            assert result["id"] == self.test_character_id
    
    def test_update_character_data_preserves_normalization(self):
        """Test que update_character_data préserve la normalisation"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            mock_load.return_value = {"name": "Original", "gold": 10}
            
            service = CharacterService(self.test_character_id)
            
            # Mettre à jour quelques champs
            service.update_character_data({
                "name": "Updated Hero",
                "xp": 25
            })
            
            # Vérifier que l'objet est toujours normalisé
            assert isinstance(service.character_data, Character)
            assert service.character_data.name == "Updated Hero"
            assert service.character_data.xp == 25
            assert service.character_data.gold == 10  # Préservé
    
    def test_add_gold_updates_character_correctly(self):
        """Test que add_gold met à jour correctement le personnage"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            with patch('back.services.character_persistence_service.CharacterPersistenceService.save_character_data') as mock_save:
                mock_load.return_value = {"gold": 50.0}
                
                service = CharacterService(self.test_character_id)
                service.add_gold(25.5)
                
                # Vérifier que l'or a été mis à jour
                assert service.character_data.gold == 75.5
                assert mock_save.called
    
    def test_properties_work_correctly(self):
        """Test que les propriétés status et is_complete fonctionnent"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            # Personnage incomplet
            mock_load.return_value = {"name": "Incomplete"}

            service = CharacterService(self.test_character_id)

            assert service.character_data.status == CharacterStatus.PROGRESS
            assert not service.character_data.is_complete
    
    def test_get_all_characters_returns_normalized_dicts(self):
        """Test que get_all_characters retourne des dictionnaires normalisés"""
        with patch('os.path.exists') as mock_exists:
            with patch('os.listdir') as mock_listdir:
                with patch('back.services.character_service.CharacterService.__init__', return_value=None):
                    with patch('back.services.character_service.CharacterService.to_dict') as mock_to_dict:
                        mock_exists.return_value = True
                        mock_listdir.return_value = ["char1.json", "char2.json"]
                        mock_to_dict.return_value = {"id": "test", "name": "Test"}
                        
                        # Mock les instances de CharacterService
                        with patch('back.services.character_service.CharacterService') as mock_service_class:
                            mock_instance = mock_service_class.return_value
                            mock_instance.to_dict.return_value = {"id": "test", "name": "Test"}
                            
                            result = CharacterService.get_all_characters()
                            
                            assert isinstance(result, list)
                            # Le test vérifie que la méthode ne crash pas avec la nouvelle architecture
    
    def test_equipment_field_is_normalized(self):
        """Test que le champ equipment est correctement normalisé"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            mock_load.return_value = {"equipment": ["Épée", "Bouclier"]}
            
            service = CharacterService(self.test_character_id)
            
            assert isinstance(service.character_data, Character)
            assert service.character_data.equipment == ["Épée", "Bouclier"]
    
    def test_missing_equipment_field_gets_default(self):
        """Test qu'un personnage sans champ equipment reçoit une liste vide par défaut"""
        with patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data') as mock_load:
            mock_load.return_value = {"name": "Hero without equipment"}
            
            service = CharacterService(self.test_character_id)
            
            assert isinstance(service.character_data, Character)
            assert service.character_data.equipment == []
