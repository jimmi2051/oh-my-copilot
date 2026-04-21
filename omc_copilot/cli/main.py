from __future__ import annotations

import argparse
import sys
from pathlib import Path

from omc_copilot.cli.commands.ask import run_ask
from omc_copilot.cli.commands.doctor import run_doctor
from omc_copilot.cli.commands.hud import run_hud
from omc_copilot.cli.commands.parity import run_parity_inventory
from omc_copilot.cli.commands.run import run_task
from omc_copilot.cli.commands.session import run_session_search
from omc_copilot.cli.commands.setup import run_setup
from omc_copilot.cli.commands.team import run_team
from omc_copilot.cli.notify import main as notify_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omc-copilot")
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Run autopilot orchestration loop")
    run_cmd.add_argument("task", help="Task prompt")
    run_cmd.add_argument(
        "--mode", default=None, help="Mode override (autopilot/team/ralph)"
    )
    run_cmd.add_argument("--max-iterations", type=int, default=8)
    run_cmd.add_argument("--cwd", default=".")

    setup_cmd = sub.add_parser(
        "setup", help="Install OMC-style Copilot instructions for plugin-first workflow"
    )
    setup_cmd.add_argument("--target", default=".")
    setup_cmd.add_argument(
        "--plugin-guidance",
        action="store_true",
        help="Print a copilot plugin install command after setup",
    )

    ask_cmd = sub.add_parser("ask", help="Ask Copilot directly")
    ask_cmd.add_argument("prompt")
    ask_cmd.add_argument("--cwd", default=".")

    team_cmd = sub.add_parser("team", help="Team-compatible orchestration mode")
    team_cmd.add_argument("task")
    team_cmd.add_argument("--max-iterations", type=int, default=10)
    team_cmd.add_argument("--cwd", default=".")

    notify_cmd = sub.add_parser("notify", help="Notification configuration and send")

    session_cmd = sub.add_parser("session", help="Session operations")
    session_sub = session_cmd.add_subparsers(dest="session_cmd", required=True)
    session_search = session_sub.add_parser("search")
    session_search.add_argument("query")
    session_search.add_argument("--project-root", default=".")

    doctor_cmd = sub.add_parser("doctor", help="Check installation health")
    doctor_cmd.add_argument("--project-root", default=".")

    hud_cmd = sub.add_parser("hud", help="Print runtime HUD")
    hud_cmd.add_argument("--project-root", default=".")

    parity_cmd = sub.add_parser(
        "parity-inventory", help="Extract parity inventory from oh-my-claudecode"
    )
    parity_cmd.add_argument("--omc-root", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return run_task(
            args.task, args.mode, args.max_iterations, Path(args.cwd).resolve()
        )
    if args.command == "setup":
        return run_setup(
            Path(args.target).resolve(), plugin_guidance=args.plugin_guidance
        )
    if args.command == "ask":
        return run_ask(args.prompt, Path(args.cwd).resolve())
    if args.command == "team":
        return run_team(args.task, Path(args.cwd).resolve(), args.max_iterations)
    if args.command == "session" and args.session_cmd == "search":
        return run_session_search(args.query, Path(args.project_root).resolve())
    if args.command == "doctor":
        return run_doctor(Path(args.project_root).resolve())
    if args.command == "hud":
        return run_hud(Path(args.project_root).resolve())
    if args.command == "parity-inventory":
        return run_parity_inventory(Path(args.omc_root).resolve())
    if args.command == "notify":
        sub_argv = None
        if argv is None:
            sub_argv = sys.argv[2:]
        else:
            sub_argv = argv[1:]
        return notify_main(sub_argv)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
