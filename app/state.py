from dataclasses import dataclass, field


@dataclass
class RuntimeState:
    rsi_states: dict = field(default_factory=dict)
    last_signals: dict = field(default_factory=dict)
