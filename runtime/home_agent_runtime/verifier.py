from __future__ import annotations

from typing import Any

from .models import ExecutionResult, HomeGraph, Intent


class Verifier:
    def verify(self, intent: Intent, home: HomeGraph) -> ExecutionResult:
        room = home.get_room(intent.room)
        device = home.get_device(intent.room, intent.device)
        action = device.actions[intent.action]
        rule = action.verify

        if not rule:
            return ExecutionResult(True, "verified", "No verification rule declared")

        if "state" in rule:
            expected = rule["state"]
            ok = device.state == expected
            return ExecutionResult(
                ok,
                "verified" if ok else "verification_failed",
                f"Device state is {device.state}; expected {expected}",
            )

        sensor_name = rule.get("sensor")
        if sensor_name:
            sensor = room.sensors[sensor_name]
            ok = _compare(sensor.state, rule["operator"], rule["value"])
            return ExecutionResult(
                ok,
                "verified" if ok else "verification_failed",
                f"{sensor.entity_id} is {sensor.state}; rule {rule['operator']} {rule['value']}",
            )

        return ExecutionResult(False, "verification_failed", "Unsupported verification rule")


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    if operator == ">":
        return actual > expected
    if operator == ">=":
        return actual >= expected
    if operator == "<":
        return actual < expected
    if operator == "<=":
        return actual <= expected
    if operator == "==":
        return actual == expected
    raise ValueError(f"Unsupported operator: {operator}")
