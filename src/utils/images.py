import random
from typing import List, Tuple

import pygame

from .constants import BACKGROUNDS, PIPES, PLAYERS


class Images:
    numbers: List[pygame.Surface]
    game_over: pygame.Surface
    welcome_message: pygame.Surface
    base: pygame.Surface
    background: pygame.Surface
    player: Tuple[pygame.Surface]
    pipe: Tuple[pygame.Surface]

    def __init__(self) -> None:
        self.numbers = list(
            (
                pygame.image.load(f"assets/sprites/{num}.png").convert_alpha()
                for num in range(10)
            )
        )
        for i in range (len(self.numbers)):
            self.numbers[i] = pygame.transform.scale(self.numbers[i], (self.numbers[i].get_width() * 2* 1.171875, self.numbers[i].get_height() * 2* 1.171875))
        # game over sprite
        self.game_over = pygame.image.load(
            "assets/sprites/gameover.png"
        ).convert_alpha()
        self.game_over = pygame.transform.scale(self.game_over, (self.game_over.get_width()*2 * 1.171875, self.game_over.get_height() * 2*1.171875))
        # welcome_message sprite for welcome screen
        self.welcome_message = pygame.image.load(
            "assets/sprites/message.png"
        ).convert_alpha()
        self.welcome_message = pygame.transform.scale(self.welcome_message, (self.welcome_message.get_width() * 2*1.171875, self.welcome_message.get_height() * 2*1.171875))
        
        # base (ground) sprite
        self.base = pygame.image.load("assets/sprites/base.png").convert_alpha()
        self.base = pygame.transform.scale(self.base, ((self.base.get_width())*2*1.171875, (self.base.get_height())*2*1.171875))
        self.randomize()

    def randomize(self):
        # select random background sprites
        rand_bg = random.randint(0, len(BACKGROUNDS) - 1)
        # select random player sprites
        rand_player = random.randint(0, len(PLAYERS) - 1)
        # select random pipe sprites
        rand_pipe = random.randint(0, len(PIPES) - 1)

        self.background = pygame.image.load(BACKGROUNDS[rand_bg]).convert()
        self.background = pygame.transform.scale(self.background, (self.background.get_width() * 2*1.171875, self.background.get_height() * 2*1.171875))
        self.player = [
            pygame.image.load(PLAYERS[rand_player][0]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][1]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][2]).convert_alpha(),
        ]
        for i in range (len(self.player)):
            self.player[i] = pygame.transform.scale(self.player[i], (self.player[i].get_width() * 2*1.171875, self.player[i].get_height() * 2*1.171875))
        self.pipe = [
            pygame.transform.flip(
                pygame.image.load(PIPES[rand_pipe]).convert_alpha(),
                False,
                True,
            ),
            pygame.image.load(PIPES[rand_pipe]).convert_alpha(),
        ]
        for i in range(len(self.pipe)):
            self.pipe[i] = pygame.transform.scale(self.pipe[i], (self.pipe[i].get_width() * 2*1.171875, self.pipe[i].get_height()*2*1.171875))
