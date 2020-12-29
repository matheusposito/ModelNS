import time
from constants import *
from firm import Firm
import matplotlib.pyplot as plt

class World:
    def __init__(self):
        firms_by_price = []
        # Não existem no modelo, até o momento, firmas que produzem bens primários no Norte
        # no_firm_n_p = 0 não entra no loop
        self.t = 0
        self.start_time = time.time()
        self.firms_n_p = []
        for _ in range(no_firm_n_p):
            self.firms_n_m.append(Firm(no_workers_n_p, wage_n, capital_n_p, False))

        self.firms_n_m = []
        for _ in range(no_firm_n_m):
            self.firms_n_m.append(Firm(no_workers_n_m, wage_n, capital_n_m, False, False))

        self.firms_s_p = []
        for _ in range(no_firm_s_p):
            self.firms_s_p.append(Firm(no_workers_s_p, wage_s, capital_s_p))

        self.firms_s_m = []
        for _ in range(no_firm_s_m):
            self.firms_s_m.append(Firm(no_workers_s_m, wage_s, capital_s_m, is_primary=False))

    def get_mean_primary_south_price(self):
        mean = 0
        for firm in self.firms_s_p:
            mean += firm.price
        mean = mean / len(self.firms_s_p)
        return mean

    def get_total_demand_quadruple(self):
        total_firm_primary_demand = 0
        total_workers_primary_demand = 0
        total_firm_manufactured_demand = 0
        total_workers_manufactured_demand = 0

        for firm in self.firms_s_p:
            total_firm_primary_demand += firm.get_primary_demand_firm()
            total_workers_primary_demand += firm.get_primary_demand_workers()
            total_firm_manufactured_demand += firm.get_manufactured_demand_firm()
            total_workers_manufactured_demand += firm.get_manufactured_demand_workers()

        for firm in self.firms_s_m:
            total_firm_primary_demand += firm.get_primary_demand_firm()
            total_workers_primary_demand += firm.get_primary_demand_workers()
            total_firm_manufactured_demand += firm.get_manufactured_demand_firm()
            total_workers_manufactured_demand += firm.get_manufactured_demand_workers()

        for firm in self.firms_n_p:
            total_firm_primary_demand += firm.get_primary_demand_firm()
            total_workers_primary_demand += firm.get_primary_demand_workers()
            total_firm_manufactured_demand += firm.get_manufactured_demand_firm()
            total_workers_manufactured_demand += firm.get_manufactured_demand_workers()

        for firm in self.firms_n_m:
            total_firm_primary_demand += firm.get_primary_demand_firm()
            total_workers_primary_demand += firm.get_primary_demand_workers()
            total_firm_manufactured_demand += firm.get_manufactured_demand_firm()
            total_workers_manufactured_demand += firm.get_manufactured_demand_workers()

        return total_firm_primary_demand, total_workers_primary_demand, total_firm_manufactured_demand, total_workers_manufactured_demand

    y = []
    csv = 'turn\tfirm.production\tfirm.last_profit\tfirm.market_share\tfirm.markup\tfirm.price\tfirm.demand\tis.south\tis.primary\tfirm.workers[0].remainder\tfirm.workers[1].remainder\n'

    def tick(self):
        print(f'--- {self.t} ------')
        mean_price = 0
        total_production_manufactured = 0
        total_production_primary = 0

        for firm in self.firms_n_m + self.firms_s_m:
            total_production_manufactured += firm.price * firm.production

        for firm in self.firms_n_p + self.firms_s_p:
            total_production_primary += firm.price * firm.production

        if len(self.firms_s_p) + len(self.firms_n_p) != 0:
            for firm in self.firms_s_p + self.firms_n_p:
                mean_price += firm.price
            mean_price /= (len(self.firms_s_p) + len(self.firms_n_p))

        i = 0
        for firm in self.firms_s_p:
            firm.update(mean_price, total_production_primary, total_production_manufactured)
            firm.id = i
            i += 1
        i = 0

        for firm in self.firms_s_m:
            firm.update(mean_price, total_production_primary, total_production_manufactured)
            firm.id = i
            i += 1
        i = 0

        for firm in self.firms_n_p:
            firm.update(mean_price, total_production_primary, total_production_manufactured)
            firm.id = i
            i += 1
        i = 0

        for firm in self.firms_n_m:
            firm.update(mean_price, total_production_primary, total_production_manufactured)
            firm.id = i
            i += 1

        firms_by_price_p = self.firms_s_p + self.firms_n_p
        firms_by_price_p.sort(key=lambda x: x.price, reverse=False)

        firms_by_price_m = self.firms_s_m + self.firms_n_m
        firms_by_price_m.sort(key=lambda x: x.price, reverse=False)

# MERCADO DOS PRODUTOS PRIMARIOS
        for seller in firms_by_price_p:

            total_primary_demand = self.get_total_demand_quadruple()

            for buyer in self.firms_s_p + self.firms_s_m + self.firms_n_p + self.firms_n_m:
                amount_to_buy = seller.production * buyer.get_primary_demand_firm() / total_primary_demand[0]
                amount_to_buy_w = seller.production * buyer.get_primary_demand_workers() / total_primary_demand[1]

                # Venda
                if seller.is_south:
                    if seller.is_primary:
                        self.firms_s_p[seller.id].profit += amount_to_buy + amount_to_buy_w
                    else:
                        self.firms_s_m[seller.id].profit += amount_to_buy + amount_to_buy_w
                else:
                    if seller.is_primary:
                        self.firms_n_p[seller.id].profit += amount_to_buy + amount_to_buy_w
                    else:
                        self.firms_n_m[seller.id].profit += amount_to_buy + amount_to_buy_w

                # Compra
                if buyer.is_south:
                    if buyer.is_primary:
                        self.firms_s_p[buyer.id].last_profit -= amount_to_buy
                        self.firms_s_p[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_s_p[buyer.id].workers)
                    else:
                        self.firms_s_m[buyer.id].last_profit -= amount_to_buy
                        self.firms_s_m[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_s_m[buyer.id].workers)
                else:
                    if buyer.is_primary:
                        self.firms_n_p[buyer.id].last_profit -= amount_to_buy
                        self.firms_n_p[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_n_p[buyer.id].workers)

                    else:
                        self.firms_n_m[buyer.id].last_profit -= amount_to_buy
                        self.firms_n_m[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_n_m[buyer.id].workers)

# MERCADO DOS PRODUTOS MANUFATURADOS
        for seller in firms_by_price_m:

            total_manufactured_demand = self.get_total_demand_quadruple()

            for buyer in self.firms_s_p + self.firms_s_m + self.firms_n_p + self.firms_n_m:
                amount_to_buy = seller.production * buyer.get_manufactured_demand_firm() / total_manufactured_demand[2]
                amount_to_buy_w = seller.production * buyer.get_manufactured_demand_workers() / total_manufactured_demand[3]

                # Venda
                if seller.is_south:
                    if seller.is_primary:
                        self.firms_s_p[seller.id].profit += amount_to_buy + amount_to_buy_w
                    else:
                        self.firms_s_m[seller.id].profit += amount_to_buy + amount_to_buy_w
                else:
                    if seller.is_primary:
                        self.firms_n_p[seller.id].profit += amount_to_buy + amount_to_buy_w
                    else:
                        self.firms_n_m[seller.id].profit += amount_to_buy + amount_to_buy_w

                # Compra
                if buyer.is_south:
                    if buyer.is_primary:
                        self.firms_s_p[buyer.id].last_profit -= amount_to_buy
                        self.firms_s_p[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_s_p[buyer.id].workers)
                    else:
                        self.firms_s_m[buyer.id].last_profit -= amount_to_buy
                        self.firms_s_m[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_s_m[buyer.id].workers)
                else:
                    if buyer.is_primary:
                        self.firms_n_p[buyer.id].last_profit -= amount_to_buy
                        self.firms_n_p[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_n_p[buyer.id].workers)

                    else:
                        self.firms_n_m[buyer.id].last_profit -= amount_to_buy
                        self.firms_n_m[buyer.id].workers[0].remainder -= amount_to_buy_w / len(self.firms_n_m[buyer.id].workers)

        # Investir em P&D (aqui)

        self.y.append(mean_price)
        self.t += 1
        for firm in self.firms_s_p + self.firms_s_m + self.firms_n_m + self.firms_n_p:
            self.csv += f'{self.t}\t{firm.production}\t{firm.last_profit}\t{firm.market_share}\t{firm.markup}\t{firm.price}\t{firm.demand}\t{firm.is_south}\t{firm.is_primary}\t{firm.workers[0].remainder}\t{firm.workers[1].remainder}\n'

    def run(self):
        for _ in range(no_turns):
            self.tick()
        plt.plot(range(len(self.y)), self.y)
        # plt.show()
        with open('debug.tsv', 'w') as file:
            file.write(self.csv)

        print(f'Simulation finished after:{time.time() - self.start_time}')