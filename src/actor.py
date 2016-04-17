import math

import pygame

INTERACTION_RADIUS = 0.02
PROXIMITY = 0.1
TIMESCALE = 3.0
MARGIN = 0.001


class Actor(pygame.sprite.Sprite):
    def __init__(self, world, pos, fixed=False, position=0.0):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.pos = pos
        self.image = pygame.Surface((10, 10))
        self.rect = self.image.get_rect()
        self.direction = (0.0, 0.0)
        self.speed = 0.3
        self.position = position
        self.update_colour()
        self.crowdedness = 0.0
        self.fixed = fixed
        self.updated = 0
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
        r = int(255 * (1.0 + self.position) / 2.0)
        b = 255 - r
        self.image.fill((r, 0, b))

    def influence(self, other):
        return 0.0 if self.fixed else 0.6

    def interact(self, other):
        pass


class Citizen(Actor):
    def __init__(self, world, *args, **kwargs):
        Actor.__init__(self, world, world.random_pos(), *args, **kwargs)
        self.connection = {}
        self.time = {}

    def attraction(self, actor):
        connection = self.connection.get(actor, 0.0)
        proximity = PROXIMITY / (PROXIMITY + (self.pos[0] - actor.pos[0])**2
                                 + (self.pos[1] - actor.pos[1])**2)
        time = self.time[actor]
        time = time / (TIMESCALE + time)
        crowdedness = 1.0  # / (0.1 + actor.crowdedness)
        return (connection + proximity) * time * crowdedness

    def update(self, frame, dt):
        maximum = 0.0
        target = None
        move = [0.0, 0.0]
        for a in self.world.actors:
            if a is not self:
                self.time[a] = self.time.get(a, 0.0) + dt
                attraction = self.attraction(a)
                if attraction > maximum:
                    target = a
                    maximum = attraction
        for a in self.world.actors:
            if a is target:
                factor = 1.0
            elif a.fixed:
                factor = 0.0
            else:
                factor = -0.1 / (0.01 + (a.pos[0] - self.pos[0])**2
                                 + (a.pos[1] - self.pos[1])**2)**2
            move[0] += factor * (a.pos[0] - self.pos[0])
            move[1] += factor * (a.pos[1] - self.pos[1])
        move[0] -= 1.0 / (self.world.left - MARGIN - self.pos[0])
        move[0] -= 1.0 / (self.world.right + MARGIN - self.pos[0])
        move[1] -= 1.0 / (self.world.top - MARGIN - self.pos[1])
        move[1] -= 1.0 / (self.world.bottom + MARGIN - self.pos[1])
        norm2 = move[0]**2 + move[1]**2
        if norm2 > INTERACTION_RADIUS**2:
            norm = math.sqrt(norm2)
        else:
            norm = INTERACTION_RADIUS
        move[0] /= norm
        move[1] /= norm
        self.direction = move
        Actor.update(self, frame, dt)

    def interact(self, other):
        self.time[other] = 0.0
