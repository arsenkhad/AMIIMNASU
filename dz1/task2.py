import numpy as np
import getopt
import sys
import os

SCRIPT_PARENT_DIR = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR))
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR + '/dz1/'))
from task2_tex import generate_task2_tex
from task1 import check_default
from class_chain import ClassifiedMarkovChain

class TaskDefaults():
    input_path = SCRIPT_PARENT_DIR+'/dz1/input_task1.txt'
    exp_num    = 50
    trans_num  = 100
    N_num      = 6
    m_num      = 2

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

    print('\t-N --N_graphics NUM\033[0m')
    print(f'\t\tset amount of graphics, produced per node from closed classes. By default {TaskDefaults.m_num}.')
    print()

def main(input_filename = 'dz1/input_task2.txt', tex_dest = 'dz1/task2_doc/', exp_per_node = 10, trans_per_experiment = 100, graph_N = 6, graph_closed = 2):
    A = ClassifiedMarkovChain(input_filename)
    print(A)
    img_dest = 'images/' if tex_dest else 'dz1_task2_images/'
    try:
        os.mkdir(img_dest)
    except FileExistsError:
        pass
    A.generate_dot(img_dest)

    freq_data = []

    open_amount = len(A.N_class_nums) * exp_per_node
    if graph_N > open_amount:
        graph_N = open_amount
    if graph_closed > exp_per_node:
        graph_closed = exp_per_node

    lines_to_plot = list(np.random.choice(open_amount, size=graph_N))
    for i in range(A.node_count - len(A.N_class_nums)):
        for j in range(graph_closed):
            lines_to_plot.append(open_amount + i * exp_per_node + j)

    for i in range(A.node_count):
        current_data = []
        for j in range(exp_per_node):
            result = A.run_experiment(trans_per_experiment, start_choice=i)
            rel_frequencies = [result.count(i) / (trans_per_experiment + 1) for i in range(A.node_count)]
            current_data.append(rel_frequencies)
            if (i * exp_per_node + j) in lines_to_plot:
                A.plot_transitions(result)
        freq_data.append(np.sum(current_data, axis=0) / exp_per_node)

    A.plot_transitions(dest=img_dest)
    print('\nЧастоты вхождений\n', ClassifiedMarkovChain.matrix_to_string(freq_data))

    if tex_dest:
        generate_task2_tex(tex_dest, img_dest, A, freq_data)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:d:e:t:N:m:", ["help", "input=", "tex_dest=", "node_experiments=", "transition_count=", "N_graphics=", "closed_graphics="])
    except getopt.GetoptError as err:
        print(err)
        print_usage()
        sys.exit(2)
    input_filename = ''
    tex_dest = ''
    exp_num = 0
    trans_num = 0
    N_num = 0
    m_num = 0
    for c, optarg in opts:
        if c in ('-h', '--help'):
            print_usage()
            exit()
        elif c in ('-i', '--input'):
            input_filename = optarg
        elif c in ('-d', '--tex_dest'):
            tex_dest = optarg
        elif c in ('-e', '--node_experiments'):
            exp_num = int(optarg)
        elif c in ('-t', '--transition_count'):
            trans_num = int(optarg)
        elif c in ('-N', '--N_graphics'):
            N_num = int(optarg)
        elif c in ('-m', '--closed_graphics'):
            m_num = int(optarg)
    
    input_filename = check_default(input_filename, TaskDefaults.input_path, 'Path to input file')
    exp_num   = check_default(exp_num,    10, 'Amount of experiments per node')
    trans_num = check_default(trans_num, 100, 'Amount of transitions per experiment')
    N_num     = check_default(N_num,       6, 'Amount of graphics from open class N')
    m_num     = check_default(m_num,       2, 'Amount of graphics per node from closed classes')

    if tex_dest and tex_dest[-1] != '/':
        tex_dest += '/'

    if not tex_dest:
        print('Report destination not specified. Only terminal and image output will be provided.')

    main(input_filename, tex_dest, exp_num, trans_num, N_num, m_num)