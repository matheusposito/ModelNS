no_turns = 16

no_firm_s_m = 16
no_firm_s_p = 16
no_firm_n_m = no_firm_s_p + no_firm_s_m
no_firm_n_p = 0

gamma_0 = 0.2
gamma_1 = 0.1

wage_s = 16.0
wage_n = 16.0

capital_s_m = 16.0
capital_s_p = 17.0
capital_n_m = 16.0
capital_n_p = 0.0

demand_s_m = 5
demand_s_p = 5
demand_n_m = 5
demand_n_p = 0

demand_series_weight = [.6, .5, .4]

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
    def __init__(self, no_workers, initial_wage, capital, productivity, is_south=True, is_primary=True,):
        self.workers = []
        for _ in range(no_workers):
            self.workers.append(Worker(initial_wage, is_south))
        self.last_y = 2
        self.capital = capital
        self.last_capital = self.capital
        self.productivity = productivity
        self.demand = self.init_demand(is_south, is_primary)
        self.get_investment = self._get_investment_primary if is_primary else self._get_investment_manufacture

    @staticmethod
    def init_demand(is_south, is_primary):
        if is_south:
            if is_primary:
                d = demand_s_p
            else:
                d = demand_s_m
        else:
            if is_primary:
                d = demand_n_p
            else:
                d = demand_n_m
        return [d] * len(demand_series_weight)

    def get_ex_demand(self):
        return sum([a[0] * a[1] for a in tuple(zip(self.demand, demand_series_weight))])

    def _get_investment_primary(self):
        return self.last_y * savings_rate

    def _get_investment_manufacture(self):
        return (gamma_0 + gamma_1 * (self.get_ex_demand() / self.productivity)) * self.capital

    # TODO: refazer porque precisa olhar a demanda experada
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
            self.firm_n_m.append(Firm(no_workers_n_m, wage_n, capital_n_m, productivity_n_m, False, False))

        self.firm_s_p = []
        for _ in range(no_firm_s_p):
            self.firm_s_p.append(Firm(no_workers_s_p, wage_s, capital_s_p, productivity_s_p))

        self.firm_s_m = []
        for _ in range(no_firm_s_m):
            self.firm_s_m.append(Firm(no_workers_s_m, wage_s, capital_s_m, productivity_s_m, is_primary=False))

    def tick(self):
        print(self.firm_s_p[0].get_investment())
        pass

    def run(self):
        for _ in range(no_turns):
            self.tick()


if __name__ == '__main__':
    print('entra na minha casa')
    world = World()
    world.run()
