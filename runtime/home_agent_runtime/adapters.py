from __future__ import annotations

from .models import ExecutionResult, HomeGraph, Intent


class DryRunHomeAssistantAdapter:
    """Mutates the in-memory home graph as if Home Assistant accepted the call."""

    def execute(self, intent: Intent, home: HomeGraph) -> ExecutionResult:
        device = home.get_device(intent.room, intent.device)
        action = device.actions[intent.action]
        verify = action.verify

        if "simulate_state" in verify:
            device.state = verify["simulate_state"]

        sensor_name = verify.get("sensor")
        if sensor_name and "simulate_sensor_value" in verify:
            room = home.get_room(intent.room)
            room.sensors[sensor_name].state = verify["simulate_sensor_value"]

        return ExecutionResult(
            True,
            "executed",
            "Dry-run adapter executed service",
            {
                "service": action.service,
                "entity_id": device.entity_id,
                "params": intent.params,
            },
        )
