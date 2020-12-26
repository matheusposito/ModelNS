class Worker:
    def __init__(self, wage, is_south=True, remainder=0.0):
        self.wage = wage
        self.remainder = remainder
        self.is_south = is_south
