"""
Tests unitaires pour le PydanticJsonlStore.
Validation de la compatibilité avec l'agent PydanticAI.
"""

import tempfile
import os
from pydantic_ai.messages import ModelRequest, TextPart, ModelMessagesTypeAdapter
from back.storage.pydantic_jsonl_store import PydanticJsonlStore


class TestPydanticJsonlStore:
    """
    ### TestPydanticJsonlStore
    **Description :** Tests unitaires pour la classe PydanticJsonlStore (API PydanticAI uniquement).
    """

    def test_load_realistic_json_history(self):
        """
        ### test_load_realistic_json_history
        **Description :** Teste le chargement d'un historique JSON réaliste (exemple fourni) via load_pydantic_history.
        """
        import json
        example_json = [
            {"parts": [
                {"content": "Exemple de prompt système.", "part_kind": "system-prompt"}
            ], "timestamp": "2025-06-09T09:30:34.839940Z", "kind": "request"},
            {"parts": [
                {"content": "Exemple de réponse MJ.", "part_kind": "text"}
            ], "timestamp": "2025-06-09T09:30:35Z", "kind": "response"}
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_realistic.jsonl")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(example_json, f, ensure_ascii=False, indent=2)
            store = PydanticJsonlStore(filepath)
            loaded = store.load_pydantic_history()
            assert len(loaded) == 2
            assert loaded[0].parts[0].content == "Exemple de prompt système."
            assert loaded[1].parts[0].content == "Exemple de réponse MJ."
            # Vérifie que les objets sont bien des ModelRequest/ModelResponse
            from pydantic_ai.messages import ModelRequest, ModelResponse
            assert isinstance(loaded[0], ModelRequest) or isinstance(loaded[0], ModelResponse)
            assert isinstance(loaded[1], ModelRequest) or isinstance(loaded[1], ModelResponse)

    def test_save_and_load_pydantic_history(self):
        """
        ### test_save_and_load_pydantic_history
        **Description :** Teste la sauvegarde et le rechargement d'un historique de messages PydanticAI à partir d'un exemple JSON fourni, en utilisant validate_python.
        """
        import json
        from pydantic_ai.messages import ModelMessagesTypeAdapter
        # Exemple JSON fourni (copié/collé)
        example_json = [
            {"parts": [
                {"content": "[Contexte du personnage:\n\"{\\\"id\\\":\\\"79e55c14-7dd5-4189-b209-ea88f6d067eb\\\",\\\"name\\\":\\\"Galadhwen\\\",\\\"race\\\":\\\"Elfe Sylvain\\\",\\\"culture\\\":\\\"Rurale\\\",\\\"profession\\\":\\\"Aventurier\\\",\\\"caracteristiques\\\":{\\\"Force\\\":69,\\\"Constitution\\\":69,\\\"Agilit\u00e9\\\":69,\\\"Rapidité\\\":69,\\\"Volonté\\\":69,\\\"Raisonnement\\\":69,\\\"Intuition\\\":68,\\\"Présence\\\":68},\\\"competences\\\":{\\\"Comédie\\\":21},\\\"hp\\\":102,\\\"inventory\\\":[],\\\"equipment\\\":[\\\"Bandoulière\\\",\\\"Coutelas\\\",\\\"Bottes de cuir\\\",\\\"Gants de cuir\\\",\\\"Tenue de voyage\\\",\\\"Aiguille à coudre\\\"],\\\"spells\\\":[\\\"Voies du Verrouillage\\\",\\\"Teintes\\\",\\\"Accrochage\\\"],\\\"equipment_summary\\\":{\\\"total_cost\\\":4.8,\\\"total_weight\\\":5.2,\\\"remaining_money\\\":15.2,\\\"starting_money\\\":20.0},\\\"culture_bonuses\\\":{\\\"Artisanat\\\":3,\\\"Endurance\\\":1,\\\"Soins\\\":1,\\\"Herboristerie\\\":1,\\\"Connaissance Générale\\\":2,\\\"Équitation\\\":1,\\\"Natation\\\":2}}\"\n]\n\nje regarde la fontaine",
                 "timestamp": "2025-06-09T10:04:39.378072Z",
                 "part_kind": "user-prompt"}
            ],
            "instructions": None,
            "kind": "request"
            },
            {"parts": [
                {"content": "**Esgalbar, place centrale du village**  \n\n*Le soleil décline lentement à l'horizon, teintant le ciel de nuances orangées. Une brume légère flotte autour de la fontaine sèche, comme si elle retenait les souvenirs d'un temps où l'eau y coulait en abondance. Les pierres de la fontaine, autrefois ornées de motifs élégants, sont maintenant usées par les siècles et les intempéries. Quelques feuilles mortes s'accumulent dans son bassin vide, et un silence pesant règne sur la place, troublé seulement par le murmure du vent dans les branches des arbres environnants.*  \n\n**Points d'intérêt :**  \n- **La fontaine** : Son bassin est vide, mais des inscriptions à moitié effacées sont visibles sur son rebord. Elles semblent être en sindarin, la langue des Elfes.  \n- **Les alentours** : Quelques villageois pressent le pas, évitant de s'attarder près de la fontaine, comme si elle portait une malédiction.  \n\n**Actions possibles :**  \n1. **Examiner les inscriptions sur la fontaine** pour tenter de les déchiffrer. [Jet de dés : Raisonnement]  \n2. **Demander à un villageois** pourquoi la fontaine est abandonnée. [Jet de dés : Présence]  \n3. **Fouiller le bassin** pour voir s'il y a quelque chose de caché. [Jet de dés : Intuition]  \n4. **Utiliser un sort** pour tenter de réactiver la fontaine ou de comprendre son histoire. [Jet de dés : Volonté]  \n5. **Ignorer la fontaine et se diriger vers les ruines d'Arnor**, intrigué par les rumeurs de disparitions.  \n\n*Que choisissez-vous, Galadhwen ?*",
                 "part_kind": "text"}
            ],
            "usage": {"requests": 1, "request_tokens": 3701, "response_tokens": 422, "total_tokens": 4123, "details": {"cached_tokens": 3328}},
            "model_name": "deepseek-chat",
            "timestamp": "2025-06-09T10:04:41Z",
            "kind": "response",
            "vendor_details": None,
            "vendor_id": "1a42e012-8ad8-4403-867f-5a6ef1e79392"
            }
        ]
        # Désérialisation via validate_python
        historique = ModelMessagesTypeAdapter.validate_python(example_json)
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            store.save_pydantic_history(historique)
            loaded = store.load_pydantic_history()
            assert len(loaded) == 2
            assert loaded[0].parts[0].content.startswith("[Contexte du personnage:")
            assert loaded[1].parts[0].content.startswith("**Esgalbar, place centrale du village**")

    def test_save_overwrites_file(self):
        """
        ### test_save_overwrites_file
        **Description :** Teste que la sauvegarde écrase bien le fichier précédent.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            historique1 = [ModelRequest(parts=[TextPart(content="msg1", part_kind="user-prompt")])]
            store.save_pydantic_history(historique1)
            historique2 = [ModelRequest(parts=[TextPart(content="msg2", part_kind="user-prompt")])]
            store.save_pydantic_history(historique2)
            loaded = store.load_pydantic_history()
            assert len(loaded) == 1
            assert loaded[0].parts[0].content == "msg2"

    def test_load_empty_file(self):
        """
        ### test_load_empty_file
        **Description :** Teste le chargement d'un fichier vide (doit retourner une liste vide).
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            # Fichier vide
            loaded = store.load_pydantic_history()
            assert loaded == []

    def test_save_and_load_json_direct(self):
        """
        ### test_save_and_load_json_direct
        **Description :** Teste la sérialisation/désérialisation directe via to_jsonable_python/validate_python.
        """
        historique = [
            ModelRequest(parts=[TextPart(content="test direct", part_kind="user-prompt")]),
        ]
        from pydantic_core import to_jsonable_python
        historique_jsonable = to_jsonable_python(historique)
        reloaded = ModelMessagesTypeAdapter.validate_python(historique_jsonable)
        assert len(reloaded) == 1
        assert isinstance(reloaded[0], ModelRequest)
        assert reloaded[0].parts[0].content == "test direct"
