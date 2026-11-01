# -*- coding: utf-8 -*-
"""Settings and preferences toggle use cases."""

from domain.model.session import Session


def toggle_auto_sun(session: Session) -> bool:
    if session.has_auto_sun:
        session.auto_sun_enabled = not session.auto_sun_enabled
        return session.auto_sun_enabled
    return False


def toggle_game_speed(session: Session) -> float:
    session.speed_multiplier = 2.0 if session.speed_multiplier == 1.0 else 1.0
    return session.speed_multiplier


def toggle_music(session: Session) -> bool:
    session.music_enabled = not session.music_enabled
    return session.music_enabled


def toggle_sound(session: Session) -> bool:
    session.sound_enabled = not session.sound_enabled
    return session.sound_enabled
