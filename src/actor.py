import math

import pygame

INTERACTION_RADIUS = 0.01
PROXIMITY = 0.1
TIMESCALE = 3.0
MARGIN = 0.001
DECAY_RATE = 1.0
CONNECT_RATE = 0.5
CLUSTER_THRESHOLD = 0.8


class Actor(pygame.sprite.Sprite):
    def __init__(self, world, col, pos, fixed=False, position=0.0, size=15, speed=0.3):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.pos = pos
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect()
        self.colour = col
        self.direction = (2.0, 0.0)
        self.speed = speed
        self.position = position
        self.update_colour()
        self.crowdedness = 0.0
        self.fixed = fixed
        self.updated = 0
        self.connection = {}
        world.add(self)

    def update(self, frame, dt):
        self.pos = (self.pos[0] + self.direction[0] * self.speed * dt,
                    self.pos[1] + self.direction[1] * self.speed * dt)
        self.pos = (min(max(self.pos[0], self.world.left), self.world.right),
                    min(max(self.pos[1], self.world.top), self.world.bottom))
        self.rect.center = self.world.screen(self.pos)

        self.crowdedness = 0.0
        for a in self.world.actors:
            if a is not self and a.updated == frame:
                dist2 = ((self.pos[0] - a.pos[0])**2
                         + (self.pos[1] - a.pos[1])**2)
                if dist2 < INTERACTION_RADIUS**2:
                    (self.position, a.position) = (
                        self.position
                        + self.influence(a) * (a.position - self.position),
                        a.position
                        + a.influence(self) * (self.position - a.position))
                    self.update_colour()
                    a.update_colour()
                    self.interact(a)
                    a.interact(self)
                self.crowdedness += PROXIMITY / (PROXIMITY + dist2)
        self.updated = frame

    def update_colour(self):
        b = self.colour.blue()
        r = self.colour.red()
        x = (1.0 + self.position) / 2.0
        self.image.fill((0, 0, 0))
        rect = self.rect.copy()
        rect.width -= 2
        rect.height -= 2
        rect.topleft = (1, 1)
        pygame.draw.rect(self.image, tuple(int(b[i] + (r[i] - b[i])*x) for i in (0, 1, 2)), rect)

    def influence(self, other):
        if self.fixed:
            return 0.0
        else:
            return (1.0 * (other.position**2 + 0.5)
                    / ((1.0 + (self.position - other.position)**2)
                        * (self.position**2 + other.position**2 + 2 * 0.5)))

    def interact(self, other):
        pass


class Citizen(Actor):
    def __init__(self, world, col, *args, **kwargs):
        Actor.__init__(self, world, col, world.random_pos(), size=10, speed=0.2, *args, **kwargs)
        self.time = {}

    def update(self, frame, dt):
        maximum = 0.0
        target = None
        target_move = (0.0, 0.0)
        move = [0.0, 0.0]
        for a in self.world.actors:
            if a is not self:
                a_move = (0.0, 0.0)
                self.time[a] = self.time.get(a, 0.0) + dt
                dx = a.pos[0] - self.pos[0]
                dy = a.pos[1] - self.pos[1]
                d2 = dx**2 + dy**2
                connection = self.connection.get(a, 0.0)
                proximity = PROXIMITY / (PROXIMITY + d2)
                time = self.time[a]
                time = time / (TIMESCALE + time)
                crowdedness = 1.0 / (1.0 + 0.1 * a.crowdedness)
                attraction = (connection + proximity) * time * crowdedness
                if not a.fixed:
                    if connection > CLUSTER_THRESHOLD:
                        if d2 > 0:
                            d = math.sqrt(d2)
                            f = PROXIMITY**3 / (PROXIMITY**2 + d2**2 / 100)
                            a_move = (f * dx * (1.0 - PROXIMITY / d),
                                      f * dy * (1.0 - PROXIMITY / d))
                    else:
                        if d2 > 0:
                            f = -PROXIMITY / d2
                            a_move = (f * dx, f * dy)
                else:
                    f = 4.0 * (time - 0.5) * PROXIMITY / (d2)
                    a_move = (f * dx, f * dy)

                if attraction > maximum:
                    target = a
                    target_move = a_move
                    maximum = attraction
                move[0] += a_move[0]
                move[1] += a_move[1]
        if target is not None:
            dx = target.pos[0] - self.pos[0]
            dy = target.pos[1] - self.pos[1]
            d2 = dx**2 + dy**2
            if d2 > 0:
                d = math.sqrt(d2)
                f = 1.0 / d
                move[0] += f * dx - target_move[0]
                move[1] += f * dy - target_move[1]
        # for a in self.world.actors:
        #     if a is not self and not a.fixed:
        #         self.time[a] = self.time.get(a, 0.0) + dt
        #         attraction = self.attraction(a)
        #         factor = attraction - 0.5
        #         move[0] += factor * (a.pos[0] - self.pos[0])
        #         move[1] += factor * (a.pos[1] - self.pos[1])
        move[0] -= 0.5 / (self.world.left - MARGIN - self.pos[0])
        move[0] -= 0.5 / (self.world.right + MARGIN - self.pos[0])
        move[1] -= 0.5 / (self.world.top - MARGIN - self.pos[1])
        move[1] -= 0.5 / (self.world.bottom + MARGIN - self.pos[1])
        norm2 = move[0]**2 + move[1]**2
        if norm2 > INTERACTION_RADIUS**2:
            norm = math.sqrt(norm2)
        else:
            norm = INTERACTION_RADIUS
        move[0] /= norm
        move[1] /= norm
        self.direction = move
        decay = DECAY_RATE**dt
        for a in self.connection:
            self.connection[a] *= decay
        Actor.update(self, frame, dt)

    def interact(self, other):
        self.time[other] = 0.0
        c = self.connection.get(other, 0.0)
        dc = (1.0 - c) * CONNECT_RATE
        self.connection[other] += dc
        dc /= len(self.connection) - 1
        for a in self.connection:
            if a is not other:
                self.connection[a] -= dc
