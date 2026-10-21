"""Offline coverage for the MaximoDev engine: scaffolder, validators and roster wiring."""
import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import new_work  # noqa: E402
import validate_work  # noqa: E402

FORMULA = "src/08-formulas/object/ASSET__ENGINETEST.json"


def fill(path: Path, *rows: str):
    lines = path.read_text(encoding="utf-8").splitlines()
    last = max(i for i, line in enumerate(lines) if line.startswith("|"))
    lines[last:last + 1] = list(rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for rel in ("engine", "manifests"):
            shutil.copytree(ROOT / rel, self.tmp / rel)
        (self.tmp / FORMULA).parent.mkdir(parents=True)
        (self.tmp / FORMULA).write_text('{"objectname": "ASSET", "formulaname": "ENGINETEST"}\n')
        self.patches = [patch.object(new_work, "ROOT", self.tmp),
                        patch.object(new_work, "TEMPLATES", self.tmp / "engine/templates"),
                        patch("maxdev.registry.SRC", self.tmp / "src"),
                        patch("maxdev.registry.ROOTS", [self.tmp / "src/00_predeployment", self.tmp / "src"]),
                        patch("maxdev.engine.REPO", self.tmp),
                        patch("maxdev.manifest.REPO", self.tmp)]
        for p in self.patches:
            p.start()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(new_work.main(["T-1", "--env", "demo"]), 0)
        self.wp = self.tmp / "work/T-1"

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp)

    def statuses(self):
        return {r["id"]: r for r in validate_work.validate("T-1", root=self.tmp)}

    def build_valid_package(self):
        fill(self.wp / "REQUIREMENT_REGISTER.md",
             "| FUN-001 | SRC-1 | Asset cost formula | ENGINETEST evaluates | High | DESIGNED | requirements-analyst |")
        fill(self.wp / "SOLUTION_CLASSIFICATION.md",
             "| FUN-001 | Object formula | CONFIGURATION | | ART-1 | extract | maximo-functional-architect |")
        fill(self.wp / "ARTIFACT_REGISTER.md",
             f"| ART-1 | FUN-001 | objformula | ASSET/ENGINETEST | {FORMULA} | NEW | configuration-developer | |")
        (self.tmp / "manifests/T-1.yaml").write_text(f"name: T-1\nitems:\n  - path: {FORMULA}\n")

    def test_scaffold_fills_placeholders_and_never_overwrites(self):
        names = {p.name for p in self.wp.glob("*.md")}
        self.assertEqual(names, {p.name for p in (ROOT / "engine/templates").glob("*.md")})
        text = (self.wp / "WORK_CHECKLIST.md").read_text()
        self.assertNotIn("{{", text)
        self.assertIn("demo", text)
        (self.wp / "WORK_CHECKLIST.md").write_text("kept")
        with contextlib.redirect_stdout(io.StringIO()):
            new_work.main(["T-1"])
        self.assertEqual((self.wp / "WORK_CHECKLIST.md").read_text(), "kept")

    def test_empty_package_skips_everything(self):
        self.assertEqual({r["status"] for r in self.statuses().values()}, {"SKIP"})

    def test_valid_package_passes(self):
        self.build_valid_package()
        res = self.statuses()
        self.assertFalse([r for r in res.values() if r["status"] == "FAIL"], res)
        for vid in ("W-01", "W-02", "W-03", "W-04", "W-05", "W-10", "W-11", "W-12", "W-13", "W-14"):
            self.assertEqual(res[vid]["status"], "PASS", vid)

    def test_defects_are_detected(self):
        self.build_valid_package()
        fill(self.wp / "SOLUTION_CLASSIFICATION.md",
             "| FUN-001 | Script | AUTOMATION SCRIPT | | ART-9 | | maximo-functional-architect |",
             "| GIS-001 | Map | CONFIGURATION | | ART-1 | | gis-esri-specialist |")
        fill(self.wp / "REQUIREMENT_REGISTER.md",
             "| FUN-001 | SRC-1 | Asset cost | evaluates | High | VERIFIED | requirements-analyst |",
             "| GIS-001 | SRC-1 | Map | shows | Low | OPEN | requirements-analyst |")
        fill(self.wp / "ARTIFACT_REGISTER.md",
             f"| ART-1 | FUN-001 | objformula | X | {FORMULA} | NEW | automation-script-developer | |",
             "| ART-2 | FUN-404 | domain | Y | src/03-domains/NOPE.json | NEW | configuration-developer | |")
        fill(self.wp / "DEPLOYMENT_PLAN.md", "| 1 | demo | deploy | APPLY | ok | | | |")
        fill(self.wp / "FINDINGS_LOG.md", "| F-1 | D5 | ART-1 | bad | BLOCKER | x | fix | OPEN |")
        res = self.statuses()
        for vid in ("W-03", "W-04", "W-05", "W-10", "W-12", "W-20", "W-21", "W-22", "W-23", "W-25", "W-27"):
            self.assertEqual(res[vid]["status"], "FAIL", vid)

    def test_unregistered_manifest_file_fails_w14(self):
        self.build_valid_package()
        extra = self.tmp / "src/08-formulas/object/ASSET__EXTRA.json"
        extra.write_text("{}\n")
        (self.tmp / "manifests/T-1.yaml").write_text(
            f"name: T-1\nitems:\n  - path: [{FORMULA}, src/08-formulas/object/ASSET__EXTRA.json]\n")
        self.assertEqual(self.statuses()["W-14"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
