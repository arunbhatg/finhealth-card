"""Base connector and profile loader."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from src.utils.constants import PROFILES_DIR


def load_profile(msme_id: str) -> dict:
    path = PROFILES_DIR / f"{msme_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {msme_id}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class BaseConnector(ABC):
    source_name: str = "base"

    @abstractmethod
    def fetch(self, profile: dict) -> dict:
        pass

    def connect(self, msme_id: str) -> dict:
        profile = load_profile(msme_id)
        return {
            "source": self.source_name,
            "msme_id": msme_id,
            "status": "success",
            "data": self.fetch(profile),
        }
