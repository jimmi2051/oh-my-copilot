import json
import os
import shutil

import pytest

from omc_copilot.adapters.js_bridge import JSBridgeError, run_js_code


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_run_js_code_echo(tmp_path):
    # Node.js script that reads JSON from stdin and echoes it back inside {ok: true, echo: <input>}
    code = r"""
const fs = require('fs');
let data = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  try {
    const obj = data ? JSON.parse(data) : {};
    console.log(JSON.stringify({ok:true, echo: obj}));
  } catch (e) {
    console.error(e.toString());
    process.exit(1);
  }
});
"""

    input_obj = {"hello": "world"}
    res = run_js_code(code, input_obj=input_obj, timeout=5)
    assert isinstance(res, dict)
    assert res.get("ok") is True
    assert res.get("echo") == input_obj


def test_run_js_code_node_missing_monkeypatch(monkeypatch):
    # Simulate node being absent by monkeypatching shutil.which to return None.
    # This ensures the adapter surfaces a clear JSBridgeError without relying on the test environment.
    monkeypatch.setattr(shutil, "which", lambda name: None)

    with pytest.raises(JSBridgeError):
        run_js_code("console.log(1)")
