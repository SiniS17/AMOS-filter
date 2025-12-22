# doc_validator/interface/settings_manager.py
"""
Settings Manager with JSON persistence.
Handles saving/loading all user preferences.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class SettingsManager:
    """Manages application settings with JSON persistence."""

    DEFAULT_SETTINGS = {
        # Input source settings
        "input_source_type": "local",  # "local" or "drive"
        "input_local_path": "",  # Will be set to default INPUT folder

        # SEQ auto-valid patterns
        "seq_auto_valid_patterns": ["1.", "2.", "3.", "10."],

        # Date filter
        "date_filter_enabled": False,
        "date_filter_start": "",
        "date_filter_end": "",

        # Processing options
        "action_step_control_enabled": True,  # Always enabled now, but kept for future
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize settings manager.

        Args:
            config_path: Path to settings file. If None, uses default location.
        """
        if config_path is None:
            # Store settings in user's home directory
            config_dir = Path.home() / ".amos_validator"
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / "settings.json"
        else:
            self.config_path = Path(config_path)

        self._settings: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load settings from file. Uses defaults if file doesn't exist."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    self._settings = {**self.DEFAULT_SETTINGS, **loaded}
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
                print("Using default settings")
                self._settings = self.DEFAULT_SETTINGS.copy()
        else:
            self._settings = self.DEFAULT_SETTINGS.copy()

    def save(self) -> None:
        """Save current settings to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save."""
        self._settings[key] = value
        self.save()

    def get_all(self) -> Dict[str, Any]:
        """Get all settings as a dictionary."""
        return self._settings.copy()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self.DEFAULT_SETTINGS.copy()
        self.save()