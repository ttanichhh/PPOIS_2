from __future__ import annotations

import random
from dataclasses import dataclass

import pygame


@dataclass
class Particle:
    x: float
    y: float
    dx: float
    dy: float
    life: int
    color: tuple[int, int, int]
    size: int

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.08
        self.life -= 1

    def draw(self, screen: pygame.Surface) -> None:
        if self.life <= 0:
            return
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), max(1, self.size))


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def spawn_brick_destroy(self, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        for _ in range(16):
            self.particles.append(
                Particle(
                    x=rect.centerx + random.uniform(-8, 8),
                    y=rect.centery + random.uniform(-4, 4),
                    dx=random.uniform(-3.0, 3.0),
                    dy=random.uniform(-3.5, 1.0),
                    life=random.randint(18, 32),
                    color=color,
                    size=random.randint(2, 4),
                )
            )

    def spawn_ball_lost(self, x: float, y: float) -> None:
        for _ in range(20):
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    dx=random.uniform(-2.5, 2.5),
                    dy=random.uniform(-4.0, -1.0),
                    life=random.randint(20, 36),
                    color=(255, 180, 120),
                    size=random.randint(2, 5),
                )
            )

    def update(self) -> None:
        alive: list[Particle] = []
        for particle in self.particles:
            particle.update()
            if particle.life > 0:
                alive.append(particle)
        self.particles = alive

    def draw(self, screen: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(screen)
