from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    goal: str
    number: str

@dataclass
class Action:
    type: str
    voice: Optional[str]
    keys: Optional[str]


@dataclass
class AgentTask:
    name: str
    goal: str