from __future__ import annotations

import json
from pathlib import Path

from omc_copilot.compatibility.hook_registry import supported_hook_events


class HookInstaller:
    def install_manifest(self, target_root: Path) -> Path:
        manifest = {
            "name": "omc-copilot",
            "events": supported_hook_events(),
        }
        manifest_path = target_root / ".omc" / "hooks" / "omc-copilot-hooks.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path
