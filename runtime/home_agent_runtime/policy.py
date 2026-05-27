from __future__ import annotations

from .models import ExecutionResult, HomeGraph, Intent


class PolicyEngine:
    def evaluate(self, intent: Intent, home: HomeGraph) -> ExecutionResult:
        try:
            room = home.get_room(intent.room)
            device = home.get_device(intent.room, intent.device)
            action = device.actions[intent.action]
        except KeyError as exc:
            return ExecutionResult(False, "rejected", str(exc))

        if action.risk_level in home.policy.deny_risk_levels:
            return ExecutionResult(
                False,
                "rejected",
                f"{intent.action} on {intent.device} is denied by risk policy",
                {"risk_level": action.risk_level},
            )

        if action.requires_confirmation or action.risk_level in home.policy.require_confirmation_for:
            return ExecutionResult(
                False,
                "confirmation_required",
                f"{intent.action} on {intent.device} requires human confirmation",
                {"risk_level": action.risk_level},
            )

        missing = [name for name in action.preconditions if not room.sensors.get(name)]
        if missing:
            return ExecutionResult(
                False,
                "rejected",
                "Missing required sensor preconditions",
                {"missing": missing},
            )

        if "presence" in action.preconditions and not room.sensors["presence"].state:
            return ExecutionResult(
                False,
                "rejected",
                "Presence is required for this action",
                {"sensor": room.sensors["presence"].entity_id},
            )

        return ExecutionResult(True, "accepted", "Policy accepted")
