"""Environment resolution.

An environment is a plain dotenv file: environments/.env.<name> (git-ignored).
Copy environments/.env.example to start. Process env vars override file values,
so a one-off run can do  MAXIMO_API_KEY=... maxdev ping --env dev
"""
from __future__ import annotations

import os
from pathlib import Path

from .client import Target

REPO = Path(__file__).resolve().parents[1]
ENV_DIR = REPO / "environments"


def _parse(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def list_envs() -> list[str]:
    return sorted(p.name[len(".env."):] for p in ENV_DIR.glob(".env.*") if p.name != ".env.example")


def load_env(name: str | None = None) -> tuple[Target, dict[str, str]]:
    name = name or os.environ.get("MAXIMO_ENV") or "dev"
    path = ENV_DIR / f".env.{name}"
    vals = _parse(path) if path.exists() else {}
    for k in list(vals) + [k for k in os.environ if k.startswith("MAXIMO_")]:
        if k in os.environ:
            vals[k] = os.environ[k]
    if not vals:
        raise FileNotFoundError(f"no {path} and no MAXIMO_* variables set — copy environments/.env.example")
    target = Target(
        name=name,
        base_url=vals.get("MAXIMO_BASE_URL", ""),
        api_key=vals.get("MAXIMO_API_KEY", ""),
        maxauth=vals.get("MAXIMO_MAXAUTH", ""),
        verify_tls=vals.get("MAXIMO_VERIFY_TLS", "true").lower() != "false",
        timeout=int(vals.get("MAXIMO_TIMEOUT", "180")),
    )
    return target, vals


def is_protected(vals: dict[str, str]) -> bool:
    """Environments flagged MAXIMO_PROTECTED=true (TEST/PROD) refuse writes from
    this dev tool entirely. Promotion beyond DEV is a release process, not a dev task."""
    return vals.get("MAXIMO_PROTECTED", "false").lower() == "true"
