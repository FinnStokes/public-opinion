import states


TIMED = 0
NINETY = 1


class VictoryCondition(object):
    def __init__(self, state, meter):
        self.condition = TIMED
        self.state = state
        self.meter = meter

    def reset(self, condition=None):
        if condition is not None:
            self.condition = condition

        if self.condition == TIMED:
            self.time = 60.0
        elif self.condition == NINETY:
            self.time = 0.0

    def update(self, dt):
        if self.condition == TIMED:
            self.time -= dt
            if self.time <= 0.0:
                self.state.change(states.TIMED_VICTORY)
        elif self.condition == NINETY:
            self.time += dt
            if self.meter.blue_perc() >= 90.0:
                self.state.change(states.NINETY_VICTORY)
