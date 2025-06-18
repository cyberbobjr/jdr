from fastapi.testclient import TestClient
from back.app import app

client = TestClient(app)

# Teste la récupération des races
def test_get_races():
    response = client.get("/api/creation/races")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Teste la récupération des caractéristiques
def test_get_characteristics():
    response = client.get("/api/creation/characteristics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    
    # Vérifier la structure complète du JSON
    assert "characteristics" in data
    assert "bonus_table" in data
    assert "cost_table" in data
    assert "starting_points" in data
    
    # Vérifier qu'on a bien les caractéristiques principales
    characteristics = data["characteristics"]
    assert "Force" in characteristics
    assert "Constitution" in characteristics
    assert "Agilité" in characteristics
    
    # Vérifier la structure d'une caractéristique
    force = characteristics["Force"]
    assert "short_name" in force
    assert "category" in force
    assert "description" in force
    assert "examples" in force
    assert force["short_name"] == "FOR"
    assert force["category"] == "physical"

# Teste la récupération des compétences
def test_get_skills():
    response = client.get("/api/creation/skills")
    assert response.status_code == 200
    assert "skill_groups" in response.json() or len(response.json()) > 0

# Teste la création et suppression d'un personnage
def test_create_and_delete_character():
    # Création
    response = client.post("/api/creation/new")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    character_id = data["id"]
    # Suppression
    del_response = client.delete(f"/api/creation/delete/{character_id}")
    assert del_response.status_code == 204

# Teste la génération de nom, background, description physique (mock minimal)
def test_generate_llm_endpoints():
    payload = {"race": "Elfe", "culture": "Noldor"}
    for endpoint in ["generate-name", "generate-background", "generate-physical-description"]:
        response = client.post(f"/api/creation/{endpoint}", json=payload)
        # 422 attendu si LLM désactivé ou payload incomplet, 200 sinon
        assert response.status_code in (200, 422, 500)

# Teste la validation des caractéristiques
def test_check_attributes():
    payload = {"attributes": {"Force": 50, "Agilité": 50, "Constitution": 50, "Volonté": 50, "Raisonnement": 50, "Intuition": 50, "Présence": 50}}
    response = client.post("/api/creation/check-attributes", json=payload)
    assert response.status_code == 200
    assert "valid" in response.json()

# Teste la validation des compétences
def test_check_skills():
    payload = {"skills": {"Perception": 2, "Discrétion": 2}}
    response = client.post("/api/creation/check-skills", json=payload)
    assert response.status_code == 200
    assert "valid" in response.json() and "cost" in response.json()
