import math
import random
import pygame
from pingpong.network import Network
from enum import Enum

POWERSHOT_EVENT_UP = pygame.USEREVENT + 1
POWERSHOT_EVENT_DOWN = pygame.USEREVENT + 2
POWERSHOT_EVENT_END = pygame.USEREVENT + 3


class Direction(Enum):
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3


class Player:
    width = 20
    height = 60

    def __init__(self, init_x, init_y, color=(255, 255, 255)):
        self.x = init_x
        self.y = init_y
        self.color = color
        self.velocity = 6
        self.angle = 0
        self.power_shot = False

    def draw(self, game):
        pygame.draw.rect(game, self.color, (self.x, self.y, self.width, self.height), 0)

    def move(self, angle, velocity):
        self.x += velocity * math.cos(angle)
        self.y += velocity * math.sin(angle)

    def move_mouse(self, mouse_x, mouse_y):
        eucl_dist = math.hypot(
            mouse_x - self.x - (self.width / 2), mouse_y - self.y - (self.height / 2)
        )
        if eucl_dist > self.velocity:
            sinx = (mouse_y - self.y - (self.height / 2)) / eucl_dist
            cosx = (mouse_x - self.x - (self.width / 2)) / eucl_dist

            self.x += self.velocity * cosx
            self.y += self.velocity * sinx

            self.angle = math.atan2(
                mouse_y - self.y - (self.height / 2),
                mouse_x - self.x - (self.width / 2),
            )


class Ball:
    radius = 10

    def __init__(self, init_x, init_y, color=(255, 255, 255)):
        self.x = init_x
        self.y = init_y
        self.color = color
        self.velocity = 4
        self.direction = self._random_direction()
        self.cooldown = 20

    def draw(self, game):
        pygame.draw.circle(game, self.color, (self.x, self.y), self.radius)

    def move(self, game):
        self.handleBorders(game)

        self.x += self.velocity * math.cos(self.direction)
        self.y += self.velocity * math.sin(self.direction)

    def _random_direction(self):
        if random.randint(0, 1) == 0:
            return 3 * math.pi / 4 + (random.random() * 2 * math.pi / 4)
        else:
            return (7 * math.pi / 4 + (random.random() * 2 * math.pi / 4)) % (
                2 * math.pi
            )

    def handleBorders(self, game):
        # Border checking

        # Top and bottom
        if self.y > game.height - self.radius:
            self.flip_x()

        elif self.y < self.radius:
            self.flip_x()

        # Left and right
        if self.x > game.width:
            # TODO handle points

            self.x = game.width / 2
            self.y = game.height / 2
            self.direction = self._random_direction()
            self.velocity = 4
            game.score2 += 1

        elif self.x < 0:
            # TODO handle points

            self.x = game.width / 2
            self.y = game.height / 2
            self.direction = self._random_direction()
            self.velocity = 4
            game.score1 += 1

        # Paddle and self collisions

        if (
            self.x > game.player1.x
            and self.x < game.player1.x + game.player1.width
            and self.y > game.player1.y
            and self.y < game.player1.y + game.player1.height
        ):
            if self.cooldown == 0:
                self.direction = game.player1.angle
                self.cooldown = 20

                if game.player1.power_shot:
                    self.velocity += 4
                else:
                    self.velocity = self.velocity * 0.9

        if (
            self.x > game.player2.x
            and self.x < game.player2.x + game.player2.width
            and self.y > game.player2.y
            and self.y < game.player2.y + game.player2.height
        ):
            if self.cooldown == 0:
                self.direction = game.player2.angle
                self.cooldown = 20

                if game.player2.power_shot:
                    self.velocity += 4
                else:
                    self.velocity = self.velocity * 0.9

        self.cooldown -= 1 if self.cooldown > 0 else 0

    def flip_x(self):
        self.direction = math.pi * 2 - self.direction

    def flip_y(self):
        self.direction = math.pi - self.direction

    def flipDirection(self):
        if self.direction == Direction.LEFT:
            self.direction = Direction.RIGHT
            return

        self.direction = Direction.LEFT


class Game:
    def __init__(self, width: int, height: int, host: str, port: int) -> None:
        self.net = Network(host, port)
        self.width = width
        self.height = height
        self.player1 = Player(10, self.height / 2 - Player.height / 2)
        self.player2 = Player(
            self.width - 10 - Player.width, self.height / 2 - Player.height / 2
        )
        self.board = Board(self.width, self.height)
        self.ball = Ball(self.width / 2, self.height / 2)
        self.score1 = 0
        self.score2 = 0

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption("Dynamic Ping Pong")

        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            clock.tick(60)
            self.handle_events()
            self.handle_ball()
            self.communicate()
            self.update()

        pygame.quit()

    def handle_events(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
            return
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.player1.power_shot = True
            self.player1.color = (218, 112, 214)
            for _ in range(20):
                pygame.event.post(pygame.event.Event(POWERSHOT_EVENT_UP))
            for _ in range(20):
                pygame.event.post(pygame.event.Event(POWERSHOT_EVENT_DOWN))
            pygame.event.post(pygame.event.Event(POWERSHOT_EVENT_END))
        elif event.type == POWERSHOT_EVENT_UP:
            self.player1.move(self.player1.angle, 2)
        elif event.type == POWERSHOT_EVENT_DOWN:
            self.player1.move(self.player1.angle, -2)
        elif event.type == POWERSHOT_EVENT_END:
            self.player1.power_shot = False
            self.player1.color = (255, 255, 255)
        else:
            self.player1.move_mouse(
                pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            )

        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_RIGHT:
        #         if self.player1.x < self.width - self.player1.width:
        #             self.player1.move(Direction.RIGHT)
        #     elif event.key == pygame.K_LEFT:
        #         if self.player1.x >= 0:
        #             self.player1.move(Direction.LEFT)
        #     elif event.key == pygame.K_UP:
        #         if self.player1.y > self.player1.velocity:
        #             self.player1.move(Direction.UP)
        #     elif event.key == pygame.K_DOWN:
        #         if self.player1.y < self.height - self.player1.velocity:
        #             self.player1.move(Direction.DOWN)

    def handle_ball(self):
        self.ball.move(self)

    def communicate(self) -> None:
        """
        Send data to the server
        """
        # Send data to the server
        response = self.net.send(
            "{0}:{1},{2}".format(self.net.id, self.player1.x, self.player1.y)
        )
        try:
            arr = response.split(":")[-1].split(",")
            self.player2.x = int(arr[0])
            self.player2.y = int(arr[1])
        except:
            # Silently pass on exception
            # TODO: Add event logging
            pass

    def quit(self) -> None:
        """
        Clean up the game and exit
        """
        pygame.quit()

    def update(self) -> None:
        """
        Update the board
        """
        self.board.draw_background()
        self.player1.draw(self.board.screen)
        self.player2.draw(self.board.screen)
        self.ball.draw(self.board.screen)
        self.board.draw_score(self.score1, self.score2)
        self.board.update()


class Board:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))

    def update(self) -> None:
        """
        Update the screen
        """
        pygame.display.update()

    def draw_background(self) -> None:
        self.screen.fill((0, 0, 0))

    def draw_score(self, score1, score2) -> None:
        font = pygame.font.SysFont("monospace", 20)
        text = font.render("{0} - {1}".format(score1, score2), True, (255, 255, 255))
        self.screen.blit(text, (self.width / 2 - text.get_width() / 2, 10))
