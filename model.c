#include <stdio.h>
typedef enum {false, true} bool;
#define NELEMS(x)  (sizeof(x) / sizeof((x)[0]))

int no_turns = 4;

float wage_s = 16.0;
float wage_n = 16.0;

float real_wage = 8;
float init_primary_price = 1;
float init_manufacture_price = 1;

float init_markup = 1;

int no_firm_s_m = 2;
int no_firm_s_p = 2;
int no_firm_n_m = 4;
int no_firm_n_p = 0;

float market_share_sensibility = 0.1;
float gamma_0 = 0.2;
float gamma_1 = 0.1;

float capital_s_m = 16.0;
float capital_s_p = 17.0;
float capital_n_m = 16.0;
float capital_n_p = 0.0;

float demand_s_m = 5;
float demand_s_p = 5;
float demand_n_m = 5;
float demand_n_p = 0;

const float demand_series_weight[] = {0.6, 0.5, 0.4};
const int demand_series_lenght = 3;

float productivity_s_m = 1.0;
float productivity_s_p = 1.0;
float productivity_n_m = 1.0;
float productivity_n_p = 1.0;

int no_workers_s_m = 16;
int no_workers_s_p = 16;
int no_workers_n_m = 16;
int no_workers_n_p = 0;

float savings_rate = 0.2;
struct Worker
{
	float wage;
	float remainder;
	bool is_south;
};

struct Firm
{
	struct Worker workers[128];
	float last_y;
	float capital;
	float last_capital;
	float productivity;
	float demand[demand_series_lenght];
	float market_share;
	float last_market_share;
	float markup;
	float production;
	float price;
	float investment;
	bool is_south;
	bool is_primary;
};

struct World
{
	struct Firm firm_s_p[128];
	struct Firm firm_s_m[128];
	struct Firm firm_n_p[128];
	struct Firm firm_n_m[128];
};

float * get_demand_ptr(bool is_south, bool is_primary){
	float d = 0;
	static float demandArray[demand_series_lenght];
	if(is_south){
		if(is_primary){
			d = demand_s_p;
		}
		else{
			d = demand_s_m;
		}
	}
	else{
		if(is_primary){
			d = demand_n_p;
		}
		else{
			d = demand_n_m;
		}
	}
	for (int i = 0; i < demand_series_lenght; ++i)
	{
		demandArray[i] = d;
	}
	return demandArray;

}

struct Firm buildFirm(int no_workers, float ini_w, float capital, float productivity, bool is_south, bool is_primary){
	struct Firm f;

	for (int i = 0; i < no_workers; ++i)
	{
		struct Worker w;
		w.wage = ini_w;
		w.is_south = is_south;
		w.remainder = 0;

		f.workers[i] = w;
	}

	f.last_y = 2;
	f.capital = capital;
	f.last_capital = capital;
	f.productivity = productivity;

	float *p = get_demand_ptr(is_south, is_primary);
	for (int i = 0; i < demand_series_lenght; ++i)
	{
		f.demand[i] = p[i];
		printf("%f\n", f.demand[i] );
	}

	f.market_share = is_primary ? 0 : 1 / no_firm_s_m + no_firm_n_m;
	f.markup = init_markup;
	f.production = 5;
	f.price = 2;
	f.investment = 0;

	return f;
}

struct World buildWorld(){
	struct World world;
	for (int i = 0; i < no_firm_s_p; ++i)
	{
		world.firm_s_p[i] = buildFirm(no_workers_s_p, wage_s, capital_s_p, productivity_s_p, true, true);
		
	}

	for (int i = 0; i < no_firm_s_m; ++i)
	{
		world.firm_s_m[i] = buildFirm(no_workers_s_m, wage_s, capital_s_m, productivity_s_m, true, true);
		
	}

	for (int i = 0; i < no_firm_n_p; ++i)
	{
		world.firm_s_p[i] = buildFirm(no_workers_n_p, wage_n, capital_n_p, productivity_n_p, true, true);
		
	}

	for (int i = 0; i < no_firm_n_m; ++i)
	{
		world.firm_n_m[i] = buildFirm(no_workers_n_m, wage_n, capital_n_m, productivity_n_m, true, true);
		
	}
	return world;
}
void tick(int turn){
	printf("Turn %i\n",turn );
}

void run(){
	struct World world = buildWorld();

	for(int i = 0; i < no_turns; i++){
		tick(i);
	}
	return;
}

int main(){
	run();
	return 0;
}