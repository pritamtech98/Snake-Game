import random
import time
from typing import Dict, List, Tuple, Union

import pygame
from pygame.locals import (
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_RIGHT,
    K_UP,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    QUIT,
)

SCREEN_WIDTH: int = 400
SCREEN_HEIGHT: int = 200
COLOR_WHITE: Tuple[int, int, int] = (255, 255, 255)
COLOR_BLACK: Tuple[int, int, int] = (0, 0, 0)
COLOR_RED: Tuple[int, int, int] = (255, 0, 0)
PASTEL_PINK: Tuple[int, int, int] = (255, 183, 197)
SNAKE_INIT_LANDING_SITE: Tuple[int, int] = (50, 50)
SNAKE_COLOR: Tuple[int, int, int] = (33, 219, 83)
APPLE_COLOR: Tuple[int, int, int] = COLOR_RED
BLOCK_SIZE: int = 10
INITIAL_SNAKE_LENGTH: int = 4
SNAKE_SPEED: dict = {"Easy": 0.14, "Medium": 0.1, "Hard": 0.06}
FONT_NAME: str = "Helvetica"
FONT_SIZE: int = 16
SCORE_POSITION: Tuple[int, int] = (5, 5)
GAME_OVER_FONT_SIZE: int = 40
FPS: int = 90
DIR_LEFT: str = "left"
DIR_RIGHT: str = "right"
DIR_UP: str = "up"
DIR_DOWN: str = "down"
GAME_THEME: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    "WHITE": {
        "SCREEN_BACKGROUND": COLOR_WHITE,
        "SCORE_COLOR": COLOR_BLACK,
        "MENU_COLOR": (133, 15, 141),
    },
    "BLACK": {
        "SCREEN_BACKGROUND": COLOR_BLACK,
        "SCORE_COLOR": COLOR_WHITE,
        "MENU_COLOR": (133, 15, 141),
    },
}
THEME: str = "BLACK"


class Body:
    def __init__(
        self,
        pos_x: int,
        pos_y: int,
        direction: str,
        screen: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]],
        color: Tuple[int, int, int] = SNAKE_COLOR,
    ) -> None:
        self.direction: str = direction
        self.width: int = BLOCK_SIZE
        self.height: int = BLOCK_SIZE
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.color: Tuple[int, int, int] = color
        self.screen: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]] = (
            screen
        )

    def draw(self) -> None:
        pygame.draw.rect(
            self.screen["SURFACE"],
            self.color,
            (self.pos_x, self.pos_y, self.width, self.height),
        )


class Apple(Body):
    def __init__(
        self,
        pos_x: int,
        pos_y: int,
        screen: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]],
        direction: str,
    ) -> None:
        super().__init__(pos_x, pos_y, direction, screen, APPLE_COLOR)

    def get_random_position(self) -> Tuple[int, int]:
        self.pos_x, self.pos_y = (
            random.randint(0, (self.screen["SCREEN_WIDTH"] - self.width) // self.width)
            * self.width
        ), (
            random.randint(
                0, (self.screen["SCREEN_HEIGHT"] - self.height) // self.height
            )
            * self.height
        )

    def check_collision(self, body: List[Body]) -> None:
        while not all(
            [(self.pos_x != cell.pos_x) or (self.pos_y != cell.pos_y) for cell in body]
        ):
            self.get_random_position()

    def place_apple(self, body: List[Body]) -> None:
        self.check_collision(body)


class Snake:
    def __init__(
        self, surface: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]]
    ) -> None:
        self.length: int = INITIAL_SNAKE_LENGTH
        self.init_direction: str = DIR_RIGHT
        self.screen: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]] = (
            surface
        )
        self.score_font: pygame.font.Font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.body: List[Body] = [
            Body(
                SNAKE_INIT_LANDING_SITE[0] + (self.length - 1 - i) * BLOCK_SIZE,
                SNAKE_INIT_LANDING_SITE[1],
                self.init_direction,
                self.screen,
            )
            for i in range(self.length)
        ]
        self.head: Body = self.body[0]
        self.apple: Apple = Apple(
            SNAKE_INIT_LANDING_SITE[0],
            SNAKE_INIT_LANDING_SITE[1],
            self.screen,
            self.init_direction,
        )
        self.apple.place_apple(self.body)

    def add_body_after_eat(self) -> None:
        self.length += 1
        directions: Dict[str, Tuple[int, int]] = {
            DIR_LEFT: (
                self.body[-1].pos_x + self.body[-1].width,
                self.body[-1].pos_y,
            ),
            DIR_RIGHT: (
                self.body[-1].pos_x - self.body[-1].width,
                self.body[-1].pos_y,
            ),
            DIR_UP: (
                self.body[-1].pos_x,
                self.body[-1].pos_y + self.body[-1].height,
            ),
            DIR_DOWN: (
                self.body[-1].pos_x,
                self.body[-1].pos_y - self.body[-1].height,
            ),
        }

        self.body.append(
            Body(
                *directions[self.body[-1].direction],
                self.body[-1].direction,
                self.screen,
            )
        )

    def draw_score(self) -> None:
        score: pygame.Surface = self.score_font.render(
            f"SCORE: {Game.SCORE}", True, GAME_THEME[THEME]["SCORE_COLOR"]
        )
        self.screen["SURFACE"].blit(score, SCORE_POSITION)

    def eat(self) -> None:
        if (self.apple.pos_x == self.head.pos_x) and (
            self.apple.pos_y == self.head.pos_y
        ):
            Game.SCORE += 1
            self.apple.place_apple(self.body)
            self.add_body_after_eat()

    def draw(self) -> None:
        self.screen["SURFACE"].fill(self.screen["SCREEN_BACKGROUND"])
        self.draw_score()
        self.eat()
        self.apple.draw()
        for block in self.body:
            block.draw()
        pygame.display.flip()

    def update_position(self) -> None:
        for i in range(self.length - 1, 0, -1):
            self.body[i].direction = self.body[i - 1].direction

    def check_collision(self) -> bool:
        return (
            self.head.pos_x < 0
            or self.head.pos_x >= self.screen["SCREEN_WIDTH"]
            or self.head.pos_y < 0
            or self.head.pos_y >= self.screen["SCREEN_HEIGHT"]
            or any(
                [
                    (cell.pos_x == self.head.pos_x and cell.pos_y == self.head.pos_y)
                    for cell in self.body[1:]
                ]
            )
        )

    def crawl(self) -> bool:
        for block in self.body:
            if block.direction == DIR_LEFT:
                block.pos_x -= block.width
            elif block.direction == DIR_RIGHT:
                block.pos_x += block.width
            elif block.direction == DIR_UP:
                block.pos_y -= block.height
            else:
                block.pos_y += block.height
        if self.check_collision():
            return False
        self.draw()
        self.update_position()
        return True


class Option:
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        screen: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]],
        radius: int = 15,
        selected: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.selected = selected
        self.text = text
        self.screen = screen
        self.radius = radius

    def is_clicked(self, pos):
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        return distance <= self.radius

    def draw(self):
        pygame.draw.circle(
            self.screen["SURFACE"],
            GAME_THEME[THEME]["SCORE_COLOR"],
            (self.x, self.y),
            self.radius,
            2,
        )
        if self.selected:
            pygame.draw.circle(
                self.screen["SURFACE"],
                COLOR_RED,
                (self.x, self.y),
                self.radius - 5,
            )
        font = pygame.font.SysFont(FONT_NAME, 15)
        text_surface = font.render(self.text, True, GAME_THEME[THEME]["SCORE_COLOR"])
        self.screen["SURFACE"].blit(
            text_surface, (self.x + self.radius + 5, self.y - self.radius)
        )


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        screen: Dict[str, int | Tuple[int] | pygame.Surface],
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.screen = screen
        self.font = pygame.font.SysFont("Calibri", 17)
        self.text_label = self.font.render(
            self.text, True, GAME_THEME[THEME]["MENU_COLOR"]
        )

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return (
            pos[0] > self.x
            and pos[0] < (self.x + self.width)
            and pos[1] > self.y
            and pos[1] < (self.y + self.height)
        )

    def draw(self):
        self.rect = pygame.draw.rect(
            self.screen["SURFACE"],
            GAME_THEME[THEME]["MENU_COLOR"],
            (self.x, self.y, self.width, self.height),
            3,
            5,
        )

        self.screen["SURFACE"].blit(
            self.text_label, self.text_label.get_rect(center=self.rect.center)
        )


class Game:
    SCORE: int = 0

    def __init__(
        self,
        screen_width: int = SCREEN_WIDTH,
        screen_height: int = SCREEN_HEIGHT,
        screen_background: Tuple[int, int, int] = COLOR_WHITE,
    ) -> None:
        pygame.init()
        pygame.display.set_caption("SNAKE")
        pygame.font.init()
        self.screen: Dict[str, Union[int, Tuple[int, int, int], pygame.Surface]] = {
            "SCREEN_BACKGROUND": screen_background,
            "SCREEN_WIDTH": screen_width,
            "SCREEN_HEIGHT": screen_height,
            "SURFACE": pygame.display.set_mode((screen_width, screen_height)),
        }
        self.score_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, GAME_OVER_FONT_SIZE
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.snake: Snake = Snake(self.screen)

    def menu_game_loop(self) -> None:
        running: bool = True
        self.screen["SURFACE"].fill(GAME_THEME[THEME]["SCREEN_BACKGROUND"])
        difficulty_label = pygame.font.SysFont("Calibri", 17)
        text_surface = difficulty_label.render(
            "CHOOSE THE DIFFICULTY", True, GAME_THEME[THEME]["MENU_COLOR"]
        )
        self.screen["SURFACE"].blit(text_surface, (40, 15))
        self.start_button = Button(120, 140, 150, 40, "START GAME", self.screen)
        self.options: List[Option] = [
            Option(50, 55, "Easy", self.screen, 8, selected=True),
            Option(170, 55, "Medium", self.screen, 8),
            Option(290, 55, "Hard", self.screen, 8),
        ]
        [option.draw() for option in self.options]
        pygame.display.flip()
        selected = "Easy"

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        for option in self.options:
                            if option.is_clicked(pos):
                                for op in self.options:
                                    op.selected = False
                                option.selected = True
                                selected = option.text
                        if self.start_button.is_clicked(pos):
                            return selected
                        self.screen["SURFACE"].fill(
                            GAME_THEME[THEME]["SCREEN_BACKGROUND"]
                        )
                        self.screen["SURFACE"].blit(text_surface, (40, 15))
                        [option.draw() for option in self.options]
            self.start_button.draw()
            pygame.display.flip()
        return None

    def main_game_loop(self, difficulty: str) -> None:
        running: bool = True

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_LEFT:
                        self.snake.head.direction = DIR_LEFT
                    elif event.key == K_RIGHT:
                        self.snake.head.direction = DIR_RIGHT
                    elif event.key == K_UP:
                        self.snake.head.direction = DIR_UP
                    elif event.key == K_DOWN:
                        self.snake.head.direction = DIR_DOWN
                elif event.type == QUIT:
                    running = False

            if not self.snake.crawl():
                break
            time.sleep(SNAKE_SPEED[difficulty])
            self.clock.tick(FPS)

    def game_over_main_loop(self):
        running: bool = True
        score: pygame.Surface = self.score_font.render(
            f"SCORE: {Game.SCORE}", True, GAME_THEME[THEME]["SCORE_COLOR"]
        )
        self.screen["SURFACE"].fill(GAME_THEME[THEME]["SCREEN_BACKGROUND"])
        self.screen["SURFACE"].blit(
            score,
            (10, (SCREEN_HEIGHT) // 2 - GAME_OVER_FONT_SIZE),
        )
        pygame.display.flip()
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                elif event.type == QUIT:
                    running = False

            self.clock.tick(FPS)

    def run(self) -> None:
        value = self.menu_game_loop()
        if value:
            self.main_game_loop(value)
            self.game_over_main_loop()


if __name__ == "__main__":
    game = Game(screen_background=GAME_THEME[THEME]["SCREEN_BACKGROUND"])
    game.run()
    pygame.quit()
