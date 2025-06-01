import unittest
from back.models.domain.caracteristiques import Caracteristiques

class TestCaracteristiques(unittest.TestCase):

    def setUp(self):
        self.caracteristiques = Caracteristiques()

    def test_initial_values(self):
        """Teste les valeurs initiales des caractéristiques."""
        expected_values = {name: 50 for name in Caracteristiques.NAMES}
        self.assertEqual(self.caracteristiques.values, expected_values)
        expected_racial_bonuses = {name: 0 for name in Caracteristiques.NAMES}
        self.assertEqual(self.caracteristiques.racial_bonuses, expected_racial_bonuses)

    def test_get_description(self):
        """Teste la récupération de la description d'une caractéristique."""
        desc_force = self.caracteristiques.get_description("Force")
        self.assertEqual(desc_force, Caracteristiques.CHARACTERISTICS_INFO["Force"])
        desc_unknown = self.caracteristiques.get_description("Inconnue")
        self.assertEqual(desc_unknown, "")

    def test_get_base_bonus(self):
        """Teste le calcul du bonus de base."""
        # Test des cas limites et des valeurs spécifiques de la table BONUS_TABLE
        self.assertEqual(self.caracteristiques._get_base_bonus(5), -18) # Range 1-5
        self.assertEqual(self.caracteristiques._get_base_bonus(10), -16) # Range 6-10
        self.assertEqual(self.caracteristiques._get_base_bonus(50), 0)  # Range 46-50
        self.assertEqual(self.caracteristiques._get_base_bonus(75), 5)  # Range 71-75
        self.assertEqual(self.caracteristiques._get_base_bonus(100), 10) # Range 96-100
        self.assertEqual(self.caracteristiques._get_base_bonus(101), 11) # Cas spécifique 101
        self.assertEqual(self.caracteristiques._get_base_bonus(105), 15) # Cas spécifique 105
        self.assertEqual(self.caracteristiques._get_base_bonus(0), 0) # Valeur hors table
        self.assertEqual(self.caracteristiques._get_base_bonus(110), 0) # Valeur hors table

    def test_get_bonus(self):
        """Teste le calcul du bonus final (valeur + bonus racial)."""
        self.caracteristiques.values["Force"] = 75
        self.caracteristiques.racial_bonuses["Force"] = 2
        # Bonus pour 75 est 5. 5 + 2 = 7
        self.assertEqual(self.caracteristiques.get_bonus("Force"), 7)

        self.caracteristiques.values["Agilité"] = 48
        self.caracteristiques.racial_bonuses["Agilité"] = -1
        # Bonus pour 48 est 0. 0 + (-1) = -1
        self.assertEqual(self.caracteristiques.get_bonus("Agilité"), -1)

    def test_calculate_cost(self):
        """Teste le calcul du coût des caractéristiques."""
        # Cas simples
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 10}), 10)
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 90}), 90)

        # Passage au coût de 2
        # 90 * 1 + 1 * 2 = 92
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 91}), 92)
        # 90 * 1 + 5 * 2 = 100
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 95}), 100)

        # Passage au coût de 3
        # 90 * 1 + 5 * 2 + 1 * 3 = 103
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 96}), 103)
        # 90 * 1 + 5 * 2 + 5 * 3 = 115
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 100}), 115)

        # Passage au coût de 10
        # 90 * 1 + 5 * 2 + 5 * 3 + 1 * 10 = 125
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 101}), 125)
        # 90 * 1 + 5 * 2 + 5 * 3 + 5 * 10 = 165
        self.assertEqual(self.caracteristiques.calculate_cost({"Force": 105}), 165)
        
        # Test avec plusieurs caractéristiques
        costs = self.caracteristiques.calculate_cost({"Force": 50, "Agilité": 100})
        expected_cost_force_50 = 50
        expected_cost_agilite_100 = 115
        self.assertEqual(costs, expected_cost_force_50 + expected_cost_agilite_100)

    def test_validate_distribution(self):
        """Teste la validation de la répartition des caractéristiques."""
        # Coût total = 50 (Force) + 50 (Agilité) = 100. Budget 550. Devrait être valide.
        self.assertTrue(self.caracteristiques.validate_distribution({"Force": 50, "Agilité": 50}))
        
        # Coût Force 105 = 165. Coût Agilité 105 = 165. Coût Constitution 105 = 165.
        # Total = 165 * 3 = 495. Budget 550. Devrait être valide.
        self.assertTrue(self.caracteristiques.validate_distribution({"Force": 105, "Agilité": 105, "Constitution": 105}))

        # Coût Force 105 = 165. Coût Agilité 105 = 165. Coût Constitution 105 = 165. Coût Rapidité 105 = 165
        # Total = 165 * 4 = 660. Budget 550. Devrait être invalide.
        self.assertFalse(self.caracteristiques.validate_distribution({"Force": 105, "Agilité": 105, "Constitution": 105, "Rapidité": 105}))

        # Test avec un budget personnalisé
        self.assertTrue(self.caracteristiques.validate_distribution({"Force": 100}, budget=115))
        self.assertFalse(self.caracteristiques.validate_distribution({"Force": 100}, budget=114))

    def test_get_profession_recommendations(self):
        """Teste la récupération des recommandations de caractéristiques par profession."""
        recommendations = self.caracteristiques.get_profession_recommendations()
        self.assertEqual(recommendations, Caracteristiques.PROFESSION_RECOMMENDATIONS)
        self.assertIn("Guerrier", recommendations)
        self.assertIn("Mage", recommendations)

if __name__ == '__main__':
    unittest.main()
