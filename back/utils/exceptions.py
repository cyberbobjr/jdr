"""
Custom exceptions for the JdR project.
"""

class JdrError(Exception):
    """Base class for all JdR exceptions."""
    pass

class ServiceNotInitializedError(JdrError):
    """Raised when a service is accessed but not initialized."""
    pass

class SessionNotFoundError(JdrError):
    """Raised when a session cannot be found."""
    pass

class CharacterNotFoundError(JdrError):
    """Raised when a character cannot be found."""
    pass

class CharacterInvalidStateError(JdrError):
    """Raised when a character is in an invalid state (e.g. draft)."""
    pass

class InternalServerError(JdrError):
    """Raised when an unexpected error occurs."""
    pass
