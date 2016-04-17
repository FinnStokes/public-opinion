QUITTING = 0
MAIN_MENU = 1
PAUSE_MENU = 2
GAME = 3


class State(object):
    def __init__(self, state):
        self.state = state
        self.entered = True

    def change(self, state):
        self.state = state
        self.entered = True

    def on_enter(self):
        if self.entered:
            self.entered = False
            return True
        return False

    def close(self):
        if self == PAUSE_MENU:
            self.change(GAME)

    def __eq__(self, state):
        return state == self.state
