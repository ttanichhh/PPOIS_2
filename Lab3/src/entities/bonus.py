from __future__ import annotations

import pygame


class Bonus:
    def __init__(self, x: int, y: int, bonus_type: str) -> None:
        self.rect = pygame.Rect(x, y, 24, 24)
        self.speed = 3
        self.bonus_type = bonus_type

    def update(self) -> None:
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface) -> None:
        color = (78, 162, 52) if self.bonus_type == 'expand' else (50, 156, 135)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)
