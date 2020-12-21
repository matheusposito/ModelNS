import math

no_turns = 16

wage_s = 16.0
wage_n = 16.0

real_wage = 8
init_primary_price = 1
init_manufacture_price = 1

init_markup = 1

no_firm_s_m = 16
no_firm_s_p = 16
no_firm_n_m = no_firm_s_p + no_firm_s_m
no_firm_n_p = 0

market_share_sensibility = 0.1
gamma_0 = 0.2
gamma_1 = 0.1

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
    def __init__(self, wage, is_south=True, remainder=0.0):
        self.wage = wage
        self.remainder = remainder
        self.is_south = is_south


class Firm:
    def __init__(self, no_workers, initial_wage, capital, productivity, is_south=True, is_primary=True):
        self.workers = []
        for _ in range(no_workers):
            self.workers.append(Worker(initial_wage, is_south))
        self.last_y = 2
        self.capital = capital
        self.last_capital = self.capital
        self.productivity = productivity
        self.demand = self.init_demand(is_south, is_primary)
        self.market_share = None if is_primary else 1 / (no_firm_s_m + no_firm_n_m)
        self.last_market_share = self.market_share
        self.markup = init_markup
        self.production = 0
        self.price = 0
        self.investment = 0
        self.is_south = is_south
        if is_primary:
            self.get_investment = self._get_investment_primary
            self.get_price = self._get_primary_price
            self.price = init_primary_price
            self.get_wage = self._get_wage_primary

        else:
            self.get_investment = self._get_investment_manufacture
            self.get_price = self._get_manufacture_price
            self.price = init_manufacture_price
            self.get_wage = self._get_wage_manufacture
            
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

    # TODO: O investimento do setor primario está em função da renda, precisa ficar em função o capital
    def _get_investment_primary(self):
        return self.last_y * savings_rate

    def _get_investment_manufacture(self):
        return (gamma_0 + gamma_1 * (self.get_ex_demand() / self.productivity)) * self.capital

    def get_allocated_capital(self):
        return self.get_ex_demand() / self.productivity

    def get_allocated_labor(self):
        # Como a função é do tipo
        return math.ceil(self.get_allocated_capital() * self.productivity)

    def update_capital_s_p(self):
        return self.last_capital + self.last_y * savings_rate

    def get_production(self):
        return self.get_allocated_capital() / self.productivity

    def get_market_share(self, total_y):
        return self.get_production() / total_y

    def get_markup(self, total_y):
        return self.markup * (market_share_sensibility * (self.get_market_share(total_y) -
                                                          self.last_market_share) / self.last_market_share)

    @staticmethod
    def _get_wage_primary(mean_price):
        return real_wage * mean_price

    # TODO: EMBRODO, problema de circularidade e problema de lógica nos salarios (rever literatura)

    def _get_wage_manufacture(self, mean_price):
        return (self.get_production() / self.get_allocated_labor()) * (1 / 1 + self.get_markup())

    def _get_primary_price(self):
        return 0

    def _get_manufacture_price(self):
        return 0

    def update_workers(self, mean_price):
        remainder = 0
        for worker in self.workers:
            remainder += worker.remainder
        no_workers = self.get_allocated_labor()
        self.workers = []
        for _ in range(no_workers):
            self.workers.append(Worker(self.get_wage(mean_price), self.is_south, remainder / no_workers))

    def update(self, mean_price):
        self.capital += self.get_investment()
        self.update_workers(mean_price)
        self.production = self.get_production()
        self.price = self.get_price()
        pass


class World:
    def __init__(self):
        # Não existem no modelo, até o momento, firmas que produzem bens primários no Norte
        # no_firm_n_p = 0 não entra no loop

        self.firms_n_p = []
        for _ in range(no_firm_n_p):
            self.firms_n_m.append(Firm(no_workers_n_p, wage_n, capital_n_p, productivity_n_p, False))

        self.firms_n_m = []
        for _ in range(no_firm_n_m):
            self.firms_n_m.append(Firm(no_workers_n_m, wage_n, capital_n_m, productivity_n_m, False, False))

        self.firms_s_p = []
        for _ in range(no_firm_s_p):
            self.firms_s_p.append(Firm(no_workers_s_p, wage_s, capital_s_p, productivity_s_p))

        self.firms_s_m = []
        for _ in range(no_firm_s_m):
            self.firms_s_m.append(Firm(no_workers_s_m, wage_s, capital_s_m, productivity_s_m, is_primary=False))

    def get_mean_primary_south_price(self):
        mean = 0
        for firm in self.firms_s_p:
            mean += firm.price
        mean = mean / len(self.firms_s_p)
        return mean

    def tick(self):
        print(self.firms_s_p[0].get_investment())
        mean_price = 0
        if len(self.firms_s_p) + len(self.firms_n_m) != 0:
            for firm in self.firms_s_p + self.firms_n_p:
                mean_price += firm.price
            mean_price /= (len(self.firms_s_p) + len(self.firms_n_p))

        for firm in self.firms_s_p + self.firms_s_m + self.firms_n_p + self.firms_n_m:
            firm.update(mean_price)
        # Investir em P&D (aqui)
        pass

    def run(self):
        for _ in range(no_turns):
            self.tick()


if __name__ == '__main__':
    print('entra na minha casa')
    world = World()
    world.run()
