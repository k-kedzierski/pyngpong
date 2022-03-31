import pygame
from pingpong.network import Network

class Player:
    width = 20
    height = 50
    
    def __init__(self, init_x, init_y, color=(255, 255, 255)):
        self.x = init_x
        self.y = init_y
        self.color = color
        self.velocity = 2

    def draw(self, game):
        pygame.draw.rect(game, self.color, (self.x, self.y, self.width, self.height), 0)

    def move(self, direction):
        if direction == 0:
            self.x += self.velocity
        elif direction == 1:
            self.x -= self.velocity
        elif direction == 2:
            self.y -= self.velocity
        elif direction == 3:
            self.y += self.velocity

class Game:

    def __init__(self, width: int, height: int) -> None:
        self.net = Network()
        self.width = width
        self.height = height
        self.player1 = Player(10, self.height / 2 - Player.height / 2)
        self.player2 = Player(self.width - 10 - Player.width, self.height / 2 - Player.height / 2)
        self.board = Board(self.width, self.height)

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption('Ping Pong')

        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            clock.tick(60)
            self.handle_events()
            self.communicate()
            self.update()


        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if self.player1.x >= self.player1.velocity:
                        self.player1.move(0)
                elif event.key == pygame.K_LEFT:
                    if self.player1.x <= self.width - self.player1.width:
                        self.player1.move(1)
                elif event.key == pygame.K_UP:
                    if self.player1.y >= self.player1.velocity:
                        self.player1.move(2)
                elif event.key == pygame.K_DOWN:
                    if self.player1.y <= self.height - self.player1.velocity:
                        self.player1.move(3)

    def communicate(self) -> None:
        """
        Send data to the server
        """
        # Send data to the server
        response = self.net.send("{0}:{1},{2}".format(self.net.id, self.player1.x, self.player1.y))
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