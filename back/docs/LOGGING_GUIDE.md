# Guide d'utilisation du système de logging

## Vue d'ensemble

Le système de logging du projet JdR "Terres du Milieu" est conçu pour fournir une observabilité complète des opérations, faciliter le débogage et permettre l'intégration avec des outils de monitoring comme Grafana/Loki.

## Architecture

### Configuration centralisée
- **Fichier** : `back/config.yaml`
- **Classe** : `Config` dans `back/config.py`
- **Format** : JSON structuré avec timestamps ISO

### Modules principaux
- `back/config.py` : Configuration et gestion des loggers
- `back/utils/logger.py` : Fonctions de logging spécialisées

## Configuration

### Fichier config.yaml
```yaml
logging:
  level: "INFO"                    # Niveau global (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  format: "json"                   # Format JSON ou texte
  file: null                       # Chemin du fichier (null = console uniquement)
  max_file_size: 10485760          # Taille max en octets (10MB)
  backup_count: 5                  # Nombre de fichiers de backup
  debug_enabled: false             # Flag debug supplémentaire
```

### Variables d'environnement
```bash
# Niveau de log (surcharge la config)
LOG_LEVEL=DEBUG

# Fichier de log (surcharge la config)
LOG_FILE=/var/log/jdr/app.log

# Debug activé
DEBUG=true
```

## Utilisation de base

### Obtenir un logger
```python
from back.config import get_logger

# Logger pour le module courant
logger = get_logger(__name__)

# Logger nommé
logger = get_logger("mon_module")
```

### Niveaux de logging
```python
# Debug - Informations détaillées pour le développement
logger.debug("Détails techniques", variable=value, context="info")

# Info - Informations générales sur le fonctionnement
logger.info("Opération réussie", action="create", id="123")

# Warning - Situations potentiellement problématiques
logger.warning("Configuration manquante", config_key="api_key")

# Error - Erreurs qui ne bloquent pas l'exécution
logger.error("Échec de connexion", error=str(e), retry_count=3)

# Critical - Erreurs graves nécessitant une intervention
logger.critical("Service indisponible", service="database")
```

## Fonctions spécialisées

### Logging métier (back/utils/logger.py)
```python
from back.utils.logger import log_debug, log_info, log_error, log_warning

# Logging avec contexte métier
log_debug("Chargement du personnage",
          character_id="123",
          action="load_character",
          status="success")

log_info("Personnage créé",
         character_name="Aragorn",
         race="Humain",
         action="character_creation")

log_error("Échec de validation",
          error="Invalid race",
          character_id="123",
          action="validation_error")
```

## Bonnes pratiques

### 1. Choix du niveau approprié
- **DEBUG** : Informations pour les développeurs (variables, états internes)
- **INFO** : Événements métier importants (création, modification, succès)
- **WARNING** : Situations anormales mais non bloquantes
- **ERROR** : Erreurs qui affectent une opération spécifique
- **CRITICAL** : Erreurs qui affectent le système entier

### 2. Contexte et métadonnées
```python
# ✅ BON : Contexte riche
logger.info("Personnage sauvegardé",
           character_id="123",
           character_name="Aragorn",
           action="save_character",
           file_size=2048)

# ❌ MAUVAIS : Contexte pauvre
logger.info("Sauvegarde réussie")
```

### 3. Gestion des erreurs
```python
try:
    # Opération risquée
    result = risky_operation()
    logger.info("Opération réussie", result=result)
except Exception as e:
    logger.error("Échec de l'opération",
                error=str(e),
                error_type=type(e).__name__,
                context="operation_details")
    raise
```

### 4. Performance
```python
# ✅ BON : Évaluation lazy des messages coûteux
logger.debug("Données détaillées: %s", expensive_debug_data())

# ❌ MAUVAIS : Évaluation toujours faite
logger.debug(f"Données détaillées: {expensive_debug_data()}")
```

## Intégration dans le code existant

### Ajout de logging à une méthode existante
```python
def create_character(self, character_data: dict) -> Character:
    """Crée un nouveau personnage."""
    logger = get_logger(__name__)

    logger.info("Début création personnage",
               character_name=character_data.get("name"),
               race=character_data.get("race"))

    try:
        # Logique existante
        character = Character(**character_data)

        logger.info("Personnage créé avec succès",
                   character_id=str(character.id),
                   action="character_created")

        return character

    except Exception as e:
        logger.error("Échec création personnage",
                    error=str(e),
                    character_data=character_data)
        raise
```

### Migration depuis l'ancien système
```python
# Ancien système
from back.utils.logger import log_debug
log_debug("Message", key="value")

# Nouveau système
from back.config import get_logger
logger = get_logger(__name__)
logger.debug("Message", extra={"key": "value"})
```

## Monitoring et observabilité

### Format JSON pour Grafana/Loki
```json
{
  "timestamp": "2025-10-25T12:30:45.123456Z",
  "level": "INFO",
  "logger": "back.services.character_service",
  "message": "Personnage créé avec succès",
  "character_id": "123",
  "character_name": "Aragorn",
  "action": "character_created"
}
```

### Requêtes Loki utiles
```
# Erreurs des dernières 24h
{level="ERROR"} |= "character" | json | line_format "{{.timestamp}} {{.logger}} {{.message}}"

# Créations de personnages réussies
{level="INFO", action="character_created"} | json | line_format "Personnage {{.character_name}} créé (ID: {{.character_id}})"
```

## Tests du système de logging

### Test unitaire basique
```python
import pytest
from back.config import get_logger

def test_logger_configuration():
    """Test que le logger est correctement configuré."""
    logger = get_logger("test_module")

    # Vérifier que c'est un logger Python standard
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'debug')

    # Test de logging (vérifier qu'aucune exception n'est levée)
    logger.info("Test message", test_key="test_value")
```

### Test d'intégration
```python
def test_logging_with_context():
    """Test du logging avec contexte métier."""
    from back.services.character_service import CharacterService

    # Créer un personnage de test
    service = CharacterService("test_id")

    # L'appel devrait générer des logs appropriés
    # (Vérifier via un handler de test ou les fichiers de log)
```

## Dépannage

### Problèmes courants

#### 1. Logs qui n'apparaissent pas
```python
# Vérifier le niveau de log
from back.config import config
print("Niveau de log:", config.get_logging_config()["level"])

# Forcer un message de test
logger = get_logger("debug")
logger.info("Test de visibilité")
```

#### 2. Format JSON mal formé
```python
# Vérifier la configuration
config = config.get_logging_config()
print("Format:", config["format"])  # Doit être "json"
```

#### 3. Fichier de log non créé
```python
# Vérifier les permissions
import os
log_file = config.get_logging_config().get("file")
if log_file:
    print("Répertoire accessible:", os.access(os.path.dirname(log_file), os.W_OK))
```

## Références

- [Documentation Python Logging](https://docs.python.org/3/library/logging.html)
- [PydanticAI Logging](https://ai.pydantic.dev/logging/)
- [Grafana Loki Query Language](https://grafana.com/docs/loki/latest/logql/)