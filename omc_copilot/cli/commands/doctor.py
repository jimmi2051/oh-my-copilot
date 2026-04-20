from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _relative_name(project_root: Path, path: Path) -> str:
    return str(path.relative_to(project_root))


def _json_manifest_check(project_root: Path, path: Path, description: str) -> tuple[str, str, str]:
    name = _relative_name(project_root, path)
    if not path.exists():
        return ("MISSING", name, f"{description} file")
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ("INVALID", name, f"{description} JSON ({exc.msg})")
    return ("OK", name, f"{description} JSON")


def _check_plugin_installation() -> tuple[str, str, str]:
    try:
        proc = subprocess.run(
            ["copilot", "plugin", "list"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except Exception:
        return ("WARN", "copilot-plugin-install", "unable to query installed plugins")

    output = f"{proc.stdout}\n{proc.stderr}".lower()
    if proc.returncode == 0 and "omc-copilot" in output:
        return ("OK", "copilot-plugin-install", "omc-copilot plugin installed")
    return ("WARN", "copilot-plugin-install", "omc-copilot plugin not detected in `copilot plugin list`")


def run_doctor(project_root: Path) -> int:
    checks: list[tuple[str, str, str]] = []
    checks.append(
        (
            "OK" if shutil.which("copilot") else "MISSING",
            "copilot-cli",
            "copilot executable in PATH",
        )
    )

    expected = [
        project_root / "AGENTS.md",
        project_root / ".github" / "copilot-instructions.md",
        project_root / ".github" / "instructions" / "omc.instructions.md",
    ]
    for path in expected:
        checks.append(("OK" if path.exists() else "MISSING", _relative_name(project_root, path), "present"))

    plugin_root = project_root / "plugins" / "omc-copilot"
    plugin_manifest_path = plugin_root / "plugin.json"
    marketplace_manifest = project_root / ".github" / "plugin" / "marketplace.json"
    local_plugin_repo = plugin_root.exists() or marketplace_manifest.exists()
    if local_plugin_repo:
        checks.append(_json_manifest_check(project_root, plugin_manifest_path, "plugin manifest"))
        checks.append(_json_manifest_check(project_root, marketplace_manifest, "marketplace manifest"))

        plugin_manifest: dict[str, object] | None = None
        if plugin_manifest_path.exists():
            try:
                loaded_manifest = json.loads(plugin_manifest_path.read_text(encoding="utf-8"))
                if isinstance(loaded_manifest, dict):
                    plugin_manifest = loaded_manifest
            except json.JSONDecodeError:
                plugin_manifest = None

        required_components: tuple[tuple[str, str], ...] = (
            ("agents", "agents"),
            ("skills", "skills"),
            ("hooks", "hooks.json"),
        )
        for component_key, default_relative in required_components:
            configured_relative = default_relative
            if plugin_manifest:
                configured_value = plugin_manifest.get(component_key)
                if isinstance(configured_value, str) and configured_value.strip():
                    configured_relative = configured_value
            component_path = plugin_root / configured_relative
            component_name = str(Path("plugins") / "omc-copilot" / Path(configured_relative))
            checks.append(
                (
                    "OK" if component_path.exists() else "MISSING",
                    component_name,
                    f"plugin component ({component_key})",
                )
            )
    else:
        checks.append(("INFO", "plugin-package-scope", "local plugin package checks skipped (consumer repository mode)"))
        if shutil.which("copilot"):
            checks.append(_check_plugin_installation())

    failed = False
    for status, name, info in checks:
        print(f"{status:8} {name:40} {info}")
        if status in {"MISSING", "INVALID"}:
            failed = True
    return 1 if failed else 0
