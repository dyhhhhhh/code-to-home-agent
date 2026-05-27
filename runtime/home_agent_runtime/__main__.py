from __future__ import annotations

import argparse

from .config import load_home_graph
from .runtime import HomeAgentRuntime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Home Agent Runtime prototype.")
    parser.add_argument("--config", required=True, help="Path to a home runtime config.")
    parser.add_argument("--request", required=True, help="User request to handle.")
    args = parser.parse_args()

    home = load_home_graph(args.config)
    runtime = HomeAgentRuntime(home)
    result = runtime.handle(args.request)
    print(f"{result.status}: {result.message}")
    if result.details:
        print(result.details)


if __name__ == "__main__":
    main()
