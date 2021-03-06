import math
import random


class World(object):
    def __init__(self, window):
        self.width, self.height = window
        ratio = self.width * 1.0 / self.height
        w = math.sqrt(ratio)
        h = 1.0/w
        self.left = -w
        self.right = w
        self.top = -h
        self.bottom = h
        self.actors = []

    def screen(self, pos, size=None):
        wpos = (self.width * (pos[0] - self.left) / (self.right - self.left),
                self.height * (pos[1] - self.top) / (self.bottom - self.top))
        if size is None:
            return wpos
        else:
            wsize = (self.width * size[0] / (self.right - self.left),
                     self.height * size[1] / (self.bottom - self.top))
            return wpos, wsize

    def world(self, pos, size=None):
        wpos = (self.left + pos[0] * (self.right - self.left) / self.width,
                self.top + pos[1] * (self.bottom - self.top) / self.height)
        if size is None:
            return wpos
        else:
            wsize = (size[0] * (self.right - self.left) / self.width,
                     size[1] * (self.bottom - self.top) / self.height)
            return wpos, wsize

    def random_pos(self):
        return (random.uniform(self.left, self.right),
                random.uniform(self.top, self.bottom))

    def add(self, actor):
        self.actors.append(actor)

    def empty(self):
        self.actors = []
