from __future__ import annotations

import pygame


class Brick:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        hp: int,
        color: tuple[int, int, int],
        score: int,
        unbreakable: bool = False,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.score = score
        self.unbreakable = unbreakable
        self.alive = hp > 0 or unbreakable

    def hit(self) -> bool:
        if self.unbreakable or not self.alive:
            return False
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def current_color(self) -> tuple[int, int, int]:
        if self.unbreakable:
            return (191, 160, 140)
        if self.max_hp <= 1:
            return self.color
        factor = 0.6 + 0.4 * (self.hp / self.max_hp)
        return tuple(min(255, max(0, int(channel * factor))) for channel in self.color)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        color = self.current_color()
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (250, 247, 249), self.rect, 2, border_radius=5)
