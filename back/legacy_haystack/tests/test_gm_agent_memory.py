import os
import pytest
from back.agents.gm_agent import build_gm_agent
from haystack.dataclasses import ChatMessage

def test_memory_persistence(tmp_path):
    """
    ### test_memory_persistence
    **Description :** Vérifie que l'historique de l'agent MJ est bien persisté et relu via le store JSONL custom.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker le fichier de session.
    **Retour :** None (assertions sur la persistance).
    """
    session_id = str(tmp_path / "test_session")
    agent = build_gm_agent(session_id=session_id)
    # Simuler une conversation (ajout manuel à l'historique)
    agent._chat_history.append(ChatMessage.from_user("Bonjour"))
    agent._chat_history.append(ChatMessage.from_assistant("Salut aventurier !"))
    agent._store.save(agent._chat_history)
    # Recharger l'agent avec la même session
    agent2 = build_gm_agent(session_id=session_id)
    history = agent2._chat_history
    assert len(history) >= 2
    assert any("Bonjour" in m.text for m in history)
    assert any("Salut aventurier" in m.text for m in history)
    # Nettoyage
    if os.path.exists(f"{session_id}.jsonl"):
        os.remove(f"{session_id}.jsonl")
