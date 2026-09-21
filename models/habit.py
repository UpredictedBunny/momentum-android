"""Habit model — lightweight data container."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Habit:
    id: int
    name: str
    icon: str
    is_completed: bool

    @classmethod
    def from_dict(cls, d: dict) -> "Habit":
        return cls(
            id=d["id"],
            name=d["name"],
            icon=d.get("icon", ""),
            is_completed=bool(d.get("is_completed", 0)),
        )


@dataclass
class RoutineItem:
    id: int
    name: str
    period: str
    est_minutes: int
    is_completed: bool

    @classmethod
    def from_dict(cls, d: dict) -> "RoutineItem":
        return cls(
            id=d["id"],
            name=d["name"],
            period=d.get("period", "morning"),
            est_minutes=d.get("est_minutes", 0),
            is_completed=bool(d.get("is_completed", 0)),
        )
