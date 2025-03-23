class ToolsGetError(Exception):
    """Base exception class for Tools Get"""
    pass

class DependencyError(ToolsGetError):
    """Raised when a required dependency is missing"""
    pass

class InstallationError(ToolsGetError):
    """Raised when installation fails"""
    pass

class ConfigError(ToolsGetError):
    """Raised when configuration is invalid"""
    pass

class PolicyKitError(ToolsGetError):
    """Raised when PolicyKit authentication fails"""
    pass
