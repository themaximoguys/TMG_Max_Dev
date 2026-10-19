"""Throwaway signing key for offline tests: trusts it in-process and installs a
wildcard licence through MAXDEV_LICENSE. Import before constructing a Session."""
import datetime as dt
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from maxdev import license  # noqa: E402
from maxdev.license import public_hex, sign  # noqa: E402

KEY = Ed25519PrivateKey.generate()
license.PUBLIC_KEYS.append(public_hex(KEY))


def token(expires=None, hosts=("*",)):
    payload = {"id": "TMG-TEST-001", "customer": "Unit Test", "issued": "2026-01-01",
               "expires": (expires or dt.date.today() + dt.timedelta(days=365)).isoformat(),
               "hosts": list(hosts)}
    return sign(KEY, payload)


os.environ["MAXDEV_LICENSE"] = token()
