"""Offline coverage for the agent hooks and the component checker."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import agent_hook  # noqa: E402
import check_components  # noqa: E402


def guard(tool, **tool_input):
    with contextlib.redirect_stderr(io.StringIO()):
        return agent_hook.guard({"tool_name": tool, "tool_input": tool_input, "cwd": str(ROOT)})


class GuardTests(unittest.TestCase):
    def test_environment_secrets_are_blocked(self):
        for tool in ("Read", "Edit", "Write"):
            for path in ("environments/.env.demo", str(ROOT / "environments/.env.prod")):
                with self.subTest(tool=tool, path=path):
                    self.assertEqual(guard(tool, file_path=path), 2)
        self.assertEqual(guard("Bash", command="cat environments/.env.demo"), 2)
        self.assertEqual(guard("Bash", command="sed -i s/true/false/ environments/.env.demo-ro"), 2)

    def test_example_and_ordinary_files_pass(self):
        self.assertEqual(guard("Read", file_path="environments/.env.example"), 0)
        self.assertEqual(guard("Edit", file_path="src/08-formulas/object/ASSET__X.json"), 0)
        self.assertEqual(guard("Bash", command="python3 -m maxdev --env demo ping"), 0)
        self.assertEqual(guard("Bash", command="curl -s https://host/maximo/api/os/mxapiasset"), 0)

    def test_raw_maximo_writes_are_blocked(self):
        for cmd in ("curl -X POST https://host/maximo/api/os/mxapiasset -d '{}'",
                    "curl https://host/maximo/oslc/script/X --data x=1",
                    "Invoke-RestMethod https://host/maximo/api/os/x -Method Delete"):
            with self.subTest(cmd=cmd):
                self.assertEqual(guard("Bash", command=cmd), 2)


class LintHookTests(unittest.TestCase):
    def test_files_outside_src_scripts_are_ignored(self):
        for path in ("tools/agent_hook.py", "README.md", "src/00_predeployment/README.md"):
            with self.subTest(path=path):
                self.assertEqual(agent_hook.lint({"tool_input": {"file_path": path}, "cwd": str(ROOT)}), 0)


class ComponentTests(unittest.TestCase):
    def test_repository_components_are_complete(self):
        self.assertEqual(check_components.check(), [])


if __name__ == "__main__":
    unittest.main()
