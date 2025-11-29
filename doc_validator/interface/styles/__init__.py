# doc_validator/interface/styles/__init__.py
"""
Styling and theming for the AMOSFilter GUI.
"""

from .theme import (
    get_dark_theme_stylesheet,
    get_light_theme_stylesheet,
    get_custom_icons,
)

__all__ = [
    "get_dark_theme_stylesheet",
    "get_light_theme_stylesheet",
    "get_custom_icons",
]