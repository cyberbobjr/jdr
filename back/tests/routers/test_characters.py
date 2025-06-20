import json
import uuid

def test_list_characters(client, isolated_data_dir):
    # Création d'un personnage strictement conforme au modèle métier, tout à la racine
    character_id = str(uuid.uuid4())
    characters_dir = isolated_data_dir / "characters"
    characters_dir.mkdir(exist_ok=True)
    character_data = {
        "id": character_id,
        "name": "Test Hero",
        "race": "Humain",
        "culture": "Rurale",
        
        "caracteristiques": {
            "Force": 10,
            "Constitution": 10,
            "Agilite": 10,
            "Rapidite": 10,
            "Volonte": 10,
            "Raisonnement": 10,
            "Intuition": 10,
            "Presence": 10
        },
        "competences": {"Athletisme": 5},
        "hp": 42,
        "xp": 0,
        "gold": 0,
        "inventory": [],
        "spells": [],
        "culture_bonuses": {"Endurance": 1}
    }
    (characters_dir / f"{character_id}.json").write_text(json.dumps(character_data), encoding="utf-8")
    response = client.get("/api/characters")
    assert response.status_code == 200
    data = response.json()
    assert "characters" in data
    assert isinstance(data["characters"], list)
    assert len(data["characters"]) > 0

def test_get_character_detail(client, isolated_data_dir):
    """
    Teste la récupération du détail d'un personnage par son id.
    """
    import uuid
    character_id = str(uuid.uuid4())
    characters_dir = isolated_data_dir / "characters"
    characters_dir.mkdir(exist_ok=True)
    character_data = {
        "id": character_id,
        "name": "Test Hero",
        "race": "Humain",
        "culture": "Rurale",
        
        "caracteristiques": {
            "Force": 10,
            "Constitution": 10,
            "Agilite": 10,
            "Rapidite": 10,
            "Volonte": 10,
            "Raisonnement": 10,
            "Intuition": 10,
            "Presence": 10
        },
        "competences": {"Athletisme": 5},
        "hp": 42,
        "xp": 0,
        "gold": 0,
        "inventory": [],
        "spells": [],
        "culture_bonuses": {"Endurance": 1}
    }
    (characters_dir / f"{character_id}.json").write_text(json.dumps(character_data), encoding="utf-8")
    response = client.get(f"/api/characters/{character_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == character_id
    assert data["name"] == "Test Hero"
    assert data["race"] == "Humain"
