import pygame


class Meter(pygame.sprite.Sprite):
    def __init__(self, rect, font, col):
        pygame.sprite.Sprite.__init__(self)
        self.format = " {:.1f}% "
        fontrect = font.render(self.format.format(100.0), True, (0, 0, 0)).get_rect()
        self.rect = rect.copy()
        self.rect.width += 2 * fontrect.width
        self.rect.height = max(rect.height, fontrect.height)
        self.rect.center = rect.center
        self.fill_rect = rect.copy()
        self.fill_rect.center = (self.rect.width / 2, self.rect.height / 2)
        self.blue = 0
        self.red = 0
        self.blue_frac = 0.5
        self.red_frac = 0.5
        self.colours = col
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.font = font

    def update(self, blue, red):
        self.blue = blue
        self.red = red
        if blue + red > 0:
            self.blue_frac = blue * 1.0 / (red + blue)
            self.red_frac = red * 1.0 / (red + blue)

        self.image.fill((255, 255, 255, 0))
        pygame.draw.rect(self.image, (0, 0, 0), self.fill_rect)
        fillrect = self.fill_rect.copy()
        fillrect.width -= 2
        fillrect.height -= 2
        fillrect.center = self.fill_rect.center
        pygame.draw.rect(self.image, self.colours.red(), fillrect)
        bar_rect = fillrect.copy()
        bar_rect.width = int(bar_rect.width*self.blue_frac)
        pygame.draw.rect(self.image, self.colours.blue(), bar_rect)
        line_rect = bar_rect.copy()
        line_rect.width = 1
        line_rect.right = bar_rect.right
        pygame.draw.rect(self.image, (0, 0, 0), line_rect)

        blue_percent = self.font.render(self.format.format(self.blue_perc()), True, self.colours.dblue())
        blue_rect = blue_percent.get_rect()
        blue_rect.midright = self.fill_rect.midleft
        self.image.blit(blue_percent, blue_rect)

        red_percent = self.font.render(self.format.format(self.red_perc()), True, self.colours.dred())
        red_rect = red_percent.get_rect()
        red_rect.midleft = self.fill_rect.midright
        self.image.blit(red_percent, red_rect)

    def red_perc(self):
        return 100.0*self.red_frac

    def blue_perc(self):
        return 100.0*self.blue_frac
