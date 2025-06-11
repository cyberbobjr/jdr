"""
Tests unitaires pour le module PROMPT.
"""

import pathlib
from back.agents.PROMPT import (
    build_system_prompt,
    get_scenario_content,
    get_rules_content,
    SYSTEM_PROMPT_TEMPLATE
)


class TestPromptModule:
    """
    ### TestPromptModule
    **Description :** Tests unitaires pour le module PROMPT contenant le template et les fonctions utilitaires.
    """

    def test_system_prompt_template_contains_placeholders(self):
        """
        ### test_system_prompt_template_contains_placeholders
        **Description :** Vérifie que le template contient bien les placeholders nécessaires.
        """
        assert "{scenario_content}" in SYSTEM_PROMPT_TEMPLATE
        assert "{rules_content}" in SYSTEM_PROMPT_TEMPLATE
        assert "Cesse d'être un modèle d'IA" in SYSTEM_PROMPT_TEMPLATE

    def test_get_scenario_content_with_existing_file(self):
        """
        ### test_get_scenario_content_with_existing_file
        **Description :** Teste le chargement d'un fichier de scénario existant.
        """
        # Utiliser le scénario existant
        content = get_scenario_content("Les_Pierres_du_Passe.md")
        assert isinstance(content, str)
        # Le fichier existe, donc le contenu ne devrait pas être vide
        if pathlib.Path("data/scenarios/Les_Pierres_du_Passe.md").exists():
            assert len(content) > 0

    def test_get_scenario_content_with_nonexistent_file(self):
        """
        ### test_get_scenario_content_with_nonexistent_file
        **Description :** Teste le comportement avec un fichier de scénario inexistant.
        """
        content = get_scenario_content("nonexistent_scenario.md")
        assert content == ""

    def test_get_rules_content(self):
        """
        ### test_get_rules_content
        **Description :** Teste le chargement du fichier de règles.
        """
        content = get_rules_content()
        assert isinstance(content, str)
        # Le fichier de règles devrait exister
        if pathlib.Path("data/rules/Regles_Dark_Dungeon.md").exists():
            assert len(content) > 0

    def test_build_system_prompt_replaces_placeholders(self):
        """
        ### test_build_system_prompt_replaces_placeholders
        **Description :** Vérifie que build_system_prompt remplace correctement les placeholders.
        """
        prompt = build_system_prompt("Les_Pierres_du_Passe.md")
        
        # Vérifier que les placeholders ont été remplacés
        assert "{scenario_content}" not in prompt
        assert "{rules_content}" not in prompt
        
        # Vérifier que le contenu de base est présent
        assert "Cesse d'être un modèle d'IA" in prompt
        assert "Tu es RPG-Bot" in prompt

    def test_build_system_prompt_with_nonexistent_scenario(self):
        """
        ### test_build_system_prompt_with_nonexistent_scenario
        **Description :** Teste build_system_prompt avec un scénario inexistant.
        """
        prompt = build_system_prompt("nonexistent_scenario.md")
        
        # Même avec un scénario inexistant, le prompt devrait être construit
        assert "{scenario_content}" not in prompt
        assert "{rules_content}" not in prompt
        assert len(prompt) > 0

    def test_build_system_prompt_returns_string(self):
        """
        ### test_build_system_prompt_returns_string
        **Description :** Vérifie que build_system_prompt retourne bien une chaîne de caractères.
        """
        prompt = build_system_prompt("Les_Pierres_du_Passe.md")
        assert isinstance(prompt, str)
        assert len(prompt) > 1000  # Le prompt devrait être substantiel

    def test_prompt_contains_key_instructions(self):
        """
        ### test_prompt_contains_key_instructions
        **Description :** Vérifie que le prompt contient les instructions clés pour l'agent.
        """
        prompt = build_system_prompt("Les_Pierres_du_Passe.md")
        
        key_instructions = [
            "skill_check_with_character",
            "Responsabilités principales",
            "Interactions",
            "Règles de narration et de jeu",
            "Suivi et contexte"
        ]
        
        for instruction in key_instructions:
            assert instruction in prompt, f"Instruction manquante: {instruction}"
