
debug = True
no_turns = 10

wage_s = 1.0
wage_n = 1.0

real_wage = 1
init_primary_price = 1
init_manufacture_price = 1

init_markup = 2

no_firm_s_m = 5
no_firm_s_p = 5
no_firm_n_m = no_firm_s_p + no_firm_s_m
no_firm_n_p = 0

market_share_sensibility = 0.1
gamma_0 = 0.2
gamma_1 = 0.1

capital_s_m = 16.0
capital_s_p = 16.0
capital_n_m = 16.0
capital_n_p = 0.0


# TODO: DEMANDA DEVE DEPENDER DO GRAU DE UTILIZAÇÃO E DA PRODUÇÃO ANTERIOR
demand_s_m = 5
demand_s_p = 5
demand_n_m = 5
demand_n_p = 0

demand_series_weight = [.3, .3, .3]

labor_productivity_s_m = 1
labor_productivity_s_p = 1
labor_productivity_n_m = 1
labor_productivity_n_p = 1

capital_productivity_s_m = 1
capital_productivity_s_p = 1
capital_productivity_n_m = 1
capital_productivity_n_p = 1

savings_rate = 0.2

#Parametros de inovação:
lambda_1 = 0.5
rho = 0.04
theta_max_1 = 0.75
theta_max_2 = 0.75
xi_1 = 0.08
xi_2 = 0.08
x_beta = [-0.05,0.25]
a_beta = 1
b_beta = 5

imitation_distance_penalty = 0.1

