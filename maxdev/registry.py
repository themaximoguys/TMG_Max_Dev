"""Loads registry.yaml and resolves which object structure a tenant actually has."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from .env import REPO

SRC = REPO / "src"
HANDLERS = {"json", "replace", "autoscript", "appxml", "readonly", "manual"}


@dataclass
class ArtifactType:
    id: str
    label: str
    layer: int
    os: list[str]
    key: list[str]
    folder: str
    handler: str
    name: list[str] = field(default_factory=list)
    select: str = "*"
    post: str = ""
    status: str = "ok"
    note: str = ""

    @property
    def dir(self) -> Path:
        return SRC / self.folder

    @property
    def name_fields(self) -> list[str]:
        return self.name or self.key[:1]

    @property
    def deployable(self) -> bool:
        return self.handler in {"json", "replace", "autoscript", "appxml"} and bool(self.os)

    def resolve_os(self, client=None, overrides: dict[str, str] | None = None) -> str:
        """Pick the structure to use: env override > first that exists on tenant > first listed."""
        ov = (overrides or {}).get(f"MAXIMO_OS_{self.id.upper()}")
        if ov:
            return ov
        if not self.os:
            raise ValueError(f"{self.id} has no REST object structure (handler={self.handler})")
        if client is None or len(self.os) == 1:
            return self.os[0]
        cache = _os_cache.setdefault(client.base, {})
        for name in self.os:
            if name not in cache:
                cache[name] = client.os_probe(name) == "ok"
            if cache[name]:
                return name
        return self.os[-1]


_os_cache: dict[str, dict[str, bool]] = {}


@lru_cache(maxsize=1)
def load() -> tuple[dict[int, str], dict[str, ArtifactType]]:
    raw = yaml.safe_load((Path(__file__).parent / "registry.yaml").read_text(encoding="utf-8"))
    types: dict[str, ArtifactType] = {}
    for t in raw["types"]:
        os_ = t.get("os") or []
        t = {**t, "os": [os_] if isinstance(os_, str) else list(os_)}
        at = ArtifactType(**t)
        if at.handler not in HANDLERS:
            raise ValueError(f"registry: {at.id} has unknown handler {at.handler}")
        if at.id in types:
            raise ValueError(f"registry: duplicate id {at.id}")
        types[at.id] = at
    return {int(k): v for k, v in raw["layers"].items()}, types


def types() -> dict[str, ArtifactType]:
    return load()[1]


def get(type_id: str) -> ArtifactType:
    t = types().get(type_id)
    if not t:
        raise KeyError(f"unknown artifact type {type_id!r}; run `maxdev types`")
    return t


def ordered(ids: list[str] | None = None) -> list[ArtifactType]:
    sel = [types()[i] for i in ids] if ids else list(types().values())
    return sorted(sel, key=lambda t: (t.layer, list(types()).index(t.id)))


ROOTS = [SRC, REPO / "bootstrap"]


def type_for_path(path: Path) -> ArtifactType | None:
    """Map a file to its type by folder. Works for src/ and for bootstrap/, which
    mirrors src/ layout. Longest folder wins (07-app-designer/_queries beats 07-app-designer)."""
    path = path.resolve()
    for root in ROOTS:
        root = root.resolve()
        if root not in path.parents:
            continue
        rel = path.parent.relative_to(root).as_posix()
        best = None
        for t in types().values():
            f = t.folder
            if rel == f or (rel.startswith(f + "/") and t.handler == "autoscript"):
                if best is None or len(f) > len(best.folder):
                    best = t
        return best
    return None
