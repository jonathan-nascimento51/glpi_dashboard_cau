from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PromptConfig:
    """Configuration for prompt generation and caching."""

    prompts_dir: Path = Path("prompts")
    default_models: dict[str, str] = field(
        default_factory=lambda: {
            "codex": "gpt-4o",
            "gemini": "gemini-1.5-pro",
        }
    )
    cache_dir: Path = Path(".cache/prompts")
    cache_ttl_seconds: int = 3600
    agents_docs: list[Path] = field(
        default_factory=lambda: [
            Path("AGENTS.md"),
            Path("src/frontend/react_app/AGENTS.md"),
        ]
    )
    multi_agent_sequence: list[str] = field(
        default_factory=lambda: [
            "A1",
            "A2",
            "A3",
            "A4",
            "A5",
            "A6",
            "A7",
            "A8",
            "A9",
        ]
    )

    def ensure_dirs(self) -> None:
        """Create directories for prompts and cache if they don't exist."""
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


CONFIG = PromptConfig()
