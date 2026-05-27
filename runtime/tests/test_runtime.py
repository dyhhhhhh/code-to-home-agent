from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from home_agent_runtime.config import load_home_graph
from home_agent_runtime.runtime import HomeAgentRuntime


def runtime() -> HomeAgentRuntime:
    return HomeAgentRuntime(load_home_graph(ROOT / "examples" / "home.yaml"))


def test_low_risk_fan_action_is_verified() -> None:
    result = runtime().handle("turn on the bedroom fan")

    assert result.status == "verified"
    assert "sensor.bedroom_fan_power" in result.message


def test_high_risk_lock_requires_confirmation() -> None:
    result = runtime().handle("unlock the front door")

    assert result.status == "confirmation_required"


def test_critical_gas_action_is_denied() -> None:
    result = runtime().handle("open kitchen gas")

    assert result.status == "rejected"
    assert result.details["risk_level"] == "critical"
