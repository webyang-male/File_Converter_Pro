"""
templates/ — package grouping the template management of File Converter Pro.

Re-exports public classes so that app.py can continue to write:
    from templates import TemplateManager, EnhancedTemplatesDialog

Author: Hyacinthe
Version: 1.0
"""

from .template_manager import TemplateManager
from .templates import EnhancedTemplatesDialog

__all__ = [
    "TemplateManager",
    "EnhancedTemplatesDialog",
]
