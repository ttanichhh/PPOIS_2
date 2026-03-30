from __future__ import annotations

import random
from pathlib import Path

import pygame

from src.animations import ParticleSystem
from src.config_loader import load_json
from src.entities.ball import Ball
from src.entities.bonus import Bonus
from src.entities.brick import Brick
from src.entities.paddle import Paddle
from src.records import RecordManager
from src.states import GAME_OVER, HELP, LEVEL_TRANSITION, MENU, NEW_RECORD, PLAYING, RECORDS
from src.ui import TextRenderer


class SilentSound:
    def play(self) -> None:
        return None


class ArkanoidGame:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent.parent
        self.config = load_json(self.base_dir / 'config' / 'game.json')
        self.level_data = load_json(self.base_dir / 'config' / 'levels.json')
        self.record_manager = RecordManager(str(self.base_dir / 'config' / 'records.json'))

        self.width = self.config['window']['width']
        self.height = self.config['window']['height']
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.config['window']['title'])
        self.clock = pygame.time.Clock()
        self.text = TextRenderer(self.screen, tuple(self.config['colors']['text']))

        self.background_image = self.load_background()
        self.hit_sound = self.load_sound('hit.wav')
        self.lose_sound = self.load_sound('lose.wav')
        self.win_sound = self.load_sound('win.wav')
        self.paddle_sound = self.load_sound('paddle.wav')
        self.start_music()

        self.bg_color = tuple(self.config['colors']['background'])
        self.paddle_color = tuple(self.config['colors']['paddle'])
        self.ball_color = tuple(self.config['colors']['ball'])

        self.state = MENU
        self.running = True
        self.menu_items = ['Начать игру', 'Таблица рекордов', 'Справка', 'Выход']
        self.menu_index = 0
        self.selected_level = 0

        self.current_level = self.selected_level
        self.score = 0
        self.lives = self.config['gameplay']['lives']
        self.player_name = ''
        self.transition_timer = 0
        self.transition_message = ''

        self.bonuses: list[Bonus] = []
        self.particles = ParticleSystem()

        self.create_entities()
        self.load_level(self.current_level)

    def load_background(self) -> pygame.Surface | None:
        path = self.base_dir / 'assets' / 'images' / 'background.png'
        if path.exists():
            image = pygame.image.load(str(path)).convert()
            return pygame.transform.scale(image, (self.width, self.height))
        return None

    def load_sound(self, name: str):
        path = self.base_dir / 'assets' / 'sounds' / name
        if not pygame.mixer.get_init() or not path.exists():
            return SilentSound()
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error:
            return SilentSound()

    def start_music(self) -> None:
        path = self.base_dir / 'assets' / 'sounds' / 'bg_music.wav'
        if not pygame.mixer.get_init() or not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except pygame.error:
            return

    def create_entities(self) -> None:
        paddle_cfg = self.config['paddle']
        ball_cfg = self.config['ball']

        self.paddle = Paddle(
            x=self.width // 2 - paddle_cfg['width'] // 2,
            y=self.height - 55,
            width=paddle_cfg['width'],
            height=paddle_cfg['height'],
            speed=paddle_cfg['speed'],
            screen_width=self.width,
            color=self.paddle_color,
        )

        self.ball = Ball(
            x=self.width // 2,
            y=self.height - 78,
            radius=ball_cfg['radius'],
            speed_x=ball_cfg['speed_x'],
            speed_y=ball_cfg['speed_y'],
            color=self.ball_color,
        )
        self.bricks: list[Brick] = []
        self.bonuses = []

    def reset_ball(self) -> None:
        self.ball.reset(self.width // 2, self.height - 78)
        self.paddle.rect.width = self.config['paddle']['width']
        self.paddle.rect.x = self.width // 2 - self.paddle.rect.width // 2
        self.bonuses.clear()

    def start_new_game(self) -> None:
        self.current_level = self.selected_level
        self.score = 0
        self.lives = self.config['gameplay']['lives']
        self.player_name = ''
        self.transition_timer = 90
        self.transition_message = f'Уровень {self.current_level + 1}'
        self.create_entities()
        self.load_level(self.current_level)
        self.state = LEVEL_TRANSITION

    def load_level(self, level_index: int) -> None:
        self.bricks.clear()
        self.bonuses.clear()
        level = self.level_data['levels'][level_index]
        brick_types = self.level_data['brick_types']

        start_x = 65
        start_y = 85
        brick_w = 68
        brick_h = 28
        gap = 8

        for row_idx, row in enumerate(level['layout']):
            for col_idx, cell in enumerate(row):
                if cell == '0':
                    continue
                brick_info = brick_types[cell]
                x = start_x + col_idx * (brick_w + gap)
                y = start_y + row_idx * (brick_h + gap)
                brick = Brick(
                    x=x,
                    y=y,
                    width=brick_w,
                    height=brick_h,
                    hp=brick_info['hp'],
                    color=tuple(brick_info['color']),
                    score=brick_info['score'],
                    unbreakable=brick_info.get('unbreakable', False),
                )
                self.bricks.append(brick)

    def apply_bonus(self, bonus: Bonus) -> None:
        if bonus.bonus_type == 'expand':
            self.paddle.rect.width = min(self.paddle.rect.width + 30, 220)
            self.paddle.rect.x = min(self.paddle.rect.x, self.width - self.paddle.rect.width)
        elif bonus.bonus_type == 'life':
            self.lives += 1

    def spawn_bonus(self, brick: Brick) -> None:
        if random.random() > 0.18:
            return
        bonus_type = random.choice(['expand', 'life'])
        self.bonuses.append(Bonus(brick.rect.centerx - 12, brick.rect.centery - 12, bonus_type))

    def handle_ball_paddle_collision(self) -> None:
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.speed_y > 0:
            offset = (self.ball.x - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
            self.ball.speed_x = self.ball.base_speed_x * 1.4 * offset
            if abs(self.ball.speed_x) < 2:
                self.ball.speed_x = 2 if self.ball.speed_x >= 0 else -2
            self.ball.speed_y = -abs(self.ball.speed_y)
            self.ball.y = self.paddle.rect.top - self.ball.radius - 1
            self.paddle_sound.play()

    def handle_ball_brick_collision(self) -> None:
        for brick in self.bricks:
            if brick.alive and self.ball.rect.colliderect(brick.rect):
                overlap_left = self.ball.rect.right - brick.rect.left
                overlap_right = brick.rect.right - self.ball.rect.left
                overlap_top = self.ball.rect.bottom - brick.rect.top
                overlap_bottom = brick.rect.bottom - self.ball.rect.top
                #вызывает систему частиц spawn_brick_destroy()
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                destroyed = brick.hit()
                if min_overlap in (overlap_left, overlap_right):
                    self.ball.bounce_x()
                else:
                    self.ball.bounce_y()

                self.hit_sound.play()
                if destroyed:
                    self.score += brick.score
                    self.particles.spawn_brick_destroy(brick.rect, brick.color)
                    self.spawn_bonus(brick)
                elif brick.unbreakable:
                    self.score += 5
                break

    def update_bonuses(self) -> None:
        active: list[Bonus] = []
        for bonus in self.bonuses:
            bonus.update()
            if bonus.rect.colliderect(self.paddle.rect):
                self.apply_bonus(bonus)
            elif bonus.rect.top <= self.height:
                active.append(bonus)
        self.bonuses = active

    def update_game(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(1)

        self.ball.update()

        if self.ball.x - self.ball.radius <= 0:
            self.ball.x = self.ball.radius
            self.ball.bounce_x()
        elif self.ball.x + self.ball.radius >= self.width:
            self.ball.x = self.width - self.ball.radius
            self.ball.bounce_x()

        if self.ball.y - self.ball.radius <= 0:
            self.ball.y = self.ball.radius
            self.ball.bounce_y()

        self.handle_ball_paddle_collision()
        self.handle_ball_brick_collision()
        self.update_bonuses()
        self.particles.update()

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1
            self.particles.spawn_ball_lost(self.ball.x, self.ball.y)
            self.lose_sound.play()
            if self.lives <= 0:
                if self.score > self.record_manager.best_score():
                    self.state = NEW_RECORD
                else:
                    self.state = GAME_OVER
            else:
                self.reset_ball()

        if all((not brick.alive) or brick.unbreakable for brick in self.bricks):
            self.current_level += 1
            if self.current_level >= len(self.level_data['levels']):
                self.win_sound.play()
                if self.score > self.record_manager.best_score():
                    self.state = NEW_RECORD
                else:
                    self.state = GAME_OVER
            else:
                self.load_level(self.current_level)
                self.reset_ball()
                self.transition_timer = 90
                self.transition_message = f'Уровень {self.current_level + 1}'
                self.state = LEVEL_TRANSITION

    def draw_background(self) -> None:
        if self.background_image is not None:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)

    def draw_hud(self) -> None:
        text = f'Счёт: {self.score}   •   Жизни: {self.lives}   •   Уровень: {self.current_level + 1}'
        self.text.left(text, 18, 16)

    def draw_menu(self) -> None:
        self.draw_background()
        self.text.center('ARKANOID', 140, big=True)
        self.text.center(f'Выбран уровень: {self.selected_level + 1}', 200, small=True)
        self.text.center('1-5 — уровни 1-5, Q/W/E/R/T — уровни 6-10', 230, small=True)
        for index, item in enumerate(self.menu_items):
            prefix = '▶ ' if index == self.menu_index else '  '
            self.text.center(prefix + item, 320 + index * 56)
        self.text.center('Управление в игре: ← → или A / D', 610, small=True)

    def draw_help(self) -> None:
        self.draw_background()
        lines = [
            'Справка',
            'Цель игры — уничтожить все разрушаемые кирпичи мячом.',
            'Игрок управляет платформой и не должен дать мячу упасть вниз.',
            'Прочные кирпичи требуют несколько ударов.',
            'Серые кирпичи неразрушимы и служат препятствием.',
            'Иногда выпадают бонусы: увеличение платформы и дополнительная жизнь.',
            'ESC — назад в меню.',
        ]
        for i, line in enumerate(lines):
            self.text.center(line, 110 + i * 60, big=(i == 0), small=(0 < i < 6))

    def draw_records(self) -> None:
        self.draw_background()
        self.text.center('Таблица рекордов', 110, big=True)
        records = self.record_manager.records or [{'name': '---', 'score': 0}]
        for i, record in enumerate(records[:10], start=1):
            self.text.center(f"{i}. {record['name']} — {record['score']}", 180 + i * 40)
        self.text.center('ESC — назад', 635, small=True)

    def draw_game(self) -> None:
        self.draw_background()
        self.draw_hud()
        for brick in self.bricks:
            brick.draw(self.screen)
        for bonus in self.bonuses:
            bonus.draw(self.screen)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.particles.draw(self.screen)

    def draw_game_over(self) -> None:
        self.draw_background()
        self.text.center('Игра окончена', 250, big=True)
        self.text.center(f'Ваш счёт: {self.score}', 330)
        self.text.center('ENTER — в меню', 420)

    def draw_new_record(self) -> None:
        self.draw_background()
        self.text.center('Поздравляем! Новый рекорд!', 200, big=True)
        self.text.center(f'Ваш счёт: {self.score}', 280)
        self.text.center('Введите имя и нажмите ENTER', 360)
        self.text.center(self.player_name if self.player_name else '_', 430, big=True)

    def draw_transition(self) -> None:
        self.draw_game()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        self.text.center(self.transition_message, self.height // 2, big=True)

    def handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_1, pygame.K_KP1):
            self.selected_level = 0
        elif event.key in (pygame.K_2, pygame.K_KP2):
            self.selected_level = 1
        elif event.key in (pygame.K_3, pygame.K_KP3):
            self.selected_level = 2
        elif event.key in (pygame.K_4, pygame.K_KP4):
            self.selected_level = 3
        elif event.key in (pygame.K_5, pygame.K_KP5):
            self.selected_level = 4
        elif event.key == pygame.K_q:
            if len(self.level_data['levels']) >= 6:
                self.selected_level = 5
        elif event.key == pygame.K_w:
            if len(self.level_data['levels']) >= 7:
                self.selected_level = 6
        elif event.key == pygame.K_e:
            if len(self.level_data['levels']) >= 8:
                self.selected_level = 7
        elif event.key == pygame.K_r:
            if len(self.level_data['levels']) >= 9:
                self.selected_level = 8
        elif event.key == pygame.K_t:
            if len(self.level_data['levels']) >= 10:
                self.selected_level = 9

        if event.key == pygame.K_UP:
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
        elif event.key == pygame.K_DOWN:
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
        elif event.key == pygame.K_RETURN:
            if self.menu_index == 0:
                self.start_new_game()
            elif self.menu_index == 1:
                self.state = RECORDS
            elif self.menu_index == 2:
                self.state = HELP
            elif self.menu_index == 3:
                self.running = False

    # ПРИМЕР_2
    def handle_events(self) -> None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if self.state == MENU:
                self.handle_menu_event(event)
            elif self.state == PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = MENU
            elif self.state in (HELP, RECORDS):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = MENU
            elif self.state == GAME_OVER:
                #обработка нажатия клавиши
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = MENU
            elif self.state == NEW_RECORD:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        name = self.player_name.strip() or 'Player'
                        self.record_manager.add_record(name, self.score)
                        self.player_name = ''
                        self.state = MENU
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 12 and event.unicode.isprintable() and event.unicode not in '\r\n\t':
                        self.player_name += event.unicode

    def update_transition(self) -> None:
        self.particles.update()
        self.transition_timer -= 1
        if self.transition_timer <= 0:
            self.state = PLAYING

    def run(self) -> None:
        fps = self.config['gameplay']['fps']
        while self.running:
            self.handle_events()

            if self.state == PLAYING:
                self.update_game()
            elif self.state == LEVEL_TRANSITION:
                self.update_transition()
            else:
                self.particles.update()

            if self.state == MENU:
                self.draw_menu()
            elif self.state == PLAYING:
                self.draw_game()
            elif self.state == HELP:
                self.draw_help()
            elif self.state == RECORDS:
                self.draw_records()
            elif self.state == GAME_OVER:
                self.draw_game_over()
            elif self.state == NEW_RECORD:
                self.draw_new_record()
            elif self.state == LEVEL_TRANSITION:
                self.draw_transition()

            pygame.display.flip()
            self.clock.tick(fps)
