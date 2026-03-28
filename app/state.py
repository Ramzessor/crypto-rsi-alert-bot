from dataclasses import dataclass


@dataclass
class RuntimeState:
    rsi_states: dict
    last_signals: dict
    history_buffers: dict
