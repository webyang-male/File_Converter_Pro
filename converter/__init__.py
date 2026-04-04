"""
converter/ — Advanced Conversion Engine for File Converter Pro

Exports:
    AdvancedDatabaseManager  : SQLite database for advanced conversions
    AdvancedConverterEngine  : Real conversion implementations

Author: Hyacinthe
Version: 1.0
"""

from .advanced_db import AdvancedDatabaseManager
from .converters  import AdvancedConverterEngine

__all__ = ["AdvancedDatabaseManager", "AdvancedConverterEngine"]
