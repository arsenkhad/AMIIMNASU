from __future__ import annotations
import datetime
import csv
from multipledispatch import dispatch

def date_from_iso(iso_string : str):
    return datetime.datetime.fromisoformat(iso_string).date()

def get_date_decade(date : datetime.datetime):
    return (date.month - 1) * 3 + 1 + ((date.day - 1) // 10 if date.day < 30 else 2)

class WeatherRecord:
    @dispatch(list)
    def __init__(self, data_list : list) -> None:
        if len(data_list) != 2:
            raise ValueError('Data must consist of 2 values: time and temperature')
        self._date : datetime.date = date_from_iso(data_list[0])
        self._decade = get_date_decade(self._date)
        self._temp : float = float(data_list[1])

    @dispatch((datetime.datetime, datetime.date, str), float)
    def __init__(self, date, temperature) -> None:
        if type(date) == str:
            date = date_from_iso(date)
        elif type(date) == datetime.datetime:
            date = date.date()
        self._date : datetime.date = date
        self._decade = get_date_decade(date)
        self._temp : float = temperature

    def __str__(self) -> str:
        return f'date: {self._date}, temperature: {self._temp}, decade: {self._decade}'

    # All arithmetics affect and return temperatures only.
    @dispatch(object)
    def __add__(self, other : WeatherRecord):
        return self.temperature + other.temperature
    
    @dispatch((int, float))
    def __add__(self, other : int | float):
        return self.temperature + other

    @dispatch(object)
    def __radd__(self, other : WeatherRecord):
        return other.temperature + self.temperature

    @dispatch((int, float))
    def __radd__(self, other : int | float):
        return other + self.temperature

    @property
    def date(self):
        return self._date

    @property
    def temperature(self):
        return self._temp
    
    @property
    def decade(self):
        return self._decade

class WeatherIterator:
    def __init__(self, data : list[WeatherRecord], start_iter = None, end_iter = None) -> None:
        if not start_iter and end_iter:
            self.__data = data
        else:
            if not start_iter:
                start_iter = min(data, key= lambda x: x.date).date
            if not end_iter:
                end_iter = max(data, key= lambda x: x.date).date

            i = 0
            end = len(data)
            while i < end and data[i].date < start_iter:
                i += 1
            self.__data = []

            for item in data[i:]:
                if item.date >= end_iter:
                    break
                self.__data.append(item)

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        for item in self.__data:
            yield item

class WeatherData:
    def __init__(self, filename) -> None:

        self.__records : list[WeatherRecord] = []
        with open(filename, 'r') as csv_file:
            weather_reader = csv.reader(csv_file)
            next(weather_reader)
            for row in weather_reader:
                self.__records.append(WeatherRecord(row))

        self.__records.sort(key = lambda x : x.date)

        self._years = []
        for record in self.__records:
            year = record.date.year
            if year not in self._years:
                self._years.append(year)
        

    def __getitem__(self, date):
        if type(date) == str:
            date = date_from_iso(date)
        for record in self.__records:
            if record.date == date:
                return record
        return None
    
    def __iter__(self):
        return WeatherIterator(self.__records)

    def range(self, start_iter, end_iter):
        if type(start_iter) == str:
            start_iter = date_from_iso(start_iter)
        if type(end_iter) == str:
            end_iter = date_from_iso(end_iter)
        return WeatherIterator(self.__records, start_iter, end_iter)

    @property
    def years_set(self):
        return self._years

    def get_decade(self, year, decade_num):
        month = (decade_num - 1) // 3 + 1
        day = (decade_num - 1) % 3 * 10 + 1
        start_date = datetime.date(year, month, day)

        if day > 20:
            month += 1
            day = 1
        else:
            day += 10
        if month == 13:
            month = 1
            year += 1
        end_date = datetime.date(year, month, day)
        
        return self.range(start_date, end_date)

    def decade_avg(self, year, decade_num):
        dec = self.get_decade(year, decade_num)
        if not dec:
            return None
        return sum(dec) / len(dec)

    def get_decade_all(self, decade):
        return [item for item in self.__records if item.decade == decade]

    def get_decade_avgs(self, decade):
        avgs = {}
        for year in self.years_set:
            avg = self.decade_avg(year, decade)
            if avg != None:
                avgs[year] = avg
        if not avgs:
            print(f'Warning! No records of decade {decade} in given data.')
        return avgs
