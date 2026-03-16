from __future__ import annotations

import pygame


class Paddle:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        speed: int,
        screen_width: int,
        color: tuple[int, int, int],
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.screen_width = screen_width
        self.color = color

    def move(self, direction: int) -> None:
        self.rect.x += direction * self.speed
        self.rect.x = max(0, min(self.rect.x, self.screen_width - self.rect.width))

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (166, 98, 53), self.rect, 2, border_radius=8)
