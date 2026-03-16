from __future__ import annotations

import pygame


class Ball:
    def __init__(
        self,
        x: float,
        y: float,
        radius: int,
        speed_x: float,
        speed_y: float,
        color: tuple[int, int, int],
    ) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.base_speed_x = speed_x
        self.base_speed_y = speed_y
        self.color = color

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self) -> None:
        self.x += self.speed_x
        self.y += self.speed_y

    def bounce_x(self) -> None:
        self.speed_x *= -1

    def bounce_y(self) -> None:
        self.speed_y *= -1

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (166, 98, 53), (int(self.x), int(self.y)), self.radius, 2)

    def reset(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.speed_x = self.base_speed_x
        self.speed_y = self.base_speed_y
