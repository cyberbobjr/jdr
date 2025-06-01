import unittest
from back.services.character_service import CharacterService
from back.models.schema import Character

class TestCharacterService(unittest.TestCase):
    def test_get_all_characters(self):
        characters = CharacterService.get_all_characters()
        self.assertIsInstance(characters, list)
        self.assertGreater(len(characters), 0)
        self.assertIsInstance(characters[0], Character)
        self.assertIn("equipment", characters[0].model_dump())
        self.assertIn("spells", characters[0].model_dump())
        self.assertIn("equipment_summary", characters[0].model_dump())
        self.assertIn("culture_bonuses", characters[0].model_dump())

if __name__ == "__main__":
    unittest.main()
