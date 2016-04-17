import pygame


PADDING = 10
BORDER = 4


class Menu(object):
    def __init__(self, font, options, default=0):
        self.font = font
        self.options = options
        self.default = default
        self.selected = self.default
        self.top = 0.0

    def reset(self):
        self.selected = self.default

    def accept(self):
        self.options[self.selected][1](self)

    def prev(self):
        self.selected = (self.selected - 1) % len(self.options)

    def next(self):
        self.selected = (self.selected + 1) % len(self.options)

    def draw(self, surface):
        screen = surface.get_rect()
        rect = pygame.Rect((0, 10), (0,0))
        rect.midbottom = screen.midbottom
        for i, o in reversed(list(enumerate(self.options))):
            text = self.font.render(o[0], True, (0, 0, 0))
            text_rect = text.get_rect()

            button = text_rect.copy()
            button.width += 2 * PADDING
            button.height += 2 * PADDING

            box = button.copy()
            box.width += 2 * BORDER
            box.height += 2 * BORDER
            box.centerx = rect.centerx
            box.bottom = rect.top - PADDING

            button.center = box.center
            text_rect.center = button.center

            rect = box

            if i == self.selected:
                pygame.draw.rect(surface, (0, 0, 0), box)
                pygame.draw.rect(surface, (255, 255, 255), button)
            surface.blit(text, text_rect)
        self.top = box.top
