from back.routers.scenarios import normalize_json_history

# Exemple d'historique JSON brut (reprend l'exemple fourni)
EXAMPLE_HISTORY = [
    {
        "parts": [
            {
                "content": "[Contexte du personnage:\n...je regarde la fontaine",
                "timestamp": "2025-06-09T10:04:39.378072Z",
                "part_kind": "user-prompt"
            }
        ],
        "instructions": None,
        "kind": "request"
    },
    {
        "parts": [
            {
                "content": "**Esgalbar, place centrale du village** ...",
                "part_kind": "text"
            }
        ],
        "usage": {
            "requests": 1,
            "request_tokens": 3701,
            "response_tokens": 422,
            "total_tokens": 4123,
            "details": {"cached_tokens": 3328}
        },
        "model_name": "deepseek-chat",
        "timestamp": "2025-06-09T10:04:41Z",
        "kind": "response",
        "vendor_details": None,
        "vendor_id": "1a42e012-8ad8-4403-867f-5a6ef1e79392"
    },
    {
        "parts": [
            {
                "content": "[Contexte du personnage:\n...j'examine la fontaine",
                "timestamp": "2025-06-09T17:50:53.234253Z",
                "part_kind": "user-prompt"
            }
        ],
        "instructions": None,
        "kind": "request"
    },
    {
        "parts": [
            {
                "content": "",
                "part_kind": "text"
            },
            {
                "tool_name": "skill_check_with_character",
                "args": "{\"skill_name\":\"Raisonnement\",\"difficulty_name\":\"Moyenne\"}",
                "tool_call_id": "call_0_3c853af2-dfd5-4b05-9bb7-bb1719618a79",
                "part_kind": "tool-call"
            }
        ],
        "usage": {
            "requests": 1,
            "request_tokens": 6362,
            "response_tokens": 32,
            "total_tokens": 6394,
            "details": {"cached_tokens": 2944}
        },
        "model_name": "deepseek-chat",
        "timestamp": "2025-06-09T17:50:55Z",
        "kind": "response",
        "vendor_details": None,
        "vendor_id": "7d0b1324-75de-4146-984c-6eb2c3dfca80"
    },
    {
        "parts": [
            {
                "tool_name": "skill_check_with_character",
                "content": "Test de Raisonnement: ...",
                "tool_call_id": "call_0_3c853af2-dfd5-4b05-9bb7-bb1719618a79",
                "timestamp": "2025-06-09T17:51:00.149043Z",
                "part_kind": "tool-return"
            }
        ],
        "instructions": None,
        "kind": "request"
    },
    {
        "parts": [
            {
                "content": "**Examen des inscriptions sur la fontaine** ...",
                "part_kind": "text"
            }
        ],
        "usage": {
            "requests": 1,
            "request_tokens": 6447,
            "response_tokens": 480,
            "total_tokens": 6927,
            "details": {"cached_tokens": 6336}
        },
        "model_name": "deepseek-chat",
        "timestamp": "2025-06-09T17:51:00Z",
        "kind": "response",
        "vendor_details": None,
        "vendor_id": "ea4adb5c-91de-4ebf-ab76-99fcfe3095f1"
    }
]

def test_normalize_json_history_simple():
    """
    Vérifie que la fonction normalize_json_history complète bien les champs manquants (timestamp, content, part_kind) sur un exemple brut.
    """
    normalized = normalize_json_history(EXAMPLE_HISTORY)
    for msg in normalized:
        assert isinstance(msg["parts"], list)
        for part in msg["parts"]:
            assert "content" in part
            assert "timestamp" in part
            assert "part_kind" in part
            assert isinstance(part["content"], str)
            assert isinstance(part["timestamp"], str)
            assert isinstance(part["part_kind"], str)
