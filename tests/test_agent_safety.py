"""Offline regression coverage for CLI/MCP write authorization boundaries."""
import contextlib
import io
import json
import unittest
from unittest.mock import MagicMock, patch

import license_fixture  # noqa: F401
from maxdev import cli, ibm_mcp, mcp_server


class CliWriteSafetyTests(unittest.TestCase):
    COMMANDS = [
        ["script", "TMG.TEST"],
        ["script", "TMG.TEST", "--get"],
        ["dbconfig", "apply"],
        ["dbconfig", "apply", "--admin"],
        ["adminmode", "on"],
        ["adminmode", "off"],
        ["dm", "create", "PACKAGE"],
        ["dm", "upload", "package.zip"],
        ["dm", "deploy"],
        ["dm", "deploy", "--complete"],
    ]

    def invoke(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = cli.main(["--env", "unittest"] + args)
        return rc, stdout.getvalue(), stderr.getvalue()

    def test_write_commands_default_to_plans_without_remote_calls(self):
        for args in self.COMMANDS:
            with self.subTest(args=args), patch.object(cli.engine, "Session") as factory:
                session = factory.return_value
                session.env = "unittest"
                rc, output, _ = self.invoke(args)
                self.assertEqual(rc, 0)
                self.assertEqual(json.loads(output)["mode"], "DRY-RUN")
                self.assertEqual(session.mock_calls, [])

    def test_apply_refuses_protected_targets_before_remote_calls(self):
        for args in self.COMMANDS:
            with self.subTest(args=args), patch.object(cli.engine, "Session") as factory:
                session = factory.return_value
                session.guard_write.side_effect = PermissionError("protected")
                rc, _, error = self.invoke(args + ["--apply"])
                self.assertEqual(rc, 2)
                self.assertIn("protected", error)
                session.client.assert_not_called()
                self.assertEqual(session.client.mock_calls, [])

    def test_approved_script_preserves_arguments_and_checks_guard(self):
        with patch.object(cli.engine, "Session") as factory:
            session = factory.return_value
            session.client.call_script.return_value = {"ok": True}
            rc, output, _ = self.invoke(["script", "TMG.TEST", "--get", "--param", "x=a=b",
                                         "--body", '{"test": true}', "--apply"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(output), {"ok": True})
            session.guard_write.assert_called_once_with()
            session.client.call_script.assert_called_once_with(
                "TMG.TEST", params={"x": "a=b"}, body={"test": True}, method="GET")

    def test_bootstrap_failure_returns_nonzero(self):
        with patch.object(cli.engine, "Session"), patch.object(cli.engine, "resolve_files", return_value=[]), \
                patch.object(cli.engine, "deploy", return_value={"results": [], "summary": {"FAILED": 1}}):
            self.assertEqual(self.invoke(["bootstrap"])[0], 1)


class IbmToolSafetyTests(unittest.TestCase):
    def test_only_boolean_true_is_read_only(self):
        for name in ("getAndDelete", "listAndUpdate", "query", "read", "find", "create"):
            for value in (None, False, "false", "true", 1, 0, [], {}):
                with self.subTest(name=name, value=value):
                    self.assertFalse(ibm_mcp.is_read_only({"name": name, "annotations": {"readOnlyHint": value}}))
            self.assertFalse(ibm_mcp.is_read_only({"name": name}))
            self.assertTrue(ibm_mcp.is_read_only({"name": name, "annotations": {"readOnlyHint": True}}))
        self.assertFalse(ibm_mcp.is_read_only({"annotations": ["readOnlyHint"]}))

    def test_mcp_unannotated_tool_is_not_called(self):
        session, remote = MagicMock(), MagicMock()
        remote.list_tools.return_value = [{"name": "getAndDelete"}]
        with patch.object(mcp_server, "_s", return_value=session), \
                patch.object(ibm_mcp.IbmMcpClient, "from_session", return_value=remote):
            result = json.loads(mcp_server.ibm_mcp_call("getAndDelete", env="unittest"))
            self.assertEqual(result["mode"], "DRY-RUN")
            remote.call_tool.assert_not_called()
            session.guard_write.side_effect = PermissionError("protected")
            with self.assertRaises(PermissionError):
                mcp_server.ibm_mcp_call("getAndDelete", apply=True, env="unittest")
            remote.call_tool.assert_not_called()

    def test_cli_unannotated_tool_is_not_called(self):
        remote = MagicMock()
        remote.list_tools.return_value = [{"name": "getAndDelete"}]
        with patch.object(cli.engine, "Session"), \
                patch.object(ibm_mcp.IbmMcpClient, "from_session", return_value=remote), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["--env", "unittest", "ibm-mcp", "call", "getAndDelete"]), 2)
            remote.call_tool.assert_not_called()

    def test_mcp_read_only_tool_still_works(self):
        remote = MagicMock()
        remote.list_tools.return_value = [{"name": "getAsset", "annotations": {"readOnlyHint": True}}]
        remote.call_tool.return_value = {"ok": True}
        with patch.object(mcp_server, "_s"), \
                patch.object(ibm_mcp.IbmMcpClient, "from_session", return_value=remote):
            self.assertEqual(json.loads(mcp_server.ibm_mcp_call("getAsset")), {"ok": True})
            remote.call_tool.assert_called_once_with("getAsset", None)


if __name__ == "__main__":
    unittest.main()
