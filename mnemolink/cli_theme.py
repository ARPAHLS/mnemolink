"""Presentation palettes for the MnemoLink CLI (pastel / ocean / mono)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ThemePalette:
    heading_style: str
    id_style: str
    border_style: str
    splash_style: str
    menu_style: str
    error_color: str
    pink: str
    blue: str
    mint: str
    peach: str
    lavender: str
    gradient_start: Tuple[int, int, int]
    gradient_mid: Tuple[int, int, int]
    gradient_end: Tuple[int, int, int]


THEMES: Dict[str, ThemePalette] = {
    "pastel": ThemePalette(
        heading_style="bold #efcefa",
        id_style="#bbf7d0",
        border_style="#cfc8dc",
        splash_style="#cfc8dc",
        menu_style="#ffdac1",
        error_color="#FF9AA2",
        pink="#efcefa",
        blue="#bae6fd",
        mint="#bbf7d0",
        peach="#ffdac1",
        lavender="#cfc8dc",
        # Issue #1 splash stops: pink -> blue -> mint
        gradient_start=(0xEF, 0xCE, 0xFA),
        gradient_mid=(0xBA, 0xE6, 0xFD),
        gradient_end=(0xBB, 0xF7, 0xD0),
    ),
    "ocean": ThemePalette(
        heading_style="bold #7DD3FC",
        id_style="#BAE6FD",
        border_style="#0284C7",
        splash_style="#38BDF8",
        menu_style="#7DD3FC",
        error_color="#F87171",
        pink="#7DD3FC",
        blue="#38BDF8",
        mint="#BAE6FD",
        peach="#7DD3FC",
        lavender="#0284C7",
        gradient_start=(0x0C, 0x4A, 0x6E),
        gradient_mid=(0x02, 0x84, 0xC7),
        gradient_end=(0x7D, 0xD3, 0xFC),
    ),
    "mono": ThemePalette(
        heading_style="bold #D0D0D0",
        id_style="#E0E0E0",
        border_style="#808080",
        splash_style="#C0C0C0",
        menu_style="#A8A8A8",
        error_color="#B0B0B0",
        pink="#D0D0D0",
        blue="#A8A8A8",
        mint="#E0E0E0",
        peach="#C0C0C0",
        lavender="#808080",
        gradient_start=(0xF0, 0xF0, 0xF0),
        gradient_mid=(0xA0, 0xA0, 0xA0),
        gradient_end=(0x60, 0x60, 0x60),
    ),
}

_ACTIVE_THEME = "pastel"


def theme_name() -> str:
    return _ACTIVE_THEME


def palette() -> ThemePalette:
    return THEMES.get(_ACTIVE_THEME, THEMES["pastel"])


def set_theme(name: str) -> bool:
    """Switch the in-session palette. Returns False if the name is unknown."""
    global _ACTIVE_THEME
    key = name.strip().lower()
    if key not in THEMES:
        return False
    _ACTIVE_THEME = key
    return True
