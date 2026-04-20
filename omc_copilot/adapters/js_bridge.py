"""Minimal Node.js interoperability adapter for omc-copilot.

This module provides a tiny shim to run Node.js scripts/code from Python and
exchange JSON via stdin/stdout. It's intentionally small and dependency-free.

Usage:
    from omc_copilot.adapters.js_bridge import run_js_code
    out = run_js_code("console.log(JSON.stringify({ok: true, echo: {foo: 'bar'}}));")

Functions:
- run_js_script(script_path, input_obj=None, timeout=10, use_docker=False, docker_image='node:18-slim', memory_mb=256, cpus=0.5)
- run_js_code(code_str, input_obj=None, timeout=10, use_docker=False, docker_image='node:18-slim', memory_mb=256, cpus=0.5)

Notes:
- Requires Node.js (v16+) available on PATH for direct execution, or Docker for containerized execution.
- The adapter will raise JSBridgeError if required executables are not found.
- Running untrusted JS is a security risk; prefer containerized execution (use_docker=True) where possible.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from typing import Any, Optional


class JSBridgeError(RuntimeError):
    """Raised for any adapter-level error."""


def _ensure_executable_available(name: str) -> None:
    """Raise JSBridgeError if the given executable is not on PATH."""
    if shutil.which(name) is None:
        raise JSBridgeError(
            f"Executable '{name}' not found on PATH. Install it and ensure it's on PATH."
        )


def _limit_resources_preexec(memory_mb: int, cpu_seconds: int):
    """Return a preexec_fn that applies basic RLIMITs on POSIX systems.

    This is best-effort and will silently no-op on platforms that do not
    support the resource module or specific RLIMITs.

    Note: RLIMIT_AS (address space) is intentionally NOT set because some
    platforms and Node/V8 require large virtual address reservations that
    cause failures when RLIMIT_AS is too restrictive. Prefer using Docker
    for memory isolation (use_docker=True).
    """

    def _limit():
        try:
            import resource

            # limit CPU seconds only; do NOT set RLIMIT_AS because V8 may need
            # large virtual memory reservations even when physical memory usage
            # is small. Memory isolation should be provided via Docker.
            if hasattr(resource, "RLIMIT_CPU"):
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        except Exception:
            # best effort; don't fail the parent process if resource limiting isn't available
            pass

    return _limit


def _run_node_process(
    cmd: list[str],
    input_obj: Optional[Any],
    timeout: int,
    *,
    memory_mb: int = 256,
    cpu_seconds: int = 10,
) -> Any:
    """Run the given command (list) with JSON stdin/stdout semantics and basic resource limits.

    The first element of `cmd` is validated to exist on PATH.
    """
    _ensure_executable_available(cmd[0])

    input_bytes = None
    if input_obj is not None:
        try:
            input_bytes = json.dumps(input_obj).encode("utf-8")
        except Exception as e:
            raise JSBridgeError(f"failed to serialize input: {e}")

    preexec = None
    if os.name != "nt":
        preexec = _limit_resources_preexec(memory_mb, cpu_seconds)

    try:
        proc = subprocess.run(
            cmd,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            preexec_fn=preexec,
        )
    except subprocess.TimeoutExpired as e:
        raise JSBridgeError(f"process timed out: {e}")
    except FileNotFoundError as e:
        raise JSBridgeError(f"executable not found or not executable: {e}")
    except OSError as e:
        raise JSBridgeError(f"process failed to start: {e}")

    if proc.returncode != 0:
        stderr = proc.stderr.decode(errors="replace")
        raise JSBridgeError(f"process failed (rc={proc.returncode}): {stderr}")

    out = proc.stdout.decode("utf-8").strip()
    if not out:
        return None

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def _run_node_in_docker(
    script_path: str,
    input_obj: Optional[Any],
    timeout: int,
    *,
    image: str = "node:18-slim",
    memory_mb: int = 256,
    cpus: float = 0.5,
) -> Any:
    """Run a script inside a Docker container to provide basic isolation.

    This requires `docker` to be present on PATH and will bind-mount the
    script's parent directory into /workspace as read-only. Network access is
    disabled via --network none and simple resource flags are provided.
    """
    _ensure_executable_available("docker")

    dirpath = os.path.abspath(os.path.dirname(script_path))
    script_name = os.path.basename(script_path)

    cmd = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--network",
        "none",
        "-v",
        f"{dirpath}:/workspace:ro",
        "-w",
        "/workspace",
        "--memory",
        f"{memory_mb}m",
        "--cpus",
        str(cpus),
        image,
        "node",
        script_name,
    ]

    # Run the docker binary; _run_node_process will validate docker exists.
    return _run_node_process(
        cmd, input_obj, timeout, memory_mb=memory_mb, cpu_seconds=max(1, int(timeout))
    )


def run_js_script(
    script_path: str,
    input_obj: Optional[Any] = None,
    timeout: int = 10,
    *,
    use_docker: bool = False,
    docker_image: str = "node:18-slim",
    memory_mb: int = 256,
    cpus: float = 0.5,
) -> Any:
    """Run a Node.js script file and return parsed JSON (or raw stdout).

    If `use_docker` is True the script will be executed inside a Docker container
    (requires docker on PATH). `memory_mb` and `cpus` are applied to the container
    when using Docker and as best-effort RLIMITs when executing directly.
    """
    if not os.path.isfile(script_path):
        raise JSBridgeError(f"script not found: {script_path}")

    if use_docker:
        return _run_node_in_docker(
            script_path,
            input_obj,
            timeout,
            image=docker_image,
            memory_mb=memory_mb,
            cpus=cpus,
        )

    return _run_node_process(
        ["node", script_path],
        input_obj,
        timeout,
        memory_mb=memory_mb,
        cpu_seconds=max(1, int(timeout)),
    )


def run_js_code(
    code_str: str,
    input_obj: Optional[Any] = None,
    timeout: int = 10,
    *,
    use_docker: bool = False,
    docker_image: str = "node:18-slim",
    memory_mb: int = 256,
    cpus: float = 0.5,
) -> Any:
    """Run a snippet of JS code by writing it to a temporary file and executing node.

    Set `use_docker=True` to run inside a container which provides basic isolation
    (requires Docker). This function ensures the required binary is available
    before writing the temporary file so callers get early failures.
    """
    if use_docker:
        _ensure_executable_available("docker")
    else:
        _ensure_executable_available("node")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(code_str)
        tmp_path = f.name

    try:
        return run_js_script(
            tmp_path,
            input_obj=input_obj,
            timeout=timeout,
            use_docker=use_docker,
            docker_image=docker_image,
            memory_mb=memory_mb,
            cpus=cpus,
        )
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


if __name__ == "__main__":
    # simple CLI for manual testing
    import argparse

    parser = argparse.ArgumentParser(
        description="Run small JS snippets and return JSON or stdout."
    )
    parser.add_argument("--code", help="JS code to run (inlined)")
    parser.add_argument("--file", help="Path to a JS file to run")
    parser.add_argument("--input", help="JSON input to send to the script")
    parser.add_argument(
        "--use-docker",
        action="store_true",
        help="Run the code inside a Docker container (requires docker)",
    )
    parser.add_argument(
        "--docker-image",
        default="node:18-slim",
        help="Docker image to use when --use-docker is supplied",
    )
    parser.add_argument(
        "--memory",
        type=int,
        default=256,
        help="Memory limit in MiB for container or RLIMIT_AS",
    )
    parser.add_argument(
        "--cpus", type=float, default=0.5, help="CPU limit for container (e.g., 0.5)"
    )
    args = parser.parse_args()

    input_obj = None
    if args.input:
        input_obj = json.loads(args.input)

    if args.code:
        res = run_js_code(
            args.code,
            input_obj=input_obj,
            use_docker=args.use_docker,
            docker_image=args.docker_image,
            memory_mb=args.memory,
            cpus=args.cpus,
        )
    elif args.file:
        res = run_js_script(
            args.file,
            input_obj=input_obj,
            use_docker=args.use_docker,
            docker_image=args.docker_image,
            memory_mb=args.memory,
            cpus=args.cpus,
        )
    else:
        parser.error("either --code or --file must be provided")

    if isinstance(res, (dict, list)):
        print(json.dumps(res))
    elif res is None:
        pass
    else:
        print(res)
