import random
import time
from constants import *
from firm import Firm
import matplotlib.pyplot as plt
from scipy.stats import beta


class World:
    def __init__(self):
        firms_by_price = []
        # Não existem no modelo, até o momento, firmas que produzem bens primários no Norte
        # no_firm_n_p = 0 não entra no loop
        self.t = 0
        self.start_time = time.time()
        self.firms = []
        for _ in range(no_firm_n_p):
            self.firms.append(Firm(wage_n, capital_n_p, False))

        for _ in range(no_firm_n_m):
            self.firms.append(Firm(wage_n, capital_n_m, False, False))

        for _ in range(no_firm_s_p):
            self.firms.append(Firm(wage_s, capital_s_p))

        for _ in range(no_firm_s_m):
            self.firms.append(Firm(wage_s, capital_s_m, is_primary=False))



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
                mean_price += firm.price
            else:
                total_production_manufactured += firm.price * firm.production

        if (total_s_p + total_n_p) != 0:
            mean_price = mean_price / (total_s_p + total_n_p)

        # P&D
        innovation_list = beta.rvs(a_beta, b_beta, x_beta[0], x_beta[1], len(self.firms))
        #IMITATION
        t = time.time()
        k = len(self.firms)
        m = []
        for col in self.firms:
            n = []
            for row in self.firms:
                penalty = imitation_distance_penalty if not (row.is_south and col.is_south) else 0
                d = abs(col.labor_productivity - row.labor_productivity) * (1 + penalty)
                n.append(1 / d if d != 0 else 0)
            m.append(n)
            if self.t == no_turns - 1:
                print(n)
                # print(time.time() - t)

        #UPDATE
        i = 0
        for firm in self.firms:
            a = m[i]
            b = []
            r = random.random() *  sum(m[i])
            j = 0

            for p in a:
                if len(b) != 0:
                    b.append(p + b[-1])
                else:
                    b.append(p)
                if b[-1] > r:
                    break
                j += 1

            j -= 1
            # https://code.activestate.com/recipes/576564-walkers-alias-method-for-random-objects-with-diffe/

            firm.update(mean_price, total_production_primary, total_production_manufactured,innovation_list[i], self.firms[j].labor_productivity)
            firm.id = i
            i += 1

        self.firms.sort(key=lambda x: x.price, reverse=False)
        self.firms.sort(key=lambda x: not x.is_primary, reverse=False)

# MERCADO DOS PRODUTOS PRIMARIOS E MANUFATURADOS

        for seller in self.firms: # Primeira metade do vetor (Primarios)
            total_demand = self.get_total_demand_primary_tuple() if seller.is_primary \
                else self.get_total_demand_manufactured_tuple()

            for buyer in self.firms: # TODO: Separar o que do mundo e das fimas (proction * price)
                demand_to_print = None
                if seller.is_primary:
                    amount_to_buy_p = seller.production * seller.price * buyer.get_primary_demand_firm() / total_demand[0]
                    amount_to_buy_w_p = seller.production * seller.price * buyer.get_primary_demand_workers() / total_demand[1]
                    demand_to_print = buyer.get_primary_demand_firm()

                    # Venda
                    seller.profit += (amount_to_buy_p + amount_to_buy_p)

                    # Compra
                    buyer.expense_p -= amount_to_buy_p
                    #TODO:ARRUMAR trabalhador
                    buyer.workers[0].expense_p -= amount_to_buy_w_p / len(buyer.workers)

                else:
                    amount_to_buy_m = seller.production * seller.price * buyer.get_manufactured_demand_firm()/ total_demand[0]
                    amount_to_buy_w_m = seller.production * seller.price * buyer.get_manufactured_demand_workers() / total_demand[1]
                    demand_to_print = buyer.get_manufactured_demand_firm()

                    # Venda
                    seller.profit += (amount_to_buy_m + amount_to_buy_m)

                    # Compra
                    buyer.expense_m -= amount_to_buy_m
                    # TODO: Conferir trabalhador explodindo!
                    buyer.workers[0].expense_m -= amount_to_buy_w_m / len(buyer.workers)

                if debug:
                    self.demand_tsv += f'{seller.id}\t{amount_to_buy_m if not seller.is_primary else amount_to_buy_p}\t{demand_to_print}\t{seller.price}\t{seller.production}\t{buyer.id}\tp: {buyer.expense_p} m:{buyer.expense_m}\n'
            #TODO TIRAR GASTO COM INOVAÇAO E GASTO COM INVESTIMENTO
            seller.last_profit = seller.profit - seller.workers[0].wage
            seller.stock = seller.get_stock()
            seller.demand = seller.profit / seller.price

        # Investir em P&D (aqui)

        self.y.append(mean_price)
        self.t += 1

        if debug:
            for firm in self.firms:
                self.csv += f'{self.t}\t{firm.production}\t{firm.last_profit}\t{firm.market_share}\t{firm.markup}\t{firm.price}\t{firm.demand_series}\t{firm.is_south}\t{firm.is_primary}\t{firm.workers[0].remainder}\n'

    csv = 'turn\tfirm.production\tfirm.last_profit\tfirm.market_share\tfirm.markup\tfirm.price\tfirm.demand\tis.south\tis.primary\tfirm.workers[0].remainder\n'
    demand_tsv = 'seller id\tamount to buy\t demand\tseller price\tseller prod\tbuyer_id\texpense\n'
    def run(self):
        for _ in range(no_turns):
            self.tick()
        plt.plot(range(len(self.y)), self.y)
        # plt.show()
        with open(f'debug/_{time.clock()}', 'w') as file:
            file.write(self.csv)

        with open('debug_vendas.tsv', 'w') as file:
            file.write(self.demand_tsv)

        print(f'Simulation finished after:{time.time() - self.start_time}')