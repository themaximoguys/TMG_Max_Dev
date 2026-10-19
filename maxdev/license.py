"""License key check — offline, no phone-home (Maximo sites are often air-gapped).

A key is one line:  TMG1.<base64url payload JSON>.<base64url Ed25519 signature>
signed by TheMaximoGuys LLC (tools/license_issue.py). Payload fields:

  id        licence identifier, e.g. TMG-ACME-2026-001
  customer  licensee name
  issued    ISO date
  expires   ISO date (last valid day)
  hosts     Maximo hostnames this licence covers; "*" or "*.acme.com" patterns allowed

Where the key is looked up, first match wins:
  1. MAXDEV_LICENSE — a path to a key file, or the key itself
  2. <repo>/license.key            (git-ignored)
  3. ~/.config/maxdev/license.key

The check runs when a Session connects to Maximo, so the CLI and the MCP server
share one gate. After expiry the licence keeps working for GRACE_DAYS with a
warning, then Maximo access is refused.
"""
from __future__ import annotations

import base64
import datetime as dt
import fnmatch
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .env import REPO

PREFIX = "TMG1"
GRACE_DAYS = 14
CONTACT = "hello@themaximoguys.ai"
# Ed25519 public keys trusted to sign licences (raw, hex). Add a new key here to rotate.
PUBLIC_KEYS = ["1fda71839a8f499996e3e47d20714960263331244e88b4b959c718ebad0b5ad9"]


class LicenseError(PermissionError):
    pass


@dataclass
class License:
    id: str
    customer: str
    issued: dt.date
    expires: dt.date
    hosts: list[str]
    source: str

    def days_left(self, today: dt.date | None = None) -> int:
        return (self.expires - (today or dt.date.today())).days

    def covers(self, host: str) -> bool:
        host = host.lower()
        return any(fnmatch.fnmatchcase(host, p.lower()) for p in self.hosts)

    def state(self, today: dt.date | None = None) -> str:
        left = self.days_left(today)
        return "valid" if left >= 0 else ("grace" if left >= -GRACE_DAYS else "expired")

    def as_dict(self, today: dt.date | None = None) -> dict:
        return {"id": self.id, "customer": self.customer, "issued": self.issued.isoformat(),
                "expires": self.expires.isoformat(), "days_left": self.days_left(today),
                "state": self.state(today),
                "hosts": self.hosts, "source": self.source}


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(key, payload: dict) -> str:
    """Encode and sign a payload with an Ed25519 private key (issuer side)."""
    head = f"{PREFIX}.{_b64(json.dumps(payload, separators=(',', ':'), sort_keys=True).encode())}"
    return f"{head}.{_b64(key.sign(head.encode()))}"


def public_hex(key) -> str:
    """Raw hex public key of an Ed25519 private key, as listed in PUBLIC_KEYS."""
    from cryptography.hazmat.primitives import serialization as ser
    return key.public_key().public_bytes(ser.Encoding.Raw, ser.PublicFormat.Raw).hex()


def _locate() -> tuple[str, str] | None:
    """(token, source) from the first configured location, or None."""
    val = os.environ.get("MAXDEV_LICENSE", "").strip()
    if val:
        if val.startswith(PREFIX + "."):
            return val, "MAXDEV_LICENSE"
        p = Path(val).expanduser()
        if not p.is_file():
            raise LicenseError(f"MAXDEV_LICENSE points to {p}, which does not exist")
        return p.read_text(encoding="utf-8").strip(), str(p)
    for p in (REPO / "license.key", Path.home() / ".config/maxdev/license.key"):
        if p.is_file():
            return p.read_text(encoding="utf-8").strip(), str(p)
    return None


def parse(token: str, source: str = "token") -> License:
    """Verify the signature and decode the payload. Raises LicenseError."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != PREFIX:
        raise LicenseError(f"licence key from {source} is not a {PREFIX} key")
    signed = f"{parts[0]}.{parts[1]}".encode()
    try:
        sig = _b64d(parts[2])
    except ValueError as e:
        raise LicenseError(f"licence key from {source} is malformed") from e
    for hexkey in PUBLIC_KEYS:
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(hexkey)).verify(sig, signed)
            break
        except InvalidSignature:
            continue
    else:
        raise LicenseError(f"licence key from {source} has an invalid signature")
    try:
        d = json.loads(_b64d(parts[1]))
        return License(id=d["id"], customer=d["customer"], issued=dt.date.fromisoformat(d["issued"]),
                       expires=dt.date.fromisoformat(d["expires"]), hosts=list(d.get("hosts") or []),
                       source=source)
    except (ValueError, KeyError, TypeError) as e:
        raise LicenseError(f"licence key from {source} has an unreadable payload") from e


def load() -> License:
    found = _locate()
    if not found:
        raise LicenseError("no maxdev licence found — set MAXDEV_LICENSE or install "
                           f"~/.config/maxdev/license.key. Licensing: {CONTACT}")
    return parse(*found)


def require(base_url: str, today: dt.date | None = None) -> License:
    """Gate for Maximo access: valid signature, not past grace, host covered."""
    lic = load()
    state = lic.state(today)
    if state == "expired":
        raise LicenseError(f"maxdev licence {lic.id} expired on {lic.expires} — renew with {CONTACT}")
    if state == "grace":
        print(f"[maxdev] licence {lic.id} expired on {lic.expires}; "
              f"{GRACE_DAYS + lic.days_left(today)} grace day(s) left — renew with {CONTACT}", file=sys.stderr)
    host = urlparse(base_url).hostname or ""
    if not lic.covers(host):
        raise LicenseError(f"maxdev licence {lic.id} does not cover Maximo host {host!r} "
                           f"(licensed: {', '.join(lic.hosts) or 'none'}) — contact {CONTACT}")
    return lic


def status() -> dict:
    """Licence state for display; never raises."""
    try:
        return load().as_dict()
    except LicenseError as e:
        return {"state": "invalid", "error": str(e)}
