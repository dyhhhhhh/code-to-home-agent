from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from home_agent_runtime.config import load_home_graph
from home_agent_runtime.runtime import HomeAgentRuntime


def run_case(request: str, expected_status: str) -> None:
    runtime = HomeAgentRuntime(load_home_graph(ROOT / "examples" / "home.yaml"))
    result = runtime.handle(request)
    if result.status != expected_status:
        raise AssertionError(
            f"{request!r}: expected {expected_status}, got {result.status}: {result.message}"
        )
    print(f"ok: {request} -> {result.status}")


def main() -> None:
    run_case("turn on the bedroom fan", "verified")
    run_case("turn on bedroom light", "verified")
    run_case("unlock the front door", "confirmation_required")
    run_case("open kitchen gas", "rejected")


if __name__ == "__main__":
    main()
