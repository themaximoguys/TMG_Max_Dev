"""Licence key verification and the Session gate."""
import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import license_fixture as fx

from maxdev import engine, license

URL = "https://maximo.manage.acme.com/maximo"
TODAY = dt.date(2026, 10, 19)


class LicenseTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)

    def use(self, tok):
        os.environ["MAXDEV_LICENSE"] = tok

    def test_valid_signature_parses(self):
        lic = license.parse(fx.token(hosts=["*.acme.com"]))
        self.assertEqual((lic.id, lic.customer, lic.hosts), ("TMG-TEST-001", "Unit Test", ["*.acme.com"]))

    def test_tampered_payload_rejected(self):
        head, body, sig = fx.token().split(".")
        d = json.loads(license._b64d(body))
        d["expires"] = "2099-12-31"
        forged = license._b64(json.dumps(d).encode())
        with self.assertRaisesRegex(license.LicenseError, "invalid signature"):
            license.parse(f"{head}.{forged}.{sig}")

    def test_foreign_signing_key_rejected(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        rogue = license.sign(Ed25519PrivateKey.generate(), {"id": "X", "customer": "X", "issued": "2026-01-01",
                                                   "expires": "2099-01-01", "hosts": ["*"]})
        with self.assertRaisesRegex(license.LicenseError, "invalid signature"):
            license.parse(rogue)

    def test_garbage_rejected(self):
        for bad in ("", "nope", "TMG1.a", "XYZ1.a.b"):
            with self.assertRaises(license.LicenseError):
                license.parse(bad)

    def test_missing_license_names_contact(self):
        os.environ.pop("MAXDEV_LICENSE")
        with tempfile.TemporaryDirectory() as home, patch.object(license, "REPO", Path(home)), \
                patch.object(Path, "home", return_value=Path(home)):
            with self.assertRaisesRegex(license.LicenseError, license.CONTACT):
                license.require(URL)
            self.assertEqual(license.status()["state"], "invalid")

    def test_license_file_paths(self):
        with tempfile.TemporaryDirectory() as home:
            f = Path(home) / ".config/maxdev/license.key"
            f.parent.mkdir(parents=True)
            f.write_text(fx.token() + "\n")
            os.environ.pop("MAXDEV_LICENSE")
            with patch.object(license, "REPO", Path(home) / "norepo"), patch.object(Path, "home", return_value=Path(home)):
                self.assertEqual(license.load().source, str(f))
            self.use(str(f))
            self.assertEqual(license.load().source, str(f))

    def test_expiry_grace_then_refused(self):
        self.use(fx.token(expires=TODAY - dt.timedelta(days=3)))
        self.assertEqual(license.require(URL, today=TODAY).id, "TMG-TEST-001")
        self.assertEqual(license.load().as_dict(TODAY)["state"], "grace")
        self.use(fx.token(expires=TODAY - dt.timedelta(days=license.GRACE_DAYS + 1)))
        with self.assertRaisesRegex(license.LicenseError, "expired"):
            license.require(URL, today=TODAY)

    def test_host_binding(self):
        self.use(fx.token(hosts=["*.acme.com", "maximo.local"]))
        license.require(URL)
        license.require("https://maximo.local:9443/maximo")
        with self.assertRaisesRegex(license.LicenseError, "does not cover"):
            license.require("https://maximo.other.com/maximo")

    def test_session_enforces_license(self):
        self.use(fx.token(hosts=["licensed.example.com"]))
        with patch.dict(os.environ, {"MAXIMO_BASE_URL": URL, "MAXIMO_API_KEY": "k"}):
            with self.assertRaises(license.LicenseError):
                engine.Session("unittest")


if __name__ == "__main__":
    unittest.main()
