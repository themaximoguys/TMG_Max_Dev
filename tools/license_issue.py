"""Issue a signed maxdev licence key (TheMaximoGuys LLC internal).

  python3 tools/license_issue.py --id TMG-ACME-2026-001 --customer "Acme Water" \
      --expires 2027-10-31 --host "*.manage.acme.com" --host maximo.acme.local [--out acme.key]

The signing key is read from TMG_LICENSE_SIGNING_KEY (default
~/.tmg-license/ed25519_signing_key.pem). It must never be placed in this repo.
`--keygen` creates a new signing key and prints the public key to add to
maxdev/license.py PUBLIC_KEYS.
"""
import argparse
import datetime as dt
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from maxdev import license as lic  # noqa: E402
from maxdev.license import public_hex, sign  # noqa: E402

DEFAULT_KEY = Path.home() / ".tmg-license/ed25519_signing_key.pem"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--key", default=os.environ.get("TMG_LICENSE_SIGNING_KEY", str(DEFAULT_KEY)))
    p.add_argument("--keygen", action="store_true", help="create the signing key and print its public key")
    p.add_argument("--id"); p.add_argument("--customer")
    p.add_argument("--issued", default=dt.date.today().isoformat())
    p.add_argument("--expires", help="last valid day, YYYY-MM-DD")
    p.add_argument("--host", action="append", default=[], help="licensed Maximo hostname or pattern; repeat")
    p.add_argument("--out", help="write the key to this file instead of stdout")
    a = p.parse_args(argv)

    path = Path(a.key).expanduser()
    if a.keygen:
        if path.exists():
            p.error(f"{path} already exists; refusing to overwrite a signing key")
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        k = Ed25519PrivateKey.generate()
        path.write_bytes(k.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption()))
        path.chmod(0o600)
        print(f"created {path}\npublic key (add to PUBLIC_KEYS): {public_hex(k)}")
        return 0
    if not (a.id and a.customer and a.expires and a.host):
        p.error("--id, --customer, --expires and at least one --host are required")
    k = ser.load_pem_private_key(path.read_bytes(), None)
    if public_hex(k) not in lic.PUBLIC_KEYS:
        p.error(f"{path} is not a trusted signing key (its public key is not in maxdev/license.py)")
    payload = {"id": a.id, "customer": a.customer, "issued": dt.date.fromisoformat(a.issued).isoformat(),
               "expires": dt.date.fromisoformat(a.expires).isoformat(), "hosts": a.host}
    token = sign(k, payload)
    lic.parse(token)  # round-trip check against the embedded public key
    if a.out:
        Path(a.out).write_text(token + "\n", encoding="utf-8")
        print(f"wrote {a.out}  ({a.id}, {a.customer}, expires {payload['expires']}, hosts {a.host})")
    else:
        print(token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
