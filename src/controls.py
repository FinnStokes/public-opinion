import math

import pygame

import states


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
        self._keydowns = []
        self.time = 0.0
        self.up = 0
        self.down = 0

    def keydown(self, key):
        self._keydowns.append(key)

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

    def update_game(self, players, state, dt):
        self.update()

        for key in self._keydowns:
            if key == pygame.K_ESCAPE:
                state.change(states.PAUSE_MENU)
            for i, j in enumerate(self.joys):
                if key == (i, 7):
                    state.change(states.PAUSE_MENU)
        self._keydowns = []

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

    def update_menu(self, menu, state, dt):
        self.update()

        cancel = False
        accept = False
        for key in self._keydowns:
            if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
                cancel = True
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                accept = True
            else:
                for i, j in enumerate(self.joys):
                    if key == (i, 0):
                        accept = True
                    elif key == (i, 1) or key == (i, 6):
                        cancel = True
        self._keydowns = []

        move = [self.arrows[0] + self.wasd[0],
                self.arrows[1] + self.wasd[1]]
        for j in self.joys:
            move[0] += j[0]
            move[1] += j[1]

        if move[1] < -0.5:
            self.down = 0
            if self.up == 0:
                menu.prev()
                self.time = 0.0
                self.up = 1
            self.time += dt
            n = int(2*self.time) - self.up
            for i in range(n):
                menu.prev()
                self.up += 1
        elif move[1] > 0.5:
            self.up = 0
            if self.down == 0:
                menu.next()
                self.time = 0.0
                self.down = 1
            self.time += dt
            n = int(2*self.time) - self.down
            for i in range(n):
                menu.next()
                self.down += 1
        else:
            self.up = 0
            self.down = 0

        if cancel:
            state.close()

        if accept:
            menu.accept()
