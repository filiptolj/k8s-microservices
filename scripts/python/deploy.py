#!/usr/bin/env python3
"""Docker-based deployment script for the task microservices.

Usage:
    ./deploy.py --version_service1=1.0.0 --version_service2=1.0.1 [OPTIONS]

Options:
    --version_service1    Version tag for service1 image  (required)
    --version_service2    Version tag for service2 image  (required)
    --registry            Docker registry prefix           (default: filee/task)
    --port_service1       Host port exposed for service1   (default: 8081)
    --port_service2       Host port exposed for service2   (default: 8082)
    --startup_timeout     Startup health-check timeout (s) (default: 15)
    --cleanup             Stop and remove containers on exit

Examples:
    ./deploy.py --version_service1=1.0.0 --version_service2=1.0.1
    ./deploy.py --version_service1=1.0.0 --version_service2=1.0.1 \\
                --registry=myuser/task --port_service2=9090 --startup_timeout=30
"""

import argparse
import socket
import subprocess
import sys
import time

NETWORK_NAME = "task-network"
CONTAINER_SERVICE1 = "task-service1"
CONTAINER_SERVICE2 = "task-service2"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=False)


def docker_remove(name: str) -> None:
    """Force-remove a container, ignoring errors if it does not exist."""
    subprocess.run(
        ["docker", "rm", "-f", name],
        capture_output=True,
    )


def network_exists(name: str) -> bool:
    result = subprocess.run(
        ["docker", "network", "inspect", name],
        capture_output=True,
    )
    return result.returncode == 0


def wait_for_port(host: str, port: int, timeout: int) -> bool:
    """Poll until a TCP port accepts connections or the timeout is reached."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy task microservices using Docker.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version_service1", required=True, help="Version tag for service1"
    )
    parser.add_argument(
        "--version_service2", required=True, help="Version tag for service2"
    )
    parser.add_argument(
        "--registry", default="filee/task", help="Docker registry prefix (default: filee/task)"
    )
    parser.add_argument(
        "--port_service1", type=int, default=8081, help="Host port for service1 (default: 8081)"
    )
    parser.add_argument(
        "--port_service2", type=int, default=8082, help="Host port for service2 (default: 8082)"
    )
    parser.add_argument(
        "--startup_timeout",
        type=int,
        default=15,
        metavar="SECONDS",
        help="Startup health-check timeout in seconds (default: 15)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Stop and remove containers (and network) when the script exits",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    image1 = f"{args.registry}:service1-{args.version_service1}"
    image2 = f"{args.registry}:service2-{args.version_service2}"
    startup_timeout = args.startup_timeout

    print("\n=== Deploying microservices ===")
    print(f"  service1 : {image1}  ->  localhost:{args.port_service1}")
    print(f"  service2 : {image2}  ->  localhost:{args.port_service2}")
    print(f"  timeout  : {startup_timeout}s")

    try:
        print("\n[1/5] Setting up Docker network ...")
        if network_exists(NETWORK_NAME):
            print(f"  Network '{NETWORK_NAME}' already exists.")
        else:
            run(["docker", "network", "create", NETWORK_NAME])

        print("\n[2/5] Pulling images ...")
        run(["docker", "pull", image1])
        run(["docker", "pull", image2])

        print("\n[3/5] Starting service1 ...")
        docker_remove(CONTAINER_SERVICE1)
        run([
            "docker", "run", "-d",
            "--name", CONTAINER_SERVICE1,
            "--network", NETWORK_NAME,
            "-p", f"{args.port_service1}:8080",
            image1,
        ])

        print("\n[4/5] Starting service2 ...")
        docker_remove(CONTAINER_SERVICE2)
        run([
            "docker", "run", "-d",
            "--name", CONTAINER_SERVICE2,
            "--network", NETWORK_NAME,
            "-p", f"{args.port_service2}:8080",
            "-e", f"SERVICE1_URL=http://{CONTAINER_SERVICE1}:8080",
            image2,
        ])

        print(f"\n[5/5] Waiting for services to become ready (timeout: {startup_timeout}s) ...")
        checks = [
            ("service1", "localhost", args.port_service1),
            ("service2", "localhost", args.port_service2),
        ]
        failed = False
        for name, host, port in checks:
            if wait_for_port(host, port, startup_timeout):
                print(f"  OK  {name} is up at {host}:{port}")
            else:
                print(f"  ERR {name} did not become ready within {startup_timeout}s")
                failed = True

        if failed:
            sys.exit(1)

        print("\n=== Deployment successful! ===")
        print(f"  service1 : http://localhost:{args.port_service1}")
        print(f"  service2 : http://localhost:{args.port_service2}")
        print()
        print("Test service2 (ISO date):")
        print(f"  echo 'iso' | curl -sf -X POST http://localhost:{args.port_service2} --data-binary @-")
        print()
        print("Stop services:")
        print(f"  docker rm -f {CONTAINER_SERVICE1} {CONTAINER_SERVICE2}")

    except subprocess.CalledProcessError as exc:
        print(f"\nError: command failed with exit code {exc.returncode}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.cleanup:
            print("\nCleaning up ...")
            docker_remove(CONTAINER_SERVICE1)
            docker_remove(CONTAINER_SERVICE2)
            subprocess.run(["docker", "network", "rm", NETWORK_NAME], capture_output=True)
            print("  Done.")


if __name__ == "__main__":
    main()
