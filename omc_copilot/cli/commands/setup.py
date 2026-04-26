from __future__ import annotations

from pathlib import Path

from omc_copilot.adapters.runtime_factory import (
    includes_codex,
    includes_copilot,
    resolve_runtime_name,
)
from omc_copilot.installer.setup_wizard import SetupWizard

PLUGIN_MANIFEST_RELATIVE_PATH = Path("plugins") / "omc-copilot" / "plugin.json"


def _resolve_package_root(package_root: Path | None) -> Path:
    return package_root or Path(__file__).resolve().parents[2]


def _plugin_manifest_path(package_root: Path) -> Path:
    candidates = (
        package_root.parent / PLUGIN_MANIFEST_RELATIVE_PATH,
        package_root / PLUGIN_MANIFEST_RELATIVE_PATH,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def run_setup(
    target: Path,
    plugin_guidance: bool = False,
    package_root: Path | None = None,
    runtime_name: str | None = None,
    codex_skills_dir: Path | None = None,
) -> int:
    resolved_runtime = resolve_runtime_name(runtime_name, allow_both=True)
    package_root = _resolve_package_root(package_root)
    plugin_manifest = _plugin_manifest_path(package_root)
    plugin_present = plugin_manifest.exists()
    if includes_copilot(resolved_runtime):
        status = "OK" if plugin_present else "MISSING"
        print(
            f"{status:8} {str(PLUGIN_MANIFEST_RELATIVE_PATH):40} plugin package manifest"
        )
        if not plugin_present:
            print(
                "Setup aborted: copilot runtime setup requires "
                "plugins/omc-copilot/plugin.json."
            )
            return 1
    else:
        print(
            f"SKIPPED  {str(PLUGIN_MANIFEST_RELATIVE_PATH):40} "
            "plugin package manifest (codex runtime)"
        )

    result = SetupWizard(package_root=package_root).run(
        target_root=target,
        runtime_name=resolved_runtime,
        codex_skills_dir=codex_skills_dir,
    )
    print(f"Setup completed for {result.target_root}")
    print(f"- runtime: {resolved_runtime}")
    for path in result.instruction_files:
        print(f"- installed: {path}")
    print(f"- hook manifest: {result.hook_manifest}")
    if includes_codex(resolved_runtime):
        for path in result.codex_skill_dirs:
            print(f"- codex skill: {path}")
    if plugin_guidance and includes_copilot(resolved_runtime):
        print("Plugin install guidance:")
        print(f"copilot plugin install {plugin_manifest.parent}")
    elif plugin_guidance:
        print("Plugin install guidance skipped for codex runtime.")
    return 0
