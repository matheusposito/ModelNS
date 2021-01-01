class Worker:
    def __init__(self, wage, is_south=True, remainder=0.0):
        self.wage = wage
        self.worker_primary_spend_rate = 1 if is_south else .5
        self.remainder = remainder
        self.expense_p = remainder * self.worker_primary_spend_rate
        self.expense_m = remainder * (1 - self.worker_primary_spend_rate)
        self.is_south = is_south
