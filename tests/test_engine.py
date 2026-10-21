"""Offline coverage for the ticket engine: scaffolder and ticket validator."""
import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import new_work  # noqa: E402
import validate_work  # noqa: E402

FORMULA = "src/08-formulas/object/ASSET__ENGINETEST.json"
CLEAN_GIT = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}  # safe inside a git hook


def table(path: Path, heading: str, *rows: str):
    """Replace the blank row of the table under `## heading` with rows."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(f"## {heading}")
    blank = next(i for i in range(start, len(lines))
                 if lines[i].startswith("|") and lines[i].replace("|", "").strip() == "")
    lines[blank:blank + 1] = list(rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT / "skills/maximo-dev-engine", self.tmp / "skills/maximo-dev-engine")
        (self.tmp / "manifests").mkdir()
        (self.tmp / FORMULA).parent.mkdir(parents=True)
        (self.tmp / FORMULA).write_text('{"objectname": "ASSET", "formulaname": "ENGINETEST"}\n')
        self.patches = [patch.object(new_work, "ROOT", self.tmp),
                        patch.object(new_work, "TEMPLATE", self.tmp / "skills/maximo-dev-engine/TICKET_TEMPLATE.md"),
                        patch("maxdev.registry.SRC", self.tmp / "src"),
                        patch("maxdev.registry.ROOTS", [self.tmp / "src/00_predeployment", self.tmp / "src"]),
                        patch("maxdev.engine.REPO", self.tmp),
                        patch("maxdev.manifest.REPO", self.tmp),
                        patch.dict(os.environ, CLEAN_GIT, clear=True)]
        for p in self.patches:
            p.start()
        self.ticket = self.tmp / "work/T-1.md"

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.tmp)

    def open(self, kind="feature"):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(new_work.main(["T-1", "--type", kind, "--env", "demo"]), 0)

    def res(self):
        return {r["id"]: r for r in validate_work.validate("T-1", root=self.tmp)}

    def build(self):
        table(self.ticket, "Requirements", "| FUN-001 | Asset cost formula | ENGINETEST evaluates |")
        table(self.ticket, "Design", "| FUN-001 | CONFIGURATION | | ART-1 | main |")
        table(self.ticket, "Artifacts", f"| ART-1 | objformula | {FORMULA} | NEW | maximo-dev |")
        (self.tmp / "manifests/T-1.yaml").write_text(f"name: T-1\nitems:\n  - path: {FORMULA}\n")

    def test_scaffold_fills_template_and_never_overwrites(self):
        self.open("bug")
        text = self.ticket.read_text()
        self.assertNotIn("{{", text)
        self.assertIn("- **Type:** bug", text)
        self.assertTrue((self.tmp / "manifests/T-1.yaml").is_file())
        self.ticket.write_text("kept")
        self.open()
        self.assertEqual(self.ticket.read_text(), "kept")

    def test_empty_ticket_skips_everything(self):
        self.open()
        self.assertEqual({r["status"] for r in self.res().values()}, {"SKIP"})

    def test_valid_ticket_passes(self):
        self.open()
        self.build()
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True)
        subprocess.run(["git", "add", "-f", FORMULA], cwd=self.tmp, check=True)
        res = self.res()
        self.assertFalse([r for r in res.values() if r["status"] == "FAIL"], res)
        for vid in ("T-01", "T-02", "T-03", "T-04", "T-05", "T-06"):
            self.assertEqual(res[vid]["status"], "PASS", vid)

    def test_traceability_and_manifest_defects(self):
        self.open()
        table(self.ticket, "Requirements", "| FUN-001 | x | |", "| FUN-001 | y | z |")
        table(self.ticket, "Design", "| FUN-001 | AUTOMATION SCRIPT | | ART-9 | main |")
        table(self.ticket, "Artifacts", f"| ART-1 | domain | {FORMULA} | NEW | maximo-dev |",
              "| ART-2 | domain | src/03-domains/NOPE.json | ADD | maximo-dev |")
        (self.tmp / "manifests/T-1.yaml").write_text("name: T-1\nitems: []\n")
        res = self.res()
        for vid in ("T-01", "T-02", "T-03", "T-04", "T-05"):
            self.assertEqual(res[vid]["status"], "FAIL", vid)

    def test_git_tracking_and_stale_index(self):
        self.open()
        self.build()
        self.assertEqual(self.res()["T-06"]["status"], "SKIP")  # not a git work tree
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True)
        self.assertEqual(self.res()["T-06"]["status"], "FAIL")
        subprocess.run(["git", "add", "-f", FORMULA], cwd=self.tmp, check=True)
        self.assertEqual(self.res()["T-06"]["status"], "PASS")
        (self.tmp / FORMULA).write_text('{"changed": true}\n')
        self.assertEqual(self.res()["T-06"]["status"], "FAIL")

    def test_apply_needs_dry_run_approval_receipt_and_same_rediff(self):
        self.open()
        self.build()
        receipt = self.tmp / ".maxdev/receipts/demo/1.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text("{}")
        table(self.ticket, "Deploy log", "| 1 | demo | deploy | APPLY | created | | | |")
        self.assertEqual(self.res()["T-08"]["status"], "FAIL")
        self.ticket.write_text(self.ticket.read_text().replace(
            "| 1 | demo | deploy | APPLY | created | | | |",
            "| 1 | demo | deploy | DRY-RUN | would-create | | | d |\n"
            "| 2 | demo | deploy --apply | APPLY | created | .maxdev/receipts/demo/1.json | \"yes\" | d |\n"
            "| 3 | demo | diff | RE-DIFF | changed: length | | | d |"))
        self.assertEqual(self.res()["T-08"]["status"], "FAIL")  # applied, but live differs from repo
        self.ticket.write_text(self.ticket.read_text().replace("| changed: length |", "| same |"))
        self.assertEqual(self.res()["T-08"]["status"], "PASS")

    def test_bug_ticket_needs_reproduction_root_cause_and_regression(self):
        self.open("bug")
        self.assertEqual(self.res()["T-09"]["status"], "FAIL")
        table(self.ticket, "Current state", "| repro | demo | query X | wrong value |")
        self.ticket.write_text(self.ticket.read_text().replace(
            "**Root cause (bug only):**", "**Root cause (bug only):** script skips nulls"))
        table(self.ticket, "Tests", "| regression-1 | BUG-001 | demo | query X | PASS | ok |")
        self.assertEqual(self.res()["T-09"]["status"], "PASS")

    def test_done_needs_passing_tests_for_every_requirement(self):
        self.open()
        self.build()
        self.ticket.write_text(self.ticket.read_text().replace("- **Status:** intake", "- **Status:** done"))
        self.assertEqual(self.res()["T-10"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
