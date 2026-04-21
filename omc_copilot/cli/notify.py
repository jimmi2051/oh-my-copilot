"""CLI helpers for configuring and sending notifications.

This is a minimal, self-contained helper that writes a simple .omc/notify_config.json
in the current working directory. The real project CLI can import and integrate these
functions into the main CLI entrypoint.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional

from omc_copilot.notifications import WebhookNotifier

CONFIG_PATH = Path(os.getcwd()) / ".omc" / "notify_config.json"


def load_config() -> Dict[str, str]:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open() as fh:
        return json.load(fh)


def save_config(cfg: Dict[str, str]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w") as fh:
        json.dump(cfg, fh, indent=2)


def cmd_config_set(provider: str, webhook: str) -> None:
    cfg = load_config()
    cfg[provider] = webhook
    save_config(cfg)
    print(f"Saved webhook for provider {provider} to {CONFIG_PATH}")


def cmd_config_get(provider: str) -> None:
    cfg = load_config()
    print(cfg.get(provider))


def cmd_send(provider: str, message: str, tags: Optional[str] = None) -> int:
    cfg = load_config()
    webhook = cfg.get(provider)
    if not webhook:
        print(f"No webhook configured for provider {provider}. Use `notify config set` first.")
        return 2
    notifier = WebhookNotifier(webhook, provider=provider)
    ok = notifier.send_sync(message, tags=tags)
    print("Sent" if ok else "Failed")
    return 0 if ok else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="omc-copilot notify")
    sub = parser.add_subparsers(dest="sub")

    p_config = sub.add_parser("config", help="configure webhooks")
    p_config.add_argument("action", choices=["set", "get"]) 
    p_config.add_argument("--provider", required=True)
    p_config.add_argument("--webhook")

    p_send = sub.add_parser("send", help="send a notification")
    p_send.add_argument("--provider", required=True)
    p_send.add_argument("--message", required=True)
    p_send.add_argument("--tags")

    args = parser.parse_args(argv)
    if args.sub == "config":
        if args.action == "set":
            cmd_config_set(args.provider, args.webhook)
            return 0
        if args.action == "get":
            cmd_config_get(args.provider)
            return 0
    if args.sub == "send":
        return cmd_send(args.provider, args.message, tags=args.tags)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
