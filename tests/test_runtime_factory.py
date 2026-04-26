from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from omc_copilot.adapters.codex_cli import CodexRuntimeAdapter
from omc_copilot.adapters.copilot_cli import CopilotRuntimeAdapter
from omc_copilot.adapters.runtime_factory import (build_runtime_adapter,
                                                  resolve_runtime_name)


class RuntimeFactoryTest(unittest.TestCase):
    def test_cli_runtime_takes_precedence_over_env(self) -> None:
        with patch.dict("os.environ", {"OMC_RUNTIME": "codex"}):
            self.assertEqual(resolve_runtime_name("copilot"), "copilot")

    def test_env_runtime_takes_precedence_over_default(self) -> None:
        with patch.dict("os.environ", {"OMC_RUNTIME": "codex"}):
            self.assertEqual(resolve_runtime_name(), "codex")

    def test_default_runtime_is_copilot(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(resolve_runtime_name(), "copilot")

    def test_factory_builds_codex_adapter(self) -> None:
        with patch(
            "omc_copilot.adapters.codex_cli.shutil.which",
            return_value="/usr/local/bin/codex",
        ):
            adapter = build_runtime_adapter("codex", working_dir=Path("."))
        self.assertIsInstance(adapter, CodexRuntimeAdapter)

    def test_factory_builds_copilot_adapter(self) -> None:
        with patch(
            "omc_copilot.execution.copilot_wrapper.shutil.which",
            return_value="/usr/local/bin/copilot",
        ):
            adapter = build_runtime_adapter("copilot", working_dir=Path("."))
        self.assertIsInstance(adapter, CopilotRuntimeAdapter)


if __name__ == "__main__":
    unittest.main()
