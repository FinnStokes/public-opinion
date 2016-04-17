import math

import pygame


DEADZONE = 0.1


def normalise(vec):
    norm2 = vec[0]**2 + vec[1]**2
    if norm2 > 1:
        norm = math.sqrt(norm2)
        return [vec[0]/norm, vec[1]/norm]
    return vec


class Controls(object):
    def __init__(self):
        self.joysticks = [pygame.joystick.Joystick(i) for i in xrange(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.wasd = [0.0, 0.0]
        self.arrows = [0.0, 0.0]
        self.joys = [[0.0, 0.0] for j in self.joysticks]

    def update(self):
        pressed = pygame.key.get_pressed()

        self.arrows = [0.0, 0.0]
        if pressed[pygame.K_UP]:
            self.arrows[1] -= 1.0
        if pressed[pygame.K_DOWN]:
            self.arrows[1] += 1.0
        if pressed[pygame.K_LEFT]:
            self.arrows[0] -= 1.0
        if pressed[pygame.K_RIGHT]:
            self.arrows[0] += 1.0

        self.wasd = [0.0, 0.0]
        if pressed[pygame.K_w]:
            self.wasd[1] -= 1.0
        if pressed[pygame.K_s]:
            self.wasd[1] += 1.0
        if pressed[pygame.K_a]:
            self.wasd[0] -= 1.0
        if pressed[pygame.K_d]:
            self.wasd[0] += 1.0

        for i, j in enumerate(self.joysticks):
            self.joys[i] = [j.get_axis(k) for k in 0,1]
            for k in 0, 1:
                self.joys[i][k] = math.copysign(max(abs(self.joys[i][k]) - DEADZONE, 0.0),
                                                self.joys[i][k]) / (1.0 - DEADZONE)

    def update_game(self, players, dt):
        self.update()

        if len(players) == 1:
            move = [self.arrows[0] + self.wasd[0],
                    self.arrows[1] + self.wasd[1]]
            for j in self.joys:
                move[0] += j[0]
                move[1] += j[1]
            players[0].direction = normalise(move)
        elif len(players) > 1:
            if len(self.joys) < len(players):
                if len(players) == len(self.joys) + 1:
                    move1 = [self.arrows[0] + self.wasd[0],
                             self.arrows[1] + self.wasd[1]]
                    players[0].direction = normalise(move1)

                    for i, j in enumerate(self.joys):
                        move2 = [j[0], j[1]]
                        players[i+1].direction = normalise(move2)
                else:
                    move1 = [self.wasd[0], self.wasd[1]]
                    players[0].direction = normalise(move1)

                    move2 = [self.arrows[0], self.arrows[1]]
                    players[1].direction = normalise(move2)

                    for i, j in enumerate(self.joys):
                        move3 = [j[0], j[1]]
                        players[i+2].direction = normalise(move3)
            else:
                move1 = [self.wasd[0], self.wasd[1]]
                if 0 < len(self.joys):
                    move1[0] += self.joys[0][0]
                    move1[1] += self.joys[0][1]
                players[0].direction = normalise(move1)

                move2 = [self.arrows[0], self.arrows[1]]
                if 1 < len(self.joys):
                    move2[0] += self.joys[1][0]
                    move2[1] += self.joys[1][1]
                players[1].direction = normalise(move2)

                for i, j in enumerate(self.joys[2:]):
                    if i < len(players):
                        move3 = [j[0], j[1]]
                        players[i+2] = normalise(move3)

    def update_menu(self, menu, dt):
        move = [self.arrows[0] + self.wasd[0],
                self.arrows[1] + self.wasd[1]]
        for j in self.joys:
            move[0] += j[0]
            move[1] += j[1]
