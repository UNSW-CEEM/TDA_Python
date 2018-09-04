import collections
from datetime import timedelta

dayOfYear = collections.namedtuple('dayOfYear', 'month day')
dayOfWeek = collections.namedtuple('dayOfWeek', 'day',)
timeOfDay = collections.namedtuple('timeOfDay', 'hour minute')


class Charge():
    def __init__(self, periodicity=timedelta(days=365), granularity='as_is',
                 start_year=dayOfYear(month=1, day=1), end_year=dayOfYear(month=12, day=31),
                 start_week=dayOfWeek(day=0), end_week=dayOfWeek(day=6),
                 start_day=timeOfDay(hour=0, minute=0), end_day=timeOfDay(hour=23, minute=59)):

        self.periodicity = periodicity
        self.granularity = granularity
        self.start_year = start_year
        self.end_year = end_year
        self.start_week = start_week
        self.end_week = end_week
        self.start_day = start_day
        self.end_day = end_day

    def filter_on_time(self, load):
        # Correct time of year
        filtered_load = load[((((load['TimeStamp'].dt.month == self.start_year.month) &
                              (load['TimeStamp'].dt.day >= self.start_year.day)) |
                             (load['TimeStamp'].dt.month > self.start_year.month)) &
                              (((load['TimeStamp'].dt.month == self.end_year.month) &
                                (load['TimeStamp'].dt.day <= self.end_year.day)) |
                               (load['TimeStamp'].dt.month < self.end_year.month)))]

        # Correct time of week
        filtered_load = filtered_load[(filtered_load['TimeStamp'].dt.dayofweek >= self.start_week.day) &
                                      (filtered_load['TimeStamp'].dt.dayofweek <= self.end_week.day)]

        # Correct time of day
        filtered_load = filtered_load[((((filtered_load['TimeStamp'].dt.hour == self.start_day.hour) &
                              (filtered_load['TimeStamp'].dt.minute >= self.start_day.minute)) |
                             (filtered_load['TimeStamp'].dt.hour > self.start_day.hour)) &
                              (((filtered_load['TimeStamp'].dt.hour == self.end_day.hour) &
                                (filtered_load['TimeStamp'].dt.minute <= self.end_day.minute)) |
                               (filtered_load['TimeStamp'].dt.hour < self.end_day.hour)))]

        return filtered_load


    def periodization(self, load):
        start_period = load['TimeStamp'].astype(object).min()
        end_period = load['TimeStamp'].min() + self.periodicity
        reached_end = False
        while not reached_end:
            period_load = load[(load['TimeStamp']>= start_period) & (load['TimeStamp']<= end_period)]
            start_period += self.periodicity
            end_period += self.periodicity
            reached_end = end_period > load['TimeStamp'].max()
            yield  period_load


    def resample(self, load):
        return load


class BlockCharge(Charge):
    def __init__(self, rate, lower=0, upper=float('inf'), **kwargs):
        super(BlockCharge, self).__init__(**kwargs)
        self.rate = rate
        self.lower = lower
        self.upper = upper

    def bill(self, load):
        load = self.filter_on_time(load)
        load = self.resample(load)
        cost = 0
        for period_load in self.periodization(load):
            bulk_energy = period_load['Energy'].sum()
            if bulk_energy <= self.lower:
                peroid_cost = 0
            elif bulk_energy >= self.upper:
                peroid_cost = (self.upper - self.lower) * self.rate
            else:
                peroid_cost = (bulk_energy - self.lower) * self.rate

            cost += peroid_cost

        return cost


class Tariff():
    def __init__(self, charge_types_and_paramaters):
        self.charges = []
        for charge in charge_types_and_paramaters:
            self.charges.append(charge[0](*charge[1:]))

    def bill(self, load):
        cost = 0
        for charge in self.charges:
            cost += charge.bill(load)

        return cost

