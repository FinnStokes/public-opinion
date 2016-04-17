class Colours(object):
    def __init__(self):
        self.cb_mode = False

    def red(self):
        if self.cb_mode:
            return (255, 255, 255)
        else:
            return (255, 0, 0)

    def blue(self):
        if self.cb_mode:
            return (0, 0, 0)
        else:
            return (0, 0, 255)

    def dred(self):
        if self.cb_mode:
            return (0, 0, 0)
        else:
            return (100, 0, 0)

    def dblue(self):
        if self.cb_mode:
            return (0, 0, 0)
        else:
            return (0, 0, 100)
