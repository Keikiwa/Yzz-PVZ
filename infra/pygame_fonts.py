# -*- coding: utf-8 -*-
"""Pygame Font manager and pre-cached glyph repository.
Directly checks high quality system font paths to bypass pygame sysfont registry bugs on Windows.
"""

import os
from pathlib import Path
import pygame


class FontBank:
    _instance = None

    def __init__(self):
        pygame.font.init()
        self._cache: dict[tuple[int, bool], pygame.font.Font] = {}

        # Authoritative Windows Font locations
        self.regular_candidates = [
            Path(r"C:\Windows\Fonts\msyh.ttc"),
            Path(r"C:\Windows\Fonts\simhei.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
        ]
        self.bold_candidates = [
            Path(r"C:\Windows\Fonts\msyhbd.ttc"),
            Path(r"C:\Windows\Fonts\simhei.ttf"),
            Path(r"C:\Windows\Fonts\arialbd.ttf"),
        ]

        self.regular_path = next((p for p in self.regular_candidates if p.exists()), None)
        self.bold_path = next((p for p in self.bold_candidates if p.exists()), None)

    @classmethod
    def get_instance(cls) -> "FontBank":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self._cache:
            font_path = self.bold_path if bold and self.bold_path else self.regular_path
            if font_path and font_path.exists():
                try:
                    self._cache[key] = pygame.font.Font(str(font_path), size)
                except Exception:
                    self._cache[key] = pygame.font.Font(None, size)
            else:
                try:
                    self._cache[key] = pygame.font.SysFont("microsoftyahei,simhei,arial", size, bold=bold)
                except Exception:
                    self._cache[key] = pygame.font.Font(None, size)
        return self._cache[key]


def get_font(size: int = 20, bold: bool = False) -> pygame.font.Font:
    return FontBank.get_instance().get_font(size, bold)
