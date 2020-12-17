no_turns = 16

no_firm_s_m = 16
no_firm_s_p = 16
no_firm_n_m = no_firm_s_p + no_firm_s_m
no_firm_n_p = 0

wage_s = 16.0
wage_n = 16.0

capital_s_m = 16.0
capital_s_p = 17.0
capital_n_m = 16.0
capital_n_p = 0.0

productivity_s_m = 1.0
productivity_s_p = 1.0
productivity_n_m = 1.0
productivity_n_p = 1.0

no_workers_s_m = 16
no_workers_s_p = 16
no_workers_n_m = 16
no_workers_n_p = 0

savings_rate = 0.2


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
        self.last_capital = self.capital
        self.productivity = productivity

    def y(self):
        return self.capital / self.property

    def update(self):
        pass

    def update_capital_s_p(self):
        return self.last_capital + self.last_y * savings_rate

class World:
    def __init__(self):
        # Não existem no modelo, até o momento, firmas que produzem bens primários no Norte
        # no_firm_n_p = 0 não entra no loop

        self.firm_n_p = []
        for _ in range(no_firm_n_p):
            self.firm_n_m.append(Firm(no_workers_n_p, wage_n, capital_n_p, productivity_n_p, False))

        self.firm_n_m = []
        for _ in range(no_firm_n_m):
            self.firm_n_m.append(Firm(no_workers_n_m, wage_n, capital_n_m, productivity_n_m, False))

        self.firm_s_p = []
        for _ in range(no_firm_s_p):
            self.firm_s_p.append(Firm(no_workers_s_p, wage_s, capital_s_p, productivity_s_p))

        self.firm_s_m = []
        for _ in range(no_firm_s_m):
            self.firm_s_m.append(Firm(no_workers_s_m, wage_s, capital_s_m, productivity_s_m))

    def tick(self):
        pass

    def run(self):
        for _ in range(no_turns):
            self.tick()


if __name__ == '__main__':
    print('entra na minha casa')
    world = World()
    world.run()
