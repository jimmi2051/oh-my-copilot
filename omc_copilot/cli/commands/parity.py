from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from omc_copilot.compatibility.parity_inventory import \
    generate_parity_inventory


def run_parity_inventory(omc_root: Path) -> int:
    inventory = generate_parity_inventory(omc_root)
    print(json.dumps(asdict(inventory), indent=2))
    return 0
