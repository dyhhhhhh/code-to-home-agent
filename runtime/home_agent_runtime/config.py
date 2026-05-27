from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import ActionSpec, Device, HomeGraph, Policy, Room, Sensor


def load_home_graph(path: str | Path) -> HomeGraph:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    policy_data = data["policy"]
    policy = Policy(
        audit_log=policy_data.get("audit_log", "audit.log"),
        require_confirmation_for=policy_data.get("require_confirmation_for", []),
        deny_risk_levels=policy_data.get("deny_risk_levels", []),
        quiet_hours=policy_data.get("quiet_hours"),
        allow_medium_without_confirmation_when=policy_data.get(
            "allow_medium_without_confirmation_when", {}
        ),
    )

    rooms: dict[str, Room] = {}
    for room_name, room_data in data.get("rooms", {}).items():
        sensors = {
            sensor_name: Sensor(
                name=sensor_name,
                entity_id=sensor_data["entity_id"],
                state=sensor_data.get("state"),
                unit=sensor_data.get("unit"),
            )
            for sensor_name, sensor_data in room_data.get("sensors", {}).items()
        }

        devices: dict[str, Device] = {}
        for device_name, device_data in room_data.get("devices", {}).items():
            actions = {
                action_name: _load_action(action_name, action_data)
                for action_name, action_data in device_data.get("actions", {}).items()
            }
            devices[device_name] = Device(
                name=device_name,
                entity_id=device_data["entity_id"],
                type=device_data["type"],
                risk_level=device_data["risk_level"],
                state=device_data.get("state"),
                actions=actions,
                aliases=device_data.get("aliases", []),
            )

        rooms[room_name] = Room(
            name=room_name,
            sensors=sensors,
            devices=devices,
            aliases=room_data.get("aliases", []),
        )

    return HomeGraph(
        name=data["home"]["name"],
        default_user=data["home"].get("default_user", "owner"),
        policy=policy,
        rooms=rooms,
    )


def _load_action(action_name: str, action_data: dict[str, Any]) -> ActionSpec:
    return ActionSpec(
        name=action_name,
        risk_level=action_data["risk_level"],
        requires_confirmation=action_data.get("requires_confirmation", False),
        service=action_data["service"],
        preconditions=action_data.get("preconditions", []),
        verify=action_data.get("verify", {}),
    )
