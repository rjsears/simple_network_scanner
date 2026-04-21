"""Preset management for scan configurations"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Preset:
    name: str
    start_ip: str
    host_count: str
    cidr: str


class PresetManager:
    """Manages saved scan presets."""

    def __init__(self):
        self._config_dir = Path.home() / ".config" / "network-scanner"
        self._presets_file = self._config_dir / "presets.json"
        self._presets: dict[str, Preset] = {}
        self._load()

    def _load(self):
        """Load presets from disk."""
        if not self._presets_file.exists():
            return

        try:
            with open(self._presets_file) as f:
                data = json.load(f)

            self._presets = {}
            for name, values in data.items():
                self._presets[name] = Preset(
                    name=name,
                    start_ip=values.get("start_ip", ""),
                    host_count=values.get("host_count", ""),
                    cidr=values.get("cidr", "")
                )
        except Exception:
            self._presets = {}

    def _save_to_disk(self):
        """Save presets to disk."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

        data = {}
        for name, preset in self._presets.items():
            data[name] = {
                "start_ip": preset.start_ip,
                "host_count": preset.host_count,
                "cidr": preset.cidr
            }

        with open(self._presets_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_all(self) -> List[Preset]:
        """Get all presets."""
        return list(self._presets.values())

    def get(self, name: str) -> Optional[Preset]:
        """Get a preset by name."""
        return self._presets.get(name)

    def save(self, preset: Preset):
        """Save or update a preset."""
        self._presets[preset.name] = preset
        self._save_to_disk()

    def delete(self, name: str):
        """Delete a preset by name."""
        if name in self._presets:
            del self._presets[name]
            self._save_to_disk()
