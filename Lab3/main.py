import pygame

from src.game import ArkanoidGame


def main() -> None:
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        # Игра продолжит работу даже если звук недоступен.
        pass

    game = ArkanoidGame()
    game.run()

    pygame.quit()


if __name__ == '__main__':
    main()
