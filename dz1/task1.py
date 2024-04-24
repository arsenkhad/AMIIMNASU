import numpy as np
import getopt
import sys
import os

SCRIPT_PARENT_DIR = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR))
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR + '/dz1/'))

from task1_tex import generate_task1_tex
from markov_chain import MarkovChain

class TaskDefaults():
    input_path = SCRIPT_PARENT_DIR+'/dz1/input_task1.txt'
    exp_num    = 50
    trans_num  = 100
    pic_num    = 3

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
    print('\t-e --experiment_count NUM\033[0m')
    print(f'\t\tset amount of experiments. By default {TaskDefaults.exp_num}.')
    print('\033[1m')
    print('\t-t --transition_count NUM\033[0m')
    print(f'\t\tset amount of transitions per experiment. By default {TaskDefaults.trans_num}.')
    print('\033[1m')
    print('\t-g --graphics_count NUM\033[0m')
    print(f'\t\tset amount of produced graphics. By default {TaskDefaults.pic_num}.')
    print()

def check_default(var, default_val, var_name):
    if not var:
        var = default_val
        print(f'{var_name} not specified. Defaults to {default_val}')
    return var

# uncorrected and corrected standard deviation
def get_deviation(data):
    avg = np.mean(data)
    summ = sum([(item - avg) ** 2 for item in data])
    return avg, np.sqrt(summ / len(data)), np.sqrt(summ / (len(data) - 1))

def main(input = 'dz1/input_task1.txt', tex_dest = 'dz1/task1_doc/', pic_num = 3, experiment_count = 50, trans_per_experiment = 100):
    A = MarkovChain(input)
    img_dest = 'images/' if tex_dest else 'dz1_task1_images/'
    try:
        os.mkdir(img_dest)
    except FileExistsError:
        pass
    A.generate_dot(img_dest)
    imitation_data = []
    for i in range(experiment_count):
        result = A.run_experiment(trans_per_experiment, plot = True if i < pic_num else False, plot_dest=img_dest, exp_number=i + 1)
        rel_frequencies = [result.count(i) / (trans_per_experiment + 1) for i in range(A.node_count)]
        imitation_data.append(rel_frequencies)

    deviations = list(zip(*[get_deviation(dataset) for dataset in zip(*imitation_data)]))

    print(A)
    print('Среднеквадратичные отклонения')
    print('\nСредняя оценка:')
    print(*map(lambda x : round(x, 3), deviations[0]), sep='\t')
    print('\nИсправленная оценка:')
    print(*map(lambda x : round(x, 3), deviations[1]), sep='\t')
    if tex_dest:
        generate_task1_tex(tex_dest, img_dest, A, imitation_data, deviations, 3)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:d:g:e:t:", ["help", "input=", "tex_dest=", "graphics_count=", "experiment_count=", "transition_count="])
    except getopt.GetoptError as err:
        print(err)
        print_usage()
        sys.exit(2)
    input_filename = ''
    tex_dest = ''
    pic_num = 0
    exp_num = 0
    trans_num = 0
    for c, optarg in opts:
        if c in ('-h', '--help'):
            print_usage()
            exit()
        elif c in ('-i', '--input'):
            input_filename = optarg
        elif c in ('-d', '--tex_dest'):
            tex_dest = optarg
        elif c in ('-g', '--graphics_count'):
            pic_num = int(optarg)
        elif c in ('-e', '--experiment_count'):
            exp_num = int(optarg)
        elif c in ('-t', '--transition_count'):
            trans_num = int(optarg)
    
    input_filename = check_default(input_filename, TaskDefaults.input_path, 'Path to input file')
    exp_num        = check_default(exp_num,        TaskDefaults.exp_num,    'Amount of experiments')
    trans_num      = check_default(trans_num,      TaskDefaults.trans_num,  'Amount of transitions per experiment')
    pic_num        = check_default(pic_num,        TaskDefaults.pic_num,    'Amount of graphics')

    if tex_dest and tex_dest[-1] != '/':
        tex_dest += '/'

    if not tex_dest:
        print('Report destination not specified. Only terminal and image output will be provided.')

    main(input_filename, tex_dest, pic_num, exp_num, trans_num)
