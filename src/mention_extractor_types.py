from dataclasses import dataclass


@dataclass(frozen=True)
class Mention:
    text: str
    start: int
    end: int
    label: str
    gender: str = "unknown"
    number: str = "singular"
