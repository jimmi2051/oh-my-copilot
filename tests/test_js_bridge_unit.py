import shutil
import subprocess
from types import SimpleNamespace

import pytest

from omc_copilot.adapters.js_bridge import (JSBridgeError, run_js_code,
                                            run_js_script)


def _completed(stdout=b"", stderr=b"", returncode=0):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


def test_non_zero_exit(tmp_path, monkeypatch):
    script = tmp_path / "script.js"
    script.write_text('console.log("hello")')

    # pretend node exists
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/node")

    def fake_run(*args, **kwargs):
        return _completed(stdout=b"", stderr=b"boom", returncode=1)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(JSBridgeError):
        run_js_script(str(script))


def test_invalid_json_returns_raw(tmp_path, monkeypatch):
    script = tmp_path / "script.js"
    script.write_text('console.log("not json")')

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/node")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: _completed(
            stdout=b"notjson\n", stderr=b"", returncode=0
        ),
    )

    res = run_js_script(str(script))
    assert isinstance(res, str) and res == "notjson"


def test_timeout(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/node")

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="node", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(JSBridgeError):
        run_js_code("console.log(1)", timeout=1)


def test_missing_script():
    with pytest.raises(JSBridgeError):
        run_js_script("no-such-file.js")
