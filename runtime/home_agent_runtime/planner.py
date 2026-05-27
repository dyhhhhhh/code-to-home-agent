from __future__ import annotations

from .models import HomeGraph, Intent


class RulePlanner:
    """Small placeholder planner until an LLM client is connected."""

    def plan(self, request: str, home: HomeGraph) -> Intent:
        text = request.lower()
        room = self._first_room(text, home)
        device = self._first_device(text, home, room)
        action = self._infer_action(text, device)
        return Intent(action=action, room=room, device=device, raw_request=request)

    def _first_room(self, text: str, home: HomeGraph) -> str:
        for room_name, room in home.rooms.items():
            if room_name.replace("_", " ") in text:
                return room_name
            if any(alias in text for alias in room.aliases):
                return room_name
        return next(iter(home.rooms))

    def _first_device(self, text: str, home: HomeGraph, room_name: str) -> str:
        room = home.get_room(room_name)
        for device_name, device in room.devices.items():
            if device_name.replace("_", " ") in text or device.type in text:
                return device_name
            if any(alias in text for alias in device.aliases):
                return device_name
        return next(iter(room.devices))

    def _infer_action(self, text: str, device: str) -> str:
        if any(word in text for word in ["off", "stop", "close", "turn down"]):
            return "turn_off"
        if "unlock" in text:
            return "unlock"
        if "open" in text and "gas" in text:
            return "open"
        if any(word in text for word in ["temperature", "cool", "heat"]):
            return "set_temperature"
        if any(word in text for word in ["on", "start", "turn on", "hot"]):
            return "turn_on"
        return "turn_on" if device else "observe"
