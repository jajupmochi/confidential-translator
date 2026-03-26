import os
from pathlib import Path
from app.core.config import settings

class SettingsService:
    """Service to manage and persist application settings."""

    def __init__(self):
        # Determine the .env file path
        # In source mode: root/backend/.env or root/.env?
        # main.py adds parent.parent to sys.path, so root is two levels up from main.py.
        # config.py is in backend/app/core/config.py
        # Let's use the directory where main.py resides as a base for standalone,
        # or project root for source.
        
        self.env_path = Path(".env")
        if not self.env_path.exists():
            # Try to find it relative to this file
            self.env_path = Path(__file__).parent.parent.parent / ".env"

    def get_settings(self):
        """Get current settings."""
        return {
            "ollama_models_path": settings.ollama_models_path
        }

    def update_settings(self, new_settings: dict):
        """Update settings and persist to .env file."""
        if "ollama_models_path" in new_settings:
            path = new_settings["ollama_models_path"]
            old_path = settings.ollama_models_path
            
            if path != old_path:
                settings.ollama_models_path = path
                self._update_env_file("CT_OLLAMA_MODELS_PATH", path)
                
                # Restart Ollama to pick up new path
                from app.services.ollama_service import ollama_service
                ollama_service.stop_server()
                ollama_service.start_server()
        return self.get_settings()

    def _update_env_file(self, key: str, value: str):
        """Update or add a key-value pair in the .env file."""
        lines = []
        if self.env_path.exists():
            with open(self.env_path, "r") as f:
                lines = f.readlines()

        found = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}=\"{value}\"\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{key}=\"{value}\"\n")

        with open(self.env_path, "w") as f:
            f.writelines(new_lines)

settings_service = SettingsService()
