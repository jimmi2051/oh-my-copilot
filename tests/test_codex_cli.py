from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from omc_copilot.adapters.codex_cli import CodexRuntimeAdapter
from omc_copilot.execution.command_runner import CommandResult


class CodexRuntimeAdapterTest(unittest.TestCase):
    def test_generate_constructs_read_only_non_interactive_command(self) -> None:
        root = Path("/tmp/project")
        result = CommandResult(
            command=[],
            returncode=0,
            stdout="answer",
            stderr="",
        )
        with patch(
            "omc_copilot.adapters.codex_cli.shutil.which",
            return_value="/usr/local/bin/codex",
        ):
            with patch(
                "omc_copilot.adapters.codex_cli.run_command",
                return_value=result,
            ) as run:
                reply = CodexRuntimeAdapter(working_dir=root).generate("hello")

        self.assertEqual(reply.text, "answer")
        run.assert_called_once_with(
            [
                "codex",
                "exec",
                "--sandbox",
                "read-only",
                "-c",
                'approval_policy="never"',
                "--cd",
                str(root),
                "hello",
            ],
            cwd=root,
        )

    def test_generate_raises_with_failure_details(self) -> None:
        result = CommandResult(
            command=[],
            returncode=2,
            stdout="",
            stderr="bad flags",
        )
        with patch(
            "omc_copilot.adapters.codex_cli.shutil.which",
            return_value="/usr/local/bin/codex",
        ):
            with patch(
                "omc_copilot.adapters.codex_cli.run_command",
                return_value=result,
            ):
                with self.assertRaisesRegex(
                    RuntimeError, "codex command failed \\(code=2\\): bad flags"
                ):
                    CodexRuntimeAdapter().generate("hello")


if __name__ == "__main__":
    unittest.main()
