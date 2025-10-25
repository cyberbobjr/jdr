"""
Tests pour le système de logging du projet JdR.
"""

import json
import logging
import tempfile
import os
from pathlib import Path

from back.config import Config, get_logger
from back.utils.logger import log_debug


class TestLoggingSystem:
    """Tests du système de logging centralisé."""

    def test_config_logging_initialization(self):
        """Test que la configuration de logging s'initialise correctement."""
        config = Config()

        # Vérifier que la configuration de logging existe
        logging_config = config.get_logging_config()
        assert isinstance(logging_config, dict)
        assert "level" in logging_config
        assert "format" in logging_config

    def test_logger_creation(self):
        """Test que les loggers sont créés correctement."""
        logger = get_logger("test_module")

        # Vérifier que c'est un logger Python standard
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')

    def test_json_format_logging(self, capsys):
        """Test que les logs sont formatés en JSON."""
        logger = get_logger("test_json")

        # Logger un message
        logger.info("Test message", extra={"action": "test", "user_id": "123"})

        # Capturer la sortie
        captured = capsys.readouterr()

        # Vérifier que c'est du JSON valide
        log_line = captured.out.strip()
        assert log_line.startswith('{')

        log_data = json.loads(log_line)

        # Vérifier la structure JSON
        assert "timestamp" in log_data
        assert "level" in log_data
        assert "logger" in log_data
        assert "message" in log_data
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_json"
        assert log_data["message"] == "Test message"
        assert log_data["action"] == "test"
        assert log_data["user_id"] == "123"

    def test_log_levels(self, capsys):
        """Test que les différents niveaux de log fonctionnent."""
        logger = get_logger("test_levels")

        # Logger différents niveaux
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        captured = capsys.readouterr()
        log_lines = captured.out.strip().split('\n')

        # Compter les messages (devrait être 5 si DEBUG est activé, sinon 4)
        json_lines = [line for line in log_lines if line.startswith('{')]
        assert len(json_lines) >= 4  # Au moins INFO, WARNING, ERROR, CRITICAL

        # Vérifier les niveaux
        levels = []
        for line in json_lines:
            if line:
                data = json.loads(line)
                levels.append(data["level"])

        assert "INFO" in levels
        assert "WARNING" in levels
        assert "ERROR" in levels
        assert "CRITICAL" in levels

    def test_file_logging(self):
        """Test que les logs peuvent être écrits dans un fichier."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as temp_file:
            temp_path = temp_file.name

        try:
            # Créer une config temporaire avec fichier
            config_content = f"""
logging:
  level: "INFO"
  format: "json"
  file: "{temp_path}"
  max_file_size: 1048576
  backup_count: 3
"""

            config_file = Path(tempfile.gettempdir()) / "test_config.yaml"
            config_file.write_text(config_content)

            # Créer config avec ce fichier
            config = Config(str(config_file))

            # Obtenir logger et logger un message
            logger = config.get_logger("test_file")
            logger.info("Test file logging", extra={"test": "value"})

            # Vérifier que le fichier a été créé et contient le log
            assert Path(temp_path).exists()

            with open(temp_path, 'r') as f:
                content = f.read()
                assert content.strip()
                log_data = json.loads(content.strip())
                assert log_data["message"] == "Test file logging"
                assert log_data["test"] == "value"

        finally:
            # Nettoyage
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if config_file.exists():
                config_file.unlink()

    def test_legacy_logging_functions(self, capsys):
        """Test que les fonctions de logging legacy fonctionnent."""
        # Test log_debug
        log_debug("Legacy debug message", action="legacy_test", value=42)

        captured = capsys.readouterr()
        log_line = captured.out.strip()

        assert log_line.startswith('{')
        log_data = json.loads(log_line)
        assert log_data["message"] == "Legacy debug message"
        assert log_data["level"] == "DEBUG"
        assert log_data["action"] == "legacy_test"
        assert log_data["value"] == 42

    def test_error_logging(self, capsys):
        """Test du logging d'erreurs."""
        logger = get_logger("test_error")

        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error("Exception capturée", error=str(e), exception_type=type(e).__name__)

        captured = capsys.readouterr()
        log_line = captured.out.strip()

        log_data = json.loads(log_line)
        assert log_data["level"] == "ERROR"
        assert "Test error" in log_data["error"]
        assert log_data["exception_type"] == "ValueError"

    def test_business_context_logging(self, capsys):
        """Test du logging avec contexte métier."""
        from back.utils.logger import log_info

        log_info("Personnage créé",
                character_id="123",
                character_name="Aragorn",
                race="Humain",
                action="character_creation")

        captured = capsys.readouterr()
        log_line = captured.out.strip()

        log_data = json.loads(log_line)
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Personnage créé"
        assert log_data["character_id"] == "123"
        assert log_data["character_name"] == "Aragorn"
        assert log_data["race"] == "Humain"
        assert log_data["action"] == "character_creation"


class TestLoggingConfiguration:
    """Tests de la configuration du logging."""

    def test_config_file_not_found(self):
        """Test que Config gère correctement un fichier manquant."""
        with pytest.raises(FileNotFoundError):
            Config("nonexistent_config.yaml")

    def test_invalid_yaml_config(self):
        """Test que Config gère correctement un YAML invalide."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            temp_file.write("invalid: yaml: content: [\n")
            temp_path = temp_file.name

        try:
            with pytest.raises(ValueError):
                Config(temp_path)
        finally:
            os.unlink(temp_path)

    def test_default_config_values(self):
        """Test que les valeurs par défaut sont correctement définies."""
        config = Config()

        logging_config = config.get_logging_config()

        # Vérifier les valeurs par défaut
        assert logging_config["level"] == "INFO"
        assert logging_config["format"] == "json"
        assert logging_config["file"] is None
        assert logging_config["max_file_size"] == 10 * 1024 * 1024  # 10MB
        assert logging_config["backup_count"] == 5


class TestLoggingIntegration:
    """Tests d'intégration du système de logging."""

    def test_multiple_loggers(self, capsys):
        """Test que plusieurs loggers peuvent coexister."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        logger1.info("Message from module1", module="1")
        logger2.info("Message from module2", module="2")

        captured = capsys.readouterr()
        log_lines = captured.out.strip().split('\n')

        json_lines = [json.loads(line) for line in log_lines if line.startswith('{')]

        # Vérifier qu'on a 2 messages
        assert len(json_lines) == 2

        # Vérifier les loggers
        loggers = [data["logger"] for data in json_lines]
        assert "module1" in loggers
        assert "module2" in loggers

    def test_log_filtering_by_level(self):
        """Test que le filtrage par niveau fonctionne."""
        # Ce test nécessiterait de modifier temporairement le niveau de log
        # et de vérifier que seuls les messages appropriés passent
        # Pour l'instant, on se contente de vérifier que les niveaux existent
        logger = get_logger("test_filtering")

        assert hasattr(logger, 'setLevel')
        assert hasattr(logger, 'getEffectiveLevel')

    def test_timestamp_format(self, capsys):
        """Test que les timestamps sont au bon format."""
        import re

        logger = get_logger("test_timestamp")
        logger.info("Test timestamp")

        captured = capsys.readouterr()
        log_line = captured.out.strip()

        log_data = json.loads(log_line)

        # Vérifier le format ISO avec microsecondes et Z
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$'
        assert re.match(timestamp_pattern, log_data["timestamp"])