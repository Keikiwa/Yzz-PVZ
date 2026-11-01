# -*- coding: utf-8 -*-
"""Pygame Audio Manager.
Implements SoundPort with official soundtrack streaming and procedural sound synthesis.
"""

import math
import random
from array import array
from pathlib import Path
from typing import Optional
import pygame

from config.tuning import MUSIC_TRACKS, BASE_DIR
from domain.spec.math_util import clamp, lerp


class PygameAudioAdapter:
    SAMPLE_RATE = 44100

    def __init__(self, base_dir: Path = BASE_DIR):
        self.base_dir = base_dir
        self.enabled = True
        self.available = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.last_played: dict[str, float] = {}
        self.current_track: Optional[str] = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=2, buffer=2048)
            pygame.mixer.set_num_channels(16)
            self._init_synthesized_sounds()
            self.available = True
        except Exception:
            self.available = False

    def _tone(
        self, start_freq: float, end_freq: float, duration: float, volume: float, noise: float = 0.0
    ) -> pygame.mixer.Sound:
        sample_count = max(1, int(self.SAMPLE_RATE * duration))
        rng = random.Random(int(start_freq * 17 + end_freq * 3))
        data = array("h")
        phase = 0.0

        for i in range(sample_count):
            progress = i / sample_count
            freq = lerp(start_freq, end_freq, progress)
            phase += math.tau * freq / self.SAMPLE_RATE
            attack = min(1.0, i / max(1, self.SAMPLE_RATE * 0.012))
            release = max(0.0, 1.0 - progress) ** 0.7
            envelope = attack * release

            wave = math.sin(phase) * 0.75 + math.sin(phase * 2.01) * 0.18
            if noise > 0:
                wave += rng.uniform(-1.0, 1.0) * noise
            val = int(clamp(wave * volume * envelope, -1.0, 1.0) * 32767)
            data.append(val)
            data.append(val)

        return pygame.mixer.Sound(buffer=data.tobytes())

    def _init_synthesized_sounds(self) -> None:
        self.sounds = {
            "collect": self._tone(760, 1120, 0.16, 0.18, 0.0),
            "plant": self._tone(190, 290, 0.18, 0.12, 0.05),
            "click": self._tone(430, 390, 0.08, 0.06, 0.0),
            "explode": self._tone(95, 38, 0.70, 0.38, 0.45),
            "mower": self._tone(72, 118, 0.45, 0.35, 0.18),
            "win": self._tone(420, 880, 0.44, 0.30, 0.0),
            "lose": self._tone(220, 82, 0.55, 0.35, 0.06),
            "chomp": self._tone(150, 75, 0.16, 0.32, 0.25),
            "squash": self._tone(85, 38, 0.35, 0.45, 0.30),
            "vault": self._tone(280, 560, 0.24, 0.28, 0.08),
            "groan": self._tone(110, 160, 0.40, 0.32, 0.35),
            "splash": self._tone(320, 160, 0.28, 0.30, 0.35),
            "butter": self._tone(450, 220, 0.20, 0.38, 0.20),
        }

    def play_sound(self, sound_id: str, cooldown: float = 0.05) -> None:
        if not self.enabled or not self.available or sound_id not in self.sounds:
            return
        now = pygame.time.get_ticks() / 1000.0
        if cooldown > 0 and now - self.last_played.get(sound_id, -999.0) < cooldown:
            return
        self.last_played[sound_id] = now
        try:
            self.sounds[sound_id].play()
        except Exception:
            pass

    def play_music(self, track_name: str) -> None:
        if not self.enabled or not self.available:
            return
        if self.current_track == track_name and pygame.mixer.music.get_busy():
            return

        target_path = MUSIC_TRACKS.get(track_name)
        if not target_path or not target_path.exists():
            return

        try:
            pygame.mixer.music.load(str(target_path))
            pygame.mixer.music.set_volume(0.55)
            pygame.mixer.music.play(-1)
            self.current_track = track_name
        except Exception:
            pass

    def stop_music(self) -> None:
        if self.available:
            try:
                pygame.mixer.music.stop()
                self.current_track = None
            except Exception:
                pass
