import getopt
import sys
import os

SCRIPT_PARENT_DIR = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR))
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR + '/dz2/'))
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR + '/dz1/'))

from dz1.task1 import check_default, get_deviation
from dz2.task1_tex import generate_task1_tex
from states import States


class TaskDefaults():
    input_path = SCRIPT_PARENT_DIR+'/dz2/input_task1.txt'
    exp_num    = 100
    graph_num  = 10


def print_usage():
    print('\nUsage:')
    print('\t\tpython3 task1.py [OPTIONS] \033[0m')
    print()
    print('Options:\033[1m')
    print('\t-h, --help\033[0m')
    print('\t\tdisplay help.')
    print('\033[1m')
    print('\t-i --input INPUT_FILE\033[0m')
    print(f'\t\tset path to input file. By default {TaskDefaults.input_path}.')
    print('\033[1m')
    print('\t-d --tex_dest DEST\033[0m')
    print('\t\tset path for rendering latex report.')
    print('If empty, latex code will NOT be produced. By default empty.')
    print('\033[1m')
    print('\t-e --node_experiments NUM\033[0m')
    print(f'\t\tset amount of experiments per node. By default {TaskDefaults.exp_num}.')
    print('\033[1m')
    print('\t-t --transition_count NUM\033[0m')
    print(f'\t\tset amount of transitions per experiment. By default {TaskDefaults.trans_num}.')
    print('\033[1m')
    print('\t-N --N_graphics NUM\033[0m')
    print(f'\t\tset amount of graphics, produced from open class N. By default {TaskDefaults.N_num}.')
    print('\033[1m')
    print('\t-c --closed_graphics NUM\033[0m')
    print(f'\t\tset amount of graphics, produced per node from closed classes. By default {TaskDefaults.m_num}.')
    print()


def parse_input(input_file) -> dict:
    input = None
    with open(input_file, 'r') as file:
        input = file.read().split('\n')
    
    if not input:
        raise FileNotFoundError(f"Could not read file with given path:\n{input_file}")
    
    vars = {}
    print('\nParsed arguments:')
    for line in input:
        if line:
            if '=' in line:
                line = ''.join(line.split())
                key, value = line.split('=')
            else:
                key, value = line.strip().split()
            print(f'{key}={value}')
            vars[key] = int(value)
    return vars


def main(input_filename = 'dz2/input_task1.txt', tex_dest = 'dz2/task1_doc/', experiment_count = 100, graph_count = 10):
    vars = parse_input(input_filename)
    N = vars.pop('N', None)
    G = vars.pop('G', None)
    if N and G:
        vars['N_a'] = 2 + G % 2
        vars['N_b'] = 1 + N % 2
        vars['R_a'] = 1 + G % 2
        vars['R_b'] = 2 - G % 2
        vars['intensity_a'] = G + N % 3
        vars['intensity_b'] = G + N % 5
    for key in ['intensity_a', 'intensity_b', 'N_a', 'N_b', 'R_a', 'R_b']:
        if not vars.get(key, None):
            raise KeyError('Input does not include some of neccesary variables')

    S = States(vars['N_a'], vars['N_b'], vars['R_a'], vars['R_b'], vars['intensity_a'], vars['intensity_b'])
    img_dest = 'images/' if tex_dest else 'dz2_task1_images/'
    try:
        os.mkdir(img_dest)
    except FileExistsError:
        pass
    print(S)
    S.generate_dot(img_dest)
    S.plot_solve(img_dest)
    S.plot_reliability(img_dest)
    break_times = S.imitation(experiment_count, graph_count, img_dest)
    deviations = get_deviation(break_times)
    print('Среднее выборочное значение:   ', deviations[0])
    print('Стандартное отклонение времени:', deviations[2])

    if tex_dest:
        generate_task1_tex(tex_dest, img_dest, S, deviations)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:d:e:g:", ["help", "input=", "tex_dest=", "experiments_num=", "graphics_num="])
    except getopt.GetoptError as err:
        print(err)
        print_usage()
        sys.exit(2)
    input_filename = ''
    tex_dest = ''
    exp_num = 0
    graph_num = 0
    for c, optarg in opts:
        if c in ('-h', '--help'):
            print_usage()
            exit()
        elif c in ('-i', '--input'):
            input_filename = optarg
        elif c in ('-d', '--tex_dest'):
            tex_dest = optarg
        elif c in ('-e', '--experiments_num'):
            exp_num = int(optarg)
        elif c in ('-g', '--graphics_num'):
            graph_num = int(optarg)
    
    input_filename = check_default(input_filename, TaskDefaults.input_path, 'Path to input file')
    exp_num        = check_default(exp_num,        TaskDefaults.exp_num,    'Amount of experiments')
    graph_num      = check_default(graph_num,      TaskDefaults.graph_num,  'Amount of graphics')

    if tex_dest and tex_dest[-1] != '/':
        tex_dest += '/'

    if not tex_dest:
        print('Report destination not specified. Only terminal and image output will be provided.')

    main(input_filename, tex_dest, exp_num, graph_num)
