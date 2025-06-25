#!/usr/bin/env python3
"""
Test pour vérifier que l'utilisation d'un enum ne change pas la sortie JSON
"""

import json
from back.models.schema import CharacterStatus

def test_enum_json_output():
    """Teste que l'enum produit la même sortie JSON qu'une chaîne littérale"""
    
    # Test avec chaîne littérale
    data_with_string = {
        "name": "Test Character",
        "status": "en_cours"
    }
    
    # Test avec enum
    data_with_enum = {
        "name": "Test Character", 
        "status": CharacterStatus.IN_PROGRESS
    }
    
    # Sérialisation JSON
    json_string = json.dumps(data_with_string, default=str)
    json_enum = json.dumps(data_with_enum, default=str)
    
    print("Sortie JSON avec chaîne littérale:")
    print(json_string)
    print("\nSortie JSON avec enum:")
    print(json_enum)
    
    # Vérification que les deux sont identiques
    assert json_string == json_enum, f"Les sorties JSON diffèrent:\nString: {json_string}\nEnum: {json_enum}"
    
    print("\n✅ SUCCESS: Les sorties JSON sont identiques!")
    
    # Test de désérialisation
    parsed_string = json.loads(json_string)
    parsed_enum = json.loads(json_enum)
    
    assert parsed_string == parsed_enum, "Les données désérialisées diffèrent"
    print("✅ SUCCESS: Les données désérialisées sont identiques!")
    
    # Vérification des valeurs
    assert parsed_string["status"] == "en_cours"
    assert parsed_enum["status"] == "en_cours"
    print("✅ SUCCESS: La valeur du statut est bien 'en_cours' dans les deux cas!")

if __name__ == "__main__":
    test_enum_json_output()
