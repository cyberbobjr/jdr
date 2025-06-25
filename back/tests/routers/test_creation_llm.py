import uuid
import os
import json
import pytest
from back.models.domain.character import Character  # Ajout de l'import pour validation

def make_minimal_character():
    char_id = uuid.uuid4()
    # Exemple d'objet d'inventaire conforme au modèle Item
    inventory_item = {
        "id": "item-1",
        "name": "Coutelas",
        "item_type": "Arme",
        "price_pc": 100,
        "weight_kg": 1.5,
        "description": "Un coutelas tranchant.",
        "category": "Couteau",
        "damage": "1d6+2",
        "protection": None,
        "armor_type": None,
        "quantity": 1,
        "is_equipped": False,
        "crafting_time": None,
        "special_properties": None
    }
    char = {
        "id": str(char_id),
        "name": "Test Nom",
        "race": "Humain",
        "culture": "Rurale",
        
        "caracteristiques": {"Force": 10, "Constitution": 10},
        "competences": {"Athletisme": 5},
        "hp": 42,
        "xp": 0,
        "gold": 0,
        "inventory": [inventory_item],
        "spells": [],
        "equipment_summary": {},
        "culture_bonuses": {},
        "background": None,
        "physical_description": None
    }
    # Validation stricte Pydantic avant retour
    Character.model_validate(char)
    return char

def patch_agent(monkeypatch):
    import types
    async def fake_run(self, prompt):
        print("[MOCK PROMPT]", prompt)
        prompt_l = prompt.lower()
        consigne = prompt_l.strip().split('\n')[-1]
        if "apparence physique" in consigne or "description physique" in consigne or "physique" in consigne:
            return "Une description physique générée."
        if "background" in consigne:
            return "Un background généré."
        if "nom" in consigne:
            return "Test Nom"
        return "MOCK"
    FakeAgent = type('FakeAgent', (), {})
    FakeAgent.run = fake_run
    fake_agent = lambda session_id, character_id=None, scenario_name=None: (FakeAgent(), None)
    monkeypatch.setattr(
        "back.agents.gm_agent_pydantic.build_gm_agent_pydantic",
        fake_agent
    )
    monkeypatch.setattr(
        "back.routers.creation.build_gm_agent_pydantic",
        fake_agent
    )

@pytest.mark.usefixtures("monkeypatch")
def test_generate_character_name(monkeypatch, isolated_data_dir):
    patch_agent(monkeypatch)
    from fastapi.testclient import TestClient
    from back.main import app
    client = TestClient(app)
    character = make_minimal_character()
    char_dir = os.path.join(isolated_data_dir, "characters")
    os.makedirs(char_dir, exist_ok=True)
    # On écrit le JSON avec ensure_ascii=False et forçons l'UUID en string
    with open(os.path.join(char_dir, f"{character['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False)
    # Affichage du contenu du fichier JSON juste avant l'appel API
    with open(os.path.join(char_dir, f"{character['id']}.json"), "r", encoding="utf-8") as f:
        print("[DEBUG] Contenu JSON personnage:", f.read())
    response = client.post("/api/creation/generate-name", json=character)
    if response.status_code != 200:
        print("\n[DEBUG] Response text:", response.text)
    assert response.status_code == 200
    assert "name" in response.json()
    assert response.json()["name"] == "Test Nom"

@pytest.mark.usefixtures("monkeypatch")
def test_generate_character_background(monkeypatch, isolated_data_dir):
    patch_agent(monkeypatch)
    from fastapi.testclient import TestClient
    from back.main import app
    client = TestClient(app)
    character = make_minimal_character()
    char_dir = os.path.join(isolated_data_dir, "characters")
    os.makedirs(char_dir, exist_ok=True)
    with open(os.path.join(char_dir, f"{character['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False)
    response = client.post("/api/creation/generate-background", json=character)
    if response.status_code != 200:
        print("\n[DEBUG] Response text:", response.text)
    assert response.status_code == 200
    assert "background" in response.json()
    assert response.json()["background"] == "Un background généré."

@pytest.mark.usefixtures("monkeypatch")
def test_generate_character_physical_description(monkeypatch, isolated_data_dir):
    patch_agent(monkeypatch)
    from fastapi.testclient import TestClient
    from back.main import app
    client = TestClient(app)
    character = make_minimal_character()
    char_dir = os.path.join(isolated_data_dir, "characters")
    os.makedirs(char_dir, exist_ok=True)
    with open(os.path.join(char_dir, f"{character['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False)
    response = client.post("/api/creation/generate-physical-description", json=character)
    if response.status_code != 200:
        print("\n[DEBUG] Response text:", response.text)
    assert response.status_code == 200
    assert "physical_description" in response.json()
    assert response.json()["physical_description"] == "Une description physique générée."

@pytest.mark.usefixtures("monkeypatch")
def test_generate_character_name_partial(monkeypatch, isolated_data_dir):
    patch_agent(monkeypatch)
    from fastapi.testclient import TestClient
    from back.main import app
    client = TestClient(app)
    character = make_minimal_character()
    char_dir = os.path.join(isolated_data_dir, "characters")
    os.makedirs(char_dir, exist_ok=True)
    with open(os.path.join(char_dir, f"{character['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False)
    # Affichage du contenu du fichier JSON juste avant l'appel API
    with open(os.path.join(char_dir, f"{character['id']}.json"), "r", encoding="utf-8") as f:
        print("[DEBUG] Contenu JSON personnage:", f.read())
    partial = {"id": character["id"], "race": "Elfe"}
    response = client.post("/api/creation/generate-name", json=partial)
    if response.status_code != 200:
        print("\n[DEBUG] Response text:", response.text)
    assert response.status_code == 200
    assert "name" in response.json()
    assert response.json()["name"] == "Test Nom"

@pytest.mark.usefixtures("monkeypatch")
def test_generate_character_background_partial(monkeypatch, isolated_data_dir):
    patch_agent(monkeypatch)
    from fastapi.testclient import TestClient
    from back.main import app
    client = TestClient(app)
    character = make_minimal_character()
    char_dir = os.path.join(isolated_data_dir, "characters")
    os.makedirs(char_dir, exist_ok=True)
    with open(os.path.join(char_dir, f"{character['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False)
    partial = {"id": character["id"], "race": "Nain", }
    response = client.post("/api/creation/generate-background", json=partial)
    if response.status_code != 200:
        print("\n[DEBUG] Response text:", response.text)
    assert response.status_code == 200
    assert "background" in response.json()
    assert response.json()["background"] == "Un background généré."

@pytest.mark.usefixtures("monkeypatch")
def test_generate_character_physical_description_partial(monkeypatch, isolated_data_dir):
    patch_agent(monkeypatch)
    from fastapi.testclient import TestClient
    from back.main import app
    client = TestClient(app)
    character = make_minimal_character()
    char_dir = os.path.join(isolated_data_dir, "characters")
    os.makedirs(char_dir, exist_ok=True)
    with open(os.path.join(char_dir, f"{character['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False)
    partial = {"id": character["id"], "race": "Hobbit"}
    response = client.post("/api/creation/generate-physical-description", json=partial)
    if response.status_code != 200:
        print("\n[DEBUG] Response text:", response.text)
    assert response.status_code == 200
    assert "physical_description" in response.json()
    assert response.json()["physical_description"] == "Une description physique générée."
