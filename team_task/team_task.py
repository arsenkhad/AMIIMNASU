import os
import sys
import datetime
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PARENT_DIR = '/'.join(SCRIPT_DIR.split('/')[:-1])
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from weather import WeatherData, WeatherRecord
from dz1.markov_chain import MarkovChain

class StateChecker:
    def __init__(self, start, end) -> None:
        self.__start = start
        self.__end = end

    def __call__(self, temperature):
        if self.__start <= temperature < self.__end:
            return True
        return False
    
    @property
    def edges(self):
        return (self.__start, self.__end)

class States:
    def __init__(self, min_temp, max_temp, state_amount=12) -> None:
        state_breakpoints = np.linspace(min_temp, max_temp, state_amount + 1)
        self.__states : list[StateChecker] = []
        for i in range(state_amount):
            self.__states.append(StateChecker(state_breakpoints[i], state_breakpoints[i+1]))

    def check_entry(self, temperature):
        for i, state in enumerate(self.__states):
                if state(temperature):
                    return i

    def check_entries(self, temperatures):
        return [self.check_entry(temp) for temp in temperatures]
    
    def get_state(self, index):
        if index < 0 or index >= len(self.__states):
            return None
        return self.__states[index].edges



def v1(data : WeatherData, cur_weather, start_decade : int, end_decade : int, state_amount = 12):
    if start_decade < 1 or start_decade > 36 or end_decade < 1 or end_decade > 36:
        raise ValueError('Decade must be in 1..36')
    start_decade_data = data.get_decade_avgs(start_decade)
    end_decade_data = data.get_decade_avgs(end_decade)

    start_end_full_data = data.get_decade_all(start_decade) + data.get_decade_all(end_decade)
    states = States(min(start_end_full_data, key=lambda x: x.temperature).temperature, max(start_end_full_data, key=lambda x: x.temperature).temperature, state_amount)

    start_decade_states = states.check_entries(start_decade_data)
    end_decade_states = states.check_entries(end_decade_data)

    transitions = zip(start_decade_states, end_decade_states)
    trans_matrix = np.zeros((state_amount, state_amount))
    for trans in transitions:
        trans_matrix[trans[0]][trans[1]] += 1
    for i in range(state_amount):
        amount = start_decade_states.count(i)
        if amount:
            trans_matrix[i] /= amount

    print(*trans_matrix, '', sep='\n')

    print(trans_matrix[states.check_entry(cur_weather)])


def main():
    weather = WeatherData(SCRIPT_DIR+'/input_weather_data.csv')
    # print(weather['2013-02-01'])
    # for item in weather.range('2013-02-01', '2013-02-08T12:00:00.0'):
    #     print(item)
    # for item in weather.get_decade(2023, 4):
    #     print(item)
    # print('Avg:', weather.decade_avg(2023, 4))
    v1(weather, -4.247, 4, 13)
main()
