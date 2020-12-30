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
        self.firms = []
        self.firms_n_p = []
        for _ in range(no_firm_n_p):
            self.firms.append(Firm(no_workers_n_p, wage_n, capital_n_p, False))

        self.firms_n_m = []
        for _ in range(no_firm_n_m):
            self.firms.append(Firm(no_workers_n_m, wage_n, capital_n_m, False, False))

        self.firms_s_p = []
        for _ in range(no_firm_s_p):
            self.firms.append(Firm(no_workers_s_p, wage_s, capital_s_p))

        self.firms_s_m = []
        for _ in range(no_firm_s_m):
            self.firms.append(Firm(no_workers_s_m, wage_s, capital_s_m, is_primary=False))

    # def get_mean_primary_south_price(self):
    #     mean = 0
    #     for firm in self.firms_s_p:
    #         mean += firm.price
    #     mean = mean / len(self.firms_s_p)
    #     return mean

    def get_total_demand_primary_tuple(self):
        total_firm_primary_demand = 0
        total_workers_primary_demand = 0

        for firm in self.firms:
            total_firm_primary_demand += firm.get_primary_demand_firm()
            total_workers_primary_demand += firm.get_primary_demand_workers()

        return total_firm_primary_demand, total_workers_primary_demand

    def get_total_demand_manufactured_tuple(self):
        total_firm_manufactured_demand = 0
        total_workers_manufactured_demand = 0

        for firm in self.firms:
            total_firm_manufactured_demand += firm.get_manufactured_demand_firm()
            total_workers_manufactured_demand += firm.get_manufactured_demand_workers()

        return total_firm_manufactured_demand, total_workers_manufactured_demand

    y = []
    csv = ''# 'turn\tfirm.production\tfirm.last_profit\tfirm.market_share\tfirm.markup\tfirm.price\tfirm.demand\tis.south\tis.primary\tfirm.workers[0].remainder\tfirm.workers[1].remainder\n'

    def tick(self):
        print(f'--- {self.t} ------')
        mean_price = 0
        total_production_manufactured = 0
        total_production_primary = 0

        total_s_p = 0
        total_s_m = 0
        total_n_p = 0
        total_n_m = 0

        for firm in self.firms:
            total_s_p += 1 if firm.is_south and firm.is_primary else 0
            total_s_m += 1 if firm.is_south and (not firm.is_primary) else 0
            total_n_p += 1 if (not firm.is_south) and firm.is_primary else 0
            total_n_m += 1 if (not firm.is_south) and (not firm.is_primary) else 0

            if firm.is_primary:
                total_production_primary += firm.price * firm.production
            else:
                total_production_manufactured += firm.price * firm.production


        # for firm in self.firms_n_m + self.firms_s_m:
        #     total_production_manufactured += firm.price * firm.production
        #
        # for firm in self.firms_n_p + self.firms_s_p:
        #     total_production_primary += firm.price * firm.production

        if total_s_p + total_n_p != 0:
            for firm in self.firms_s_p + self.firms_n_p:
                mean_price += firm.price
            mean_price = mean_price / (total_s_p + total_n_p)

        i = 0
        for firm in self.firms:
            firm.update(mean_price, total_production_primary, total_production_manufactured)
            firm.id = i
            i += 1

        self.firms.sort(key=lambda x: x.price, reverse=False)
        self.firms.sort(key=lambda x: not x.is_primary, reverse=False)

# MERCADO DOS PRODUTOS PRIMARIOS E MANUFATURADOS

        for seller in self.firms[:total_s_p + total_n_p:]:
            total_demand = self.get_total_demand_primary_tuple() if seller.is_primary \
                else self.get_total_demand_manufactured_tuple()

            for buyer in self.firms:
                if buyer.is_primary:
                    amount_to_buy = seller.production * buyer.get_primary_demand_firm() / total_demand[0]
                    amount_to_buy_w = seller.production * buyer.get_primary_demand_workers() / total_demand[1]
                else:
                    amount_to_buy = seller.production * buyer.get_manufactured_demand_firm() / total_demand[0]
                    amount_to_buy_w = seller.production * buyer.get_manufactured_demand_workers() / total_demand[1]

                # Venda
                seller.profit += amount_to_buy + amount_to_buy_w

                # Compra
                buyer.last_profit -= amount_to_buy
                buyer.workers[0].remainder -= amount_to_buy_w / len(buyer.workers)

        # Investir em P&D (aqui)

        self.y.append(mean_price)
        self.t += 1
        for firm in self.firms_s_p + self.firms_s_m + self.firms_n_m + self.firms_n_p:
            pass
            #self.csv += f'{self.t}\t{firm.production}\t{firm.last_profit}\t{firm.market_share}\t{firm.markup}\t{firm.price}\t{firm.demand}\t{firm.is_south}\t{firm.is_primary}\t{firm.workers[0].remainder}\t{firm.workers[1].remainder}\n'

    def run(self):
        for _ in range(no_turns):
            self.tick()
        plt.plot(range(len(self.y)), self.y)
        # plt.show()
        with open('debug.tsv', 'w') as file:
            file.write(self.csv)

        print(f'Simulation finished after:{time.time() - self.start_time}')