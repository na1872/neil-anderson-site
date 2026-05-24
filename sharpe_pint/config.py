from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    gemini_api_key: str
    section_model: str
    editor_model: str
    section_max_output_tokens: Optional[int]
    editor_max_output_tokens: Optional[int]
    target_firms: str
    project_root: Path


def load_config(project_root: Path) -> AppConfig:
    load_dotenv(project_root / ".env")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and paste your Gemini API key."
        )

    return AppConfig(
        gemini_api_key=api_key,
        section_model=os.getenv("GEMINI_SECTION_MODEL", "gemini-3.5-flash").strip(),
        editor_model=os.getenv("GEMINI_EDITOR_MODEL", "gemini-3.5-flash").strip(),
        section_max_output_tokens=_optional_int("GEMINI_SECTION_MAX_OUTPUT_TOKENS"),
        editor_max_output_tokens=_optional_int("GEMINI_EDITOR_MAX_OUTPUT_TOKENS"),
        target_firms=os.getenv("TARGET_FIRMS", "").strip(),
        project_root=project_root,
    )


def _optional_int(name: str) -> Optional[int]:
    value = os.getenv(name, "").strip()
    return int(value) if value else None
