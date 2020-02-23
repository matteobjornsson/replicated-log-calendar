#this is my attempt to make an immutable event object

from dataclasses import dataclass

@dataclass(frozen=True)
class EventRecord:
    event: str
    time: int
    node: int
