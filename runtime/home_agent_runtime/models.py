from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


@dataclass
class Sensor:
    name: str
    entity_id: str
    state: Any
    unit: str | None = None


@dataclass
class ActionSpec:
    name: str
    risk_level: str
    requires_confirmation: bool
    service: str
    preconditions: list[str] = field(default_factory=list)
    verify: dict[str, Any] = field(default_factory=dict)


@dataclass
class Device:
    name: str
    entity_id: str
    type: str
    risk_level: str
    state: Any
    actions: dict[str, ActionSpec]
    aliases: list[str] = field(default_factory=list)


@dataclass
class Room:
    name: str
    sensors: dict[str, Sensor]
    devices: dict[str, Device]
    aliases: list[str] = field(default_factory=list)


@dataclass
class Policy:
    audit_log: str
    require_confirmation_for: list[str]
    deny_risk_levels: list[str]
    quiet_hours: dict[str, str] | None = None
    allow_medium_without_confirmation_when: dict[str, Any] = field(default_factory=dict)


@dataclass
class HomeGraph:
    name: str
    default_user: str
    policy: Policy
    rooms: dict[str, Room]

    def get_room(self, room_name: str) -> Room:
        if room_name not in self.rooms:
            raise KeyError(f"Unknown room: {room_name}")
        return self.rooms[room_name]

    def get_device(self, room_name: str, device_name: str) -> Device:
        room = self.get_room(room_name)
        if device_name not in room.devices:
            raise KeyError(f"Unknown device in {room_name}: {device_name}")
        return room.devices[device_name]


@dataclass
class Intent:
    action: str
    room: str
    device: str
    params: dict[str, Any] = field(default_factory=dict)
    raw_request: str = ""


@dataclass
class ExecutionResult:
    accepted: bool
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
