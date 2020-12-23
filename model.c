#include <stdio.h>
#include <math.h>

typedef enum {false, true} bool;
#define NELEMS(x)  (sizeof(x) / sizeof((x)[0]))

int firm_update_counter = 0;
int no_turns = 1000;

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

int no_workers_s_m = 50;
int no_workers_s_p = 50;
int no_workers_n_m = 100;
int no_workers_n_p = 0;


struct World world;
const int firm_arr_size = 128;
const int workers_arr_size = 128;
float savings_rate = 0.2;
struct Worker
{
	float wage;
	float remainder;
	bool is_south;
	bool initialized;
};


struct Firm
{
	struct Worker workers[workers_arr_size];
	int no_workers;
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
	bool initialized;
};

struct World
{
	struct Firm firm_s_p[firm_arr_size];
	struct Firm firm_s_m[firm_arr_size];
	struct Firm firm_n_p[firm_arr_size];
	struct Firm firm_n_m[firm_arr_size];
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

struct Worker buildWorker(float wage, bool is_south, float remainder)
{
	struct Worker w;
	w.wage = wage;
	w.is_south = is_south;
	w.remainder = 0;
	w.initialized = true;

	return w;
}

struct Firm buildFirm(int no_workers, float ini_w, float capital, float productivity, bool is_south, bool is_primary){
	struct Firm f;

	for (int i = 0; i < no_workers; ++i)
	{
		f.workers[i] = buildWorker(ini_w, is_south, 0);
	}

	f.no_workers = no_workers;

	f.last_y = 2;
	f.capital = capital;
	f.last_capital = capital;
	f.productivity = productivity;

	float *p = get_demand_ptr(is_south, is_primary);
	for (int i = 0; i < demand_series_lenght; ++i)
	{
		f.demand[i] = p[i];
	}

	f.market_share = is_primary ? 0 : 1 / no_firm_s_m + no_firm_n_m;
	f.markup = init_markup;
	f.production = 5;
	f.price = 2;
	f.investment = 0;
	f.initialized = true;

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

float getMeanPrimarySouthPrice(){
	float mean = 0;
	for (int i = 0; i < firm_arr_size; ++i)
	{
		if (! world.firm_s_p[i].initialized){
			break;
		}
		mean += world.firm_s_p[i].price;
	}

	return mean;
}

float getExDemand(struct Firm * firm){
	float sum = 0;
	for (int i = 0; i < demand_series_lenght; ++i)
	{
		sum += firm->demand[i] * demand_series_weight[i];
	}
	return sum;
}

float getFirmInvestment(struct Firm * firm){
	if(firm->is_primary){
		return firm->last_y * savings_rate;
	}
	else{
		return (gamma_0 + gamma_1 * (getExDemand(firm) / firm->productivity * firm->capital));
	}
}

float getAllocatedCapital(struct Firm * firm){
	if(firm->productivity <= 0){
		return 0;
	}
	return getExDemand(firm) / firm->productivity;
}

int getAllocatedLabour(struct Firm * firm){
	return (int)getAllocatedCapital(firm) * firm->productivity;
}

void updateWorkers(struct Firm * firm, float mean_price, float totalProduction){
	float remainder = 0;
	for (int i = 0; i < workers_arr_size; i++)
	{
		if (! firm->workers[i].initialized)
		{
			break;
		}
		remainder += firm->workers[i].remainder;
	}
	int no_workers = getAllocatedLabour(firm);
	for (int i = 0; i < no_workers; ++i)
	{
		firm->workers[i] = buildWorker(mean_price, firm->is_south, remainder/no_workers);
	}

	//printf("No workers: %i\n is south: %i is_primary: %i",no_workers, firm->is_south, firm->is_primary );
	for (int i = no_workers; i < workers_arr_size; i++)
	{
		if(!firm->workers[i].initialized){
			break;
		}
		firm->workers[i].initialized = false;
	}
}

void updateFirm(struct Firm *firm , float mean_price, float totalProduction){
	firm->capital = getFirmInvestment(firm);
	updateWorkers(firm, mean_price, totalProduction);
	firm->production = getAllocatedCapital(firm) / firm->productivity;
	firm->price = 1;
	firm_update_counter++;

}

void tick(int turn){
	printf("Turn %i\n",turn );

	float totalProduction = 0;
	for (int i = 0; i < firm_arr_size; ++i)
	{
		if (!world.firm_s_m[i].initialized && !world.firm_n_m[i].initialized){
			break;
		}

		if (world.firm_s_m[i].initialized){
			totalProduction += world.firm_s_m[i].production;
		}
		if (world.firm_n_m[i].initialized){
			totalProduction += world.firm_n_m[i].production;
		}
	}

	float mean_price = 0;
	int count = 0;
	for (int i = 0; i < firm_arr_size; ++i)
	{
		if (!world.firm_s_p[i].initialized && !world.firm_n_p[i].initialized){
			break;
		}

		if (world.firm_s_p[i].initialized){
			mean_price += world.firm_s_m[i].price;
			count++;
		}
		if (world.firm_n_p[i].initialized){
			mean_price += world.firm_n_m[i].price;
			count++;
		}
	}
	mean_price /= count;

	for (int i = 0; i < firm_arr_size; ++i)
	{
		if((!world.firm_s_p[i].initialized && !world.firm_s_m[i].initialized && !world.firm_n_p[i].initialized && !world.firm_n_m[i].initialized)){
			break;
		}

		if (world.firm_s_p[i].initialized)
		{
			updateFirm(&world.firm_s_p[i], mean_price, totalProduction);
		}

		if (world.firm_s_m[i].initialized)
		{
			updateFirm(&world.firm_s_m[i], mean_price, totalProduction);
		}

		if (world.firm_n_p[i].initialized)
		{
			updateFirm(&world.firm_n_p[i], mean_price, totalProduction);
		}

		if (world.firm_n_m[i].initialized)
		{
			updateFirm(&world.firm_n_m[i], mean_price, totalProduction);
		}


	}
	//printf("Mean price: %f and totalProduction: %f\n", mean_price, totalProduction );
}

void run(){
	world = buildWorld();

	for(int i = 0; i < no_turns; i++){
		tick(i);
	}
	return;
}

int main(){
	run();
	printf("Firms updated: %i\n", firm_update_counter );
	return 0;
}