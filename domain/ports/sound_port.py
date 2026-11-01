# -*- coding: utf-8 -*-
"""Sound port interface."""

from typing import Protocol


class SoundPort(Protocol):
    def play_sound(self, sound_id: str) -> None:
        ...

    def play_music(self, track_name: str) -> None:
        ...

    def stop_music(self) -> None:
        ...
