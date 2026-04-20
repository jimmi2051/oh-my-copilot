from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omc_copilot.compatibility.hook_registry import supported_hook_events
from omc_copilot.hooks.dispatcher import HookDispatcher


class HookDispatcherTest(unittest.TestCase):
    def test_dispatch_covers_all_supported_events(self) -> None:
        event_inputs: dict[str, dict[str, object]] = {
            "UserPromptSubmit": {"prompt": "  build api  "},
            "SessionStart": {},
            "PreToolUse": {"tool_name": "python"},
            "PermissionRequest": {
                "tool_name": "bash",
                "reason": "write file",
                "requires_approval": False,
            },
            "PostToolUse": {"tool_name": "bash", "ok": "true"},
            "PostToolUseFailure": {
                "tool_name": "bash",
                "error": "permission denied",
                "exit_code": "126",
            },
            "SubagentStart": {"agent_name": "python-expert", "task_id": "task-1"},
            "SubagentStop": {"agent_name": "python-expert", "outcome": "completed"},
            "PreCompact": {"reason": "token pressure", "messages_before": "42"},
            "Stop": {"active_mode": "autopilot"},
            "SessionEnd": {"summary": "done"},
        }

        with tempfile.TemporaryDirectory() as td:
            dispatcher = HookDispatcher(Path(td))
            for event in supported_hook_events():
                out = dispatcher.dispatch(event, **event_inputs[event])
                self.assertEqual(out["event"], event)
                self.assertEqual(out["status"], "handled")

            session_start = dispatcher.dispatch("SessionStart")
            self.assertEqual(session_start["project_root"], td)
            self.assertIn("timestamp", session_start)

            user_prompt_submit = dispatcher.dispatch(
                "UserPromptSubmit", prompt="  hello  "
            )
            self.assertEqual(user_prompt_submit["prompt"], "hello")
            self.assertEqual(user_prompt_submit["prompt_length"], 5)

            permission_request = dispatcher.dispatch(
                "PermissionRequest", requires_approval=False
            )
            self.assertEqual(permission_request["decision"], "auto-allow")

            post_tool_use = dispatcher.dispatch("PostToolUse", ok="true")
            self.assertTrue(post_tool_use["ok"])

            post_tool_use_failure = dispatcher.dispatch(
                "PostToolUseFailure", exit_code="126"
            )
            self.assertEqual(post_tool_use_failure["exit_code"], 126)

            pre_compact = dispatcher.dispatch("PreCompact", messages_before="4")
            self.assertEqual(pre_compact["messages_before"], 4)

            session_end = dispatcher.dispatch("SessionEnd", summary="done")
            self.assertEqual(session_end["summary"], "done")
            self.assertIn("timestamp", session_end)

    def test_unsupported_event(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            dispatcher = HookDispatcher(Path(td))
            out = dispatcher.dispatch("NotARealHook", sample=True)
            self.assertEqual(out["event"], "NotARealHook")
            self.assertEqual(out["status"], "unsupported")
            self.assertEqual(out["supported_events"], supported_hook_events())


if __name__ == "__main__":
    unittest.main()
