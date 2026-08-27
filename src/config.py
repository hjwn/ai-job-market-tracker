"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


class ConfigurationError(RuntimeError):
    """Raised when a required application setting is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Environment-backed application settings."""

    saramin_api_key: str | None = None

    def require_saramin_api_key(self) -> str:
        """Return the API key or raise a safe, actionable error."""
        if not self.saramin_api_key:
            raise ConfigurationError(
                "SARAMIN_API_KEY가 설정되지 않았습니다. "
                ".env.example을 복사해 .env를 만들고 발급받은 키를 입력하세요."
            )
        return self.saramin_api_key


def load_settings(
    env_file: str | Path | None = None,
    *,
    override: bool = False,
) -> Settings:
    """Load settings from ``.env`` and the process environment.

    Process environment values take precedence unless ``override`` is true.
    Loading configuration alone does not require an API key; callers that make
    a Saramin request must use ``require_saramin_api_key``.
    """
    file_value = _read_env_value(Path(env_file or DEFAULT_ENV_FILE), "SARAMIN_API_KEY")
    environment_value = os.getenv("SARAMIN_API_KEY")
    api_key = file_value if override and file_value is not None else environment_value
    if api_key is None:
        api_key = file_value

    return Settings(saramin_api_key=api_key.strip() if api_key else None)


def _read_env_value(env_file: Path, target_key: str) -> str | None:
    """Read one simple KEY=VALUE setting without adding a runtime dependency."""
    try:
        lines = env_file.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        return None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()

        key, separator, value = line.partition("=")
        if separator and key.strip() == target_key:
            cleaned_value = value.strip()
            if (
                len(cleaned_value) >= 2
                and cleaned_value[0] == cleaned_value[-1]
                and cleaned_value[0] in {"'", '"'}
            ):
                cleaned_value = cleaned_value[1:-1]
            return cleaned_value

    return None
