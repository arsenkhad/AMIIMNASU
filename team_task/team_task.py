import os
import sys
import graphviz as gv
import numpy as np
from collections.abc import Iterable

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PARENT_DIR = '/'.join(SCRIPT_DIR.split('/')[:-1])
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from weather import WeatherData
from dz1.markov_chain import MarkovChain, SolveMethod


def print_matrix(matrix):
    print('', *['\t'.join(str(round(item, 3)) for item in line) for line in matrix], '', sep='\n')

def get_intervals(in_data, min_val, max_val):
    intervals = np.linspace(np.floor(min_val), np.ceil(max_val), int(np.ceil(max_val) - np.floor(min_val)) + 1)
    data_sorted = sorted(in_data)
    len_avgs = len(data_sorted)
    interval_tuples = []
    
    interval_end = 0
    interval_sizes = []
    for i, int_end in enumerate(intervals[1:]):
        interval_start = interval_end
        while interval_end < len_avgs and data_sorted[interval_end] < int_end:
            interval_end += 1
        interval_sizes.append(len(data_sorted[interval_start:interval_end]))

    group_stop = max(interval_sizes)
    cur_block_size = 0
    cur_block_start = 0
    for i, ln in enumerate(interval_sizes):
        cur_block_size += ln
        if cur_block_size >= group_stop:
            if ln >= group_stop:
                if cur_block_size != ln:
                    interval_tuples.append((intervals[cur_block_start], intervals[i]))
                interval_tuples.append((intervals[i], intervals[i+1]))
            else:
                interval_tuples.append((intervals[cur_block_start], intervals[i+1]))
            cur_block_size = 0
            cur_block_start = i+1
    if cur_block_size:
        interval_tuples.append((intervals[cur_block_start], intervals[-1]))
    else:
        interval_tuples[-1] = (interval_tuples[-1][0], intervals[-1])
    return interval_tuples


def check_entries(data, intervals):
    iterable = isinstance(data, Iterable)
    if not iterable:
        data = [data]
    entries = []
    for item in data:
        entry = None
        for i, interval in enumerate(intervals):
            if interval[0] <= item < interval[1]:
                entry = i
                break
        if entry == None:
            if item == intervals[-1][1]:
                entry = len(intervals) - 1
            else:
                raise ValueError(f'{data} doesn`t belong to any of intervals')
        entries.append(entry)
    return entries if iterable else entries[0]


def v1(data : WeatherData, cur_weather, start_decade : int, end_decade : int):
    if start_decade < 1 or start_decade > 36 or end_decade < 1 or end_decade > 36:
        raise ValueError('Decade must be in 1..36')
    start_decade_data = data.get_decade_avgs(start_decade)
    end_decade_data = data.get_decade_avgs(end_decade)

    start_end_full_data = data.get_decade_all(start_decade) + data.get_decade_all(end_decade)

    min_temp = min(start_end_full_data, key=lambda x: x.temperature).temperature
    max_temp = max(start_end_full_data, key=lambda x: x.temperature).temperature
    print(min_temp, max_temp)

    intervals = get_intervals([*start_decade_data.values(), *end_decade_data.values()], min_temp, max_temp)
    state_amount = len(intervals)

    start_decade_states = check_entries(start_decade_data.values(), intervals)
    end_decade_states   = check_entries(end_decade_data.values(),   intervals)

    transitions = zip(start_decade_states, end_decade_states)
    trans_matrix = np.zeros((state_amount, state_amount))
    for trans in transitions:
        trans_matrix[trans[0]][trans[1]] += 1
    for i, line in enumerate(trans_matrix):
        if line.any():
            trans_matrix[i] /= sum(line)

    graph = gv.Digraph(graph_attr={'rankdir' : 'LR', 'ranksep' : '5'}, node_attr={'shape' : 'circle', 'width': '0.6'})
    names = ['start', 'end']
    for i in range(state_amount):
        for name in names:
            graph.node(name+str(i+1), label=f'<T<SUB>{i+1}</SUB>>', group=str(i+1))
        graph.edge(names[0]+str(i+1), names[1]+str(i+1), style='invis')


    for i, line in enumerate(trans_matrix):
        for j, trans in enumerate(line):
            if trans:
                graph.edge(names[0]+str(i+1), names[1]+str(j+1), label=str(round(trans, 2)))

    for name in names:
        subgraph = gv.Digraph(f'{name}', graph_attr={'rankdir' : 'TB', 'rank' : 'same', 'style' : 'invis'}, edge_attr={'style' : 'invis'})
        for i in range(state_amount-1):
            subgraph.edge(name+str(i+1), name+str(i+2), style='invis')
        graph.subgraph(subgraph)
    graph.render(filename=SCRIPT_DIR+'/1_markov-chain', engine='dot')
    
    print_matrix(trans_matrix)
    print(check_entries(cur_weather, intervals))
    print_matrix([trans_matrix[check_entries(cur_weather, intervals)]])

def v2(data : WeatherData, cur_weather, start_decade : int, end_decade : int):
    if start_decade < 1 or start_decade > 36 or end_decade < 1 or end_decade > 36:
        raise ValueError('Decade must be in 1..36')
    inspected_data = []
    for decade in range(start_decade, end_decade + 1):
        inspected_data.append({'decade' : decade, 'temperatures' : data.get_decade_all(decade), 'avgs' : data.get_decade_avgs(decade)})

    max_temp = -np.inf
    min_temp = np.inf

    for decade in inspected_data:
        temp_max = max(decade['temperatures'], key=lambda x: x.temperature).temperature
        temp_min = min(decade['temperatures'], key=lambda x: x.temperature).temperature
        if temp_max > max_temp:
            max_temp = temp_max
        if temp_min < min_temp:
            min_temp = temp_min
    print(min_temp, max_temp)

    intervals = get_intervals([temp for item in inspected_data for temp in item['avgs'].values()], min_temp, max_temp)
    state_amount = len(intervals)

    intervals_of_avg = []
    for year in data.years_set:
        intervals_of_avg.append(check_entries([decade['avgs'][year] for decade in inspected_data], intervals))

    trans_matrix = np.zeros((state_amount, state_amount))
    for trans_year in intervals_of_avg:
        for i in range(len(trans_year) - 1):
            trans_matrix[trans_year[i]][trans_year[i+1]] += 1
    for i, line in enumerate(trans_matrix):
        if line.any():
            trans_matrix[i] /= sum(line)
    
    graph = gv.Digraph(node_attr={'shape' : 'circle', 'width': '0.6'})
    for i, line in enumerate(trans_matrix):
        graph.node(str(i+1), label=f'<T<SUB>{i+1}</SUB>>')
        for j, trans in enumerate(line):
            if trans:
                graph.edge(str(i+1), str(j+1), label=str(round(trans, 2)))    
    graph.render(filename=SCRIPT_DIR+'/2_markov-chain', engine='dot')
    
    print_matrix(trans_matrix)
    print(check_entries(cur_weather, intervals))
    print_matrix([trans_matrix[check_entries(cur_weather, intervals)]])


def v3(data : WeatherData, cur_weather, start_decade : int, end_decade : int):
    if start_decade < 1 or start_decade > 36 or end_decade < 1 or end_decade > 36:
        raise ValueError('Decade must be in 1..36')
    inspected_data = []
    for decade in range(start_decade, end_decade + 1):
        inspected_data.append({'decade' : decade, 'temperatures' : data.get_decade_all(decade), 'avgs' : data.get_decade_avgs(decade)})

    max_temp = -np.inf
    min_temp = np.inf

    for decade in inspected_data:
        temp_max = max(decade['temperatures'], key=lambda x: x.temperature).temperature
        temp_min = min(decade['temperatures'], key=lambda x: x.temperature).temperature
        if temp_max > max_temp:
            max_temp = temp_max
        if temp_min < min_temp:
            min_temp = temp_min
    print(min_temp, max_temp)

    intervals = get_intervals([temp for item in inspected_data for temp in item['avgs'].values()], min_temp, max_temp)
    state_amount = len(intervals)

    intervals_of_avg = []
    for year in data.years_set:
        intervals_of_avg.append(check_entries([decade['avgs'][year] for decade in inspected_data], intervals))

    decade_amount = len(inspected_data)
    transitions = np.zeros((decade_amount, state_amount))
    transitions[0][check_entries(cur_weather, intervals)] = 1

    for i in range(1, decade_amount):
        trans_matrix = np.zeros((state_amount, state_amount))
        for j in range(len(intervals_of_avg)):
            trans_matrix[intervals_of_avg[j][i-1]][intervals_of_avg[j][i]] += 1
        for j, line in enumerate(trans_matrix):
            if line.any():
                trans_matrix[j] /= sum(line)
        transitions[i] = np.matmul(trans_matrix.T, transitions[i-1])

    print_matrix(transitions.T)
    print(check_entries(cur_weather, intervals))
    print_matrix([transitions[-1]])



def main():
    weather = WeatherData(SCRIPT_DIR+'/input_weather_data.csv')
    # print(weather['2013-02-01'])
    # for item in weather.range('2013-02-01', '2013-02-08T12:00:00.0'):
    #     print(item)
    # for item in weather.get_decade(2023, 4):
    #     print(item)
    # print('Avg:', weather.decade_avg(2023, 4))
    v1(weather, -4.247, 4, 13)
    v2(weather, -4.247, 4, 13)
    v3(weather, -4.247, 4, 13)
main()
