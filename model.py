from enum import Enum

no_turns = 12
wage_n = 12
wage_s = 12


class WorkerType(Enum):
    pass


class Worker:
    def __init__(self, wage, is_south=True, remainder=0):
        self.wage = wage
        self.remainder = remainder
        self.is_south = is_south


class Firm:
    def __init__(self, no_workers, initial_wage, capital, productivity, is_south=True):
        self.workers = []
        for _ in range(no_workers):
            self.workers.append(Worker(initial_wage, is_south))

        self.capital = capital
        self.productivity = productivity


class World:
    def __init__(self):
        firm = Firm(10, 20, 1, 0.1)
        pass

    def tick(self):
        pass

    def run(self):
        for _ in range(no_turns):
            pass


if __name__ == '__main__':
    print('entra na minha casa')
    world = World()
