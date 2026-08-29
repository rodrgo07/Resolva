class ResolvaError(Exception):
    """Base exception for all Resolva errors"""
    pass

class NotFoundError(ResolvaError):
    """Raised when a resource is not found"""
    pass

class ValidationError(ResolvaError):
    """Raised when validation fails"""
    pass

class PermissionError(ResolvaError):
    """Raised when the user lacks permissions"""
    pass

class AutomationSecurityError(ResolvaError):
    """Raised when an automation violates security policies"""
    pass
