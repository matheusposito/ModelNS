import math
from constants import *
from scipy.stats import beta
import random
from math import e
from worker import Worker

#TODO: DIVIDIR RECEITA DE PROFIT, DESCONTAR INVESTIMENTO E P&D ANTES DE COMPRAR PRIMARIO E CONFERIR O QUE ESTÁ ACONTECENDO COM STOCKS, PROFIT, RECEITA, buyer.expense_m e remender!!!
class Firm:
    def __str__(self):
        return f'{self.__hash__()} South: {self.is_south}, Primary: {self.is_primary}, Markup:{self.markup}, Marketshare: {self.market_share} profit: {self.profit}, Production: {self.production}, Price: {self.price}, no_worker:{self.no_workers}, w_remender: {self.std_worker.remainder} dmd series: {self.demand_series}'

    def __init__(self, initial_wage, capital, is_south=True, is_primary=True):
        self.is_south = is_south
        self.is_primary = is_primary
        self.id = -1
        self.capital = capital
        self.last_capital = self.capital
        self.stock = 0
        self.demand_series = self.init_demand(is_south, is_primary)  # TODO: parametrizar baseado na produção e nas pref.
        self.demand = self.demand_series[0]
        self.market_share = 1 / (no_firm_s_p + no_firm_n_p) if is_primary else 1 / (no_firm_s_m + no_firm_n_m)
        self.last_market_share = self.market_share
        self.markup = init_markup
        self.price = 1
        self.investment = 0
        # TODO: Adicionar as funções de consumo:
        self.primary_spend_rate = .4
        self.worker_primary_spend_rate = 1 if is_south else .5
        self.workers_wage_availability = 1.0

        if is_primary:
            self.get_investment = self._get_investment_primary
            self.get_price = self._get_primary_price
            self.price = init_primary_price
            #TODO: Wage divide por norte e Sul, mudar formula de wage
            self.get_wage = self._get_wage_primary
            self.labor_productivity = labor_productivity_s_p if is_south else labor_productivity_n_p
            self.capital_productivity = capital_productivity_s_p if is_south else capital_productivity_n_p

        else:
            self.get_investment = self._get_investment_manufacture
            self.get_price = self._get_manufacture_price
            self.price = init_manufacture_price
            self.get_wage = self._get_wage_manufacture
            self.labor_productivity = labor_productivity_s_m if is_south else labor_productivity_n_m
            self.capital_productivity = capital_productivity_s_m if is_south else capital_productivity_n_m

        self.production = self.capital * self.capital_productivity  # TODO: Capacidade ociosa
        self.last_profit = self.production * self.price
        self.profit = self.last_profit
        self.expense_p = self.last_profit * self.primary_spend_rate
        self.expense_m = self.last_profit * (1 - self.primary_spend_rate)
        self.no_workers = self.get_allocated_labor()


        # Hack para deixar calculo mais rapido, voltar caso trabalhadores passsem a ser agentes
        self.std_worker = Worker(initial_wage * self.no_workers, self.is_south, 0)
        # for _ in range(self.get_allocated_labor()):
        #     self.workers.append(Worker(initial_wage, is_south))

        self.profit_rate = self.get_profit_rate()
    @staticmethod
    #TODO: Retirar a variavel demand e colocar em função da proporção do consumo e da renda inicial
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
        return sum([a[0] * a[1] for a in tuple(zip(self.demand_series, demand_series_weight))])

    def update_ex_demand_series(self):
        # for i in range(len(self.demand))[::-1]: Quando precisar inverter o for
        for i in range(len(self.demand_series)):
            self.demand_series[len(self.demand_series) - 1 - i] = self.demand_series[len(self.demand_series) - 2 - i]
        self.demand_series[0] = self.demand

    def get_allocated_capital(self):
        #TODO: Reduzir o estoque () condicional a zerar caso seja menor q zero
        alloc_cap = max(min((self.get_ex_demand() - self.stock) / self.capital_productivity, self.capital - (self.stock / self.capital_productivity)), 0)
        return  alloc_cap

    def _get_investment_primary(self):
        return (gamma_0 + gamma_1 * (self.get_allocated_capital() / self.capital)) * self.capital

    def _get_investment_manufacture(self):
        return (gamma_0 + gamma_1 * (self.get_allocated_capital() / self.capital)) * self.capital

    # arredonda para cima
    def get_allocated_labor(self):
        n_workers = math.ceil(self.get_allocated_capital() * self.capital_productivity / self.labor_productivity)
        if self.id == 0:
            print(1)
        return  n_workers

    def get_production(self):
        return self.get_allocated_capital() * self.capital_productivity

    def get_market_share(self, total_production_primary, total_production_manufactured):
        if self.is_primary:
            return self.get_production() / total_production_primary
        else:
            return self.get_production() / total_production_manufactured

    def get_markup(self, total_production_primary, total_production_manufactured):
        if self.is_primary:
            return self.markup * (1 + market_share_sensibility * ((self.get_market_share(total_production_primary, total_production_manufactured) -
                                                              self.last_market_share))/ self.last_market_share)
        else:
            return self.markup * (1 + market_share_sensibility * ((self.get_market_share(total_production_primary, total_production_manufactured) -
                                                              self.last_market_share)) / self.last_market_share)

    #@staticmethod
    def _get_wage_primary(self, mean_price):
        return (1 / (1 + self.markup) * self.last_profit) / self.no_workers
        #return real_wage

    def _get_wage_manufacture(self, mean_price):
        return (1 / (1  + self.markup) * self.last_profit) / self.no_workers


    def _get_primary_price(self, mean_price, total_production_primary, total_production_manufactured):
        return ((1 + self.markup) * self.get_wage(mean_price) / self.labor_productivity)

    def _get_manufacture_price(self, mean_price, total_production_primary, total_production_manufactured):
        return ((1 + self.markup) * self.get_wage(mean_price) / self.labor_productivity)

    def update_std_worker(self, mean_price):
        self.std_worker.remainder = self.std_worker.expense_p + self.std_worker.expense_m # Redistribuimos qualquer recurso que tenha sobrado por destruir trabalhadores todo turno

        self.std_worker.wage = self.get_wage(mean_price)

        if self.no_workers <= 0:
            print(0)
        if self.id == 0:
            print( f'No Workers f0: {self.no_workers}')

        self.std_worker.remainder += self.std_worker.wage
        self.std_worker.expense_p = self.std_worker.remainder * self.std_worker.worker_primary_spend_rate
        if self.std_worker.remainder < 0:
            print('')
        self.std_worker.expense_m = self.std_worker.remainder * (1 - self.std_worker.worker_primary_spend_rate)
        self.std_worker.remainder = 0


    def get_primary_demand_firm(self):
        return self.expense_p

    def get_primary_demand_workers(self):
        if self.no_workers <= 0:
            return 0

        return self.std_worker.expense_p * self.no_workers

    def get_manufactured_demand_firm(self):
        return self.expense_m

    def get_manufactured_demand_workers(self):
        if self.no_workers <= 0:
            return 0
        d = self.std_worker.expense_m * self.no_workers
        if d < 0:
            print('')
        return d

    def get_stock(self):
        return (self.production * self.price - self.profit) / self.price


    def get_investment_innovation(self):
         return lambda_1 * rho * self.get_investment()

    def get_investment_imitation(self):
        return (1 - lambda_1) * rho * self.get_investment()

    def get_innovation(self,innovation_beta):
        s =self.get_investment_innovation()
        f = random.random()
        g = 1 - e ** (-xi_1 * s)
        if f < min(theta_max_1, g):
            return innovation_beta
        else:
            return 0

    def get_imitation(self, imitation_labor_productivity):
        if random.random() < min(theta_max_2, 1 - e ** (-xi_2 * self.get_investment_imitation())):
            return imitation_labor_productivity
        else:
            return 0

    def update_labor_productivity(self, innovation_beta, imitation_labor_productivity):
        return
        #self.labor_productivity = max(self.labor_productivity,self.labor_productivity * (1 + self.get_innovation(innovation_beta)), imitation_labor_productivity)

    def get_south_spend_rate(self):
        pass

    def get_north_spend_rate(self):
        pass

    def get_profit_rate(self):
        if self.production == 0 or self.price == 0:
            print(f'[ERROR] firm id: {self.id}: Prod  ou price nao podem ser 0 price:{self.price} | prod:{self.production}')
            return .5
        profit_rate = (self.production * self.price - self.std_worker.wage * self.no_workers) / self.production * self.price
        return profit_rate

    def update(self, mean_price, total_production_primary, total_production_manufactured,innovation_beta, imitation_labor_productivity):
        if self.id == 0:
            print(f'ex demand : {self.get_ex_demand()}\n{self}')

        self.update_ex_demand_series()
        self.update_labor_productivity(innovation_beta, imitation_labor_productivity)
        self.markup = self.get_markup(total_production_primary, total_production_manufactured)
        self.capital += self.get_investment()
        self.production = self.get_production()
        self.no_workers = self.get_allocated_labor()
        # mecanismo de falencia
        if self.production <= 0 or self.profit <= 0:
            id = self.id
            self.__init__(wage_s if self.is_south else wage_n, 16, self.is_south, self.is_primary)
            self.id = id
            # self.stock = 0
            # self.wage = 1
            # self.capital = 16
            # self.demand_series = d
            # self.production = self.get_production()
            # self.no_workers = self.get_allocated_labor()


        self.update_std_worker(mean_price)

#       self.stock = self.production
        self.price = self.get_price(mean_price, total_production_primary, total_production_manufactured)
        self.profit = 0
        self.expense_p = self.last_profit * self.primary_spend_rate
        self.expense_m = self.last_profit * (1 - self.primary_spend_rate)
        self.profit_rate = self.get_profit_rate()
        return False