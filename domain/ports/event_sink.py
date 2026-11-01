# -*- coding: utf-8 -*-
"""Domain event sink interface."""

from typing import Protocol, Any


class EventSink(Protocol):
    def emit(self, event_type: str, data: Optional[dict[str, Any]] = None) -> None:
        ...
