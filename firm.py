import math
from constants import *
from worker import Worker


class Firm:
    def __str__(self):
        return f'South: {self.is_south}, Primary: {self.is_primary}, Production: {self.production}, Price: {self.price}'

    def __init__(self, no_workers, initial_wage, capital, productivity, is_south=True, is_primary=True):
        self.workers = []
        for _ in range(no_workers):
            self.workers.append(Worker(initial_wage, is_south))
        self.last_y = 2 # TODO: Corrigir para production / last.production
        self.capital = capital
        self.last_capital = self.capital
        self.productivity = productivity
        self.demand = self.init_demand(is_south, is_primary)
        self.market_share = None if is_primary else 1 / (no_firm_s_m + no_firm_n_m)
        self.last_market_share = self.market_share
        self.markup = init_markup
        self.production = 5
        self.price = 1
        self.investment = 0
        self.is_south = is_south
        self.is_primary = is_primary
        self.id = -1
        self.last_profit = capital * productivity * self.price
        self.profit = self.last_profit
        self.primary_spend_rate = .4
        self.worker_primary_spend_rate = 1 if is_south else .5
        self.workers_wage_availability = 1.0

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
        return min(self.get_ex_demand() / self.productivity, self.capital / self.productivity)

    def get_allocated_labor(self):
        # Como a função é do tipo
        return math.ceil(self.get_allocated_capital() * self.productivity)

    def update_capital_s_p(self):
        return self.last_capital + self.last_y * savings_rate

    def get_production(self):
        return self.get_allocated_capital() / self.productivity

    def get_market_share(self, total_production):
        if self.is_primary and total_production == 0:
            return 0

        if total_production == 0 and not self.is_primary:
            print(f'[DEBUG] Firm.get_market_share - Skipping')
            print(self)
            return 0

        return self.get_production() / total_production

    def get_markup(self, total_production):
        return self.markup * (market_share_sensibility * (self.get_market_share(total_production) -
                                                          self.last_market_share) / self.last_market_share)

    @staticmethod
    def _get_wage_primary(mean_price, total_production):
        return real_wage * mean_price

    # TODO: EMBRODO, problema de circularidade e problema de lógica nos salarios (rever literatura)

    def _get_wage_manufacture(self, mean_price, total_production):
        return (self.get_production() / self.get_allocated_labor()) * (1 / 1 + self.get_markup(total_production))

    def _get_primary_price(self, mean_price, total_production):
        return (1 + self.markup) * self.productivity * self.get_wage(mean_price, total_production)

    def _get_manufacture_price(self, mean_price, total_production):
        return (1 + self.markup) * self.productivity * self.get_wage(mean_price, total_production)

    def update_workers(self, mean_price, total_production):
        remainder = self.workers[0].remainder # Redistribuimos qualquer recurso que tenha sobrado por destruir trabalhadores todo turno

        wage = self.get_wage(mean_price, total_production)
        no_workers = self.get_allocated_labor()
        self.workers = []
        for _ in range(no_workers): # -1 é o ultimo elemento da lista que é mais rapida com "_"
            self.workers.append(Worker(self.get_wage(mean_price, total_production),
                                       self.is_south, remainder / no_workers))
            self.workers[-1].remainder += wage

    def get_primary_demand_firm(self):
        return self.last_profit * self.primary_spend_rate

    def get_primary_demand_workers(self):
        return self.workers[0].remainder * len(self.workers) * self.worker_primary_spend_rate

    def get_manufacture_demand(self):
        return self.last_profit * (1 - self.primary_spend_rate) + \
               self.workers[0].wage * len(self.workers) * (1 - self.worker_primary_spend_rate)

    def update(self, mean_price, total_production):
        self.capital += self.get_investment()
        self.update_workers(mean_price, total_production)
        self.production = self.get_production()
        self.price = self.get_price(mean_price, total_production)
        self.profit = 0