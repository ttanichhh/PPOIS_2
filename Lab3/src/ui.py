from __future__ import annotations

import pygame


class TextRenderer:
    def __init__(self, screen: pygame.Surface, color: tuple[int, int, int]) -> None:
        self.screen = screen
        self.color = color
        self.font = pygame.font.SysFont('Arial', 28)
        self.big_font = pygame.font.SysFont('Arial', 46, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 22)

    def center(self, text: str, y: int, *, big: bool = False, small: bool = False) -> None:
        font = self.big_font if big else self.small_font if small else self.font
        surface = font.render(text, True, self.color)
        rect = surface.get_rect(center=(self.screen.get_width() // 2, y))
        self.screen.blit(surface, rect)

    def left(self, text: str, x: int, y: int, *, small: bool = False) -> None:
        font = self.small_font if small else self.font
        surface = font.render(text, True, self.color)
        self.screen.blit(surface, (x, y))
