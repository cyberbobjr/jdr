"""
Exceptions HTTP standardisées pour l'API.
Centralise la gestion des erreurs avec des codes HTTP cohérents.
"""

from fastapi import HTTPException
from typing import Optional


class CharacterNotFoundError(HTTPException):
    """
    Exception levée lorsqu'un personnage n'est pas trouvé.
    """
    def __init__(self, character_id: str):
        super().__init__(status_code=404, detail=f"Personnage {character_id} non trouvé")


class SessionNotFoundError(HTTPException):
    """
    Exception levée lorsqu'une session n'est pas trouvée.
    """
    def __init__(self, session_id: str):
        super().__init__(status_code=404, detail=f"Session {session_id} non trouvée")


class ValidationError(HTTPException):
    """
    Exception levée pour les erreurs de validation.
    """
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class BusinessLogicError(HTTPException):
    """
    Exception levée pour les erreurs de logique métier.
    """
    def __init__(self, detail: str, error_code: Optional[str] = None):
        detail_msg = detail
        if error_code:
            detail_msg = f"[{error_code}] {detail}"
        super().__init__(status_code=400, detail=detail_msg)


class InsufficientFundsError(BusinessLogicError):
    """
    Exception levée lorsqu'un personnage n'a pas assez d'argent.
    """
    def __init__(self, current_gold: float, required_gold: float):
        detail = f"Pas assez d'argent. Actuel: {current_gold}, Requis: {required_gold}"
        super().__init__(detail, "INSUFFICIENT_FUNDS")


class ItemNotFoundError(BusinessLogicError):
    """
    Exception levée lorsqu'un objet n'est pas trouvé.
    """
    def __init__(self, item_id: str):
        detail = f"Objet {item_id} non trouvé"
        super().__init__(detail, "ITEM_NOT_FOUND")


class EquipmentNotFoundError(BusinessLogicError):
    """
    Exception levée lorsqu'un équipement n'est pas trouvé.
    """
    def __init__(self, equipment_name: str):
        detail = f"Équipement {equipment_name} non trouvé"
        super().__init__(detail, "EQUIPMENT_NOT_FOUND")


class InternalServerError(HTTPException):
    """
    Exception levée pour les erreurs internes du serveur.
    """
    def __init__(self, detail: str = "Erreur interne du serveur"):
        super().__init__(status_code=500, detail=detail)
