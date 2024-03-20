import numpy as np
import graphviz as gv
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

class MarkovChain:
    def __init__(self, input_file : str) -> None:
        try:
            file = open(input_file, 'r')
            input = file.read()
            file.close()
        except:
            print("Input file not found. Aborted.")
            exit(1)
        
        self._var = input.split('\n')[0].strip()
        matrix_start = 1
        if len(self._var.split()) > 1:
            print('cum')
            self._var = ''
            matrix_start = 0
        self._trans_matrix = np.array([[float(item) for item in line.split()] for line in input.split('\n')[matrix_start:] if line])
        self._node_amount = len(self._trans_matrix)

        A = self._trans_matrix.transpose() - np.diag([1 for _ in self._trans_matrix])
        A[-1] = [1] * self._node_amount
        B = [0] * (self._node_amount)
        B[-1] = 1
        self._P = np.linalg.solve(A, B)
        self._edge_matrix = np.array([[probability for probability in self._P]] * self._node_amount)

    def __str__(self) -> str:
        return (
            f'\nМатрица переходов:\n{MarkovChain.__matrix_to_string(self._trans_matrix)}\n'
            f'\nПредельные вероятности:\n{MarkovChain.__matrix_to_string([self._P])}\n'
            f'\nПредельная матрица переходов:\n{MarkovChain.__matrix_to_string(self._edge_matrix)}\n'
        )
    
    @staticmethod
    def __matrix_to_string(matrix):
        return '\n'.join('\t'.join(str(round(item, 3)) for item in line) for line in matrix)

    @property
    def transition_matrix(self):
        return self._trans_matrix
    
    @property
    def edge_matrix(self):
        return self._edge_matrix
    
    @property
    def edge_possibilities(self):
        return self._P
    
    @property
    def variant(self):
        return self._var
    
    @property
    def node_count(self):
        return self._node_amount
    
    def __random_transition(self, line : int) -> int:
        return np.random.choice(self._node_amount, p=self._trans_matrix[line])

    def run_experiment(self, num_transitions : int = 100, plot = False, plot_dest = '', exp_number = -1) -> list:
        cur_choice = np.random.choice(self._node_amount)
        experiment = [cur_choice]
        for _ in range(num_transitions):
            cur_choice = self.__random_transition(cur_choice)
            experiment.append(cur_choice)
        
        if plot:
            self.plot_transitions(experiment, plot_dest, exp_number)
        return experiment


    def generate_dot(self, dest):
        graph = gv.Digraph()
        for i, line in enumerate(self._trans_matrix):
            for j, trans in enumerate(line):
                graph.edge(str(i+1), str(j+1), label=str(trans))
        graph.render(filename=dest+'markov-chain', engine='sfdp')

    @staticmethod
    def plot_transitions(data, dest='', exp_number=-1):
        data = [point+1 for point in data]
        data_max = max(data)
        point_count = len(data)
        scale = 50
        x = np.linspace(0, point_count-1, (point_count - 1) * scale + 1)
        y = [[data[0]]]
        for point in data[1:]:
            line = np.linspace(y[-1][-1], point, scale + 1)
            y.append(line[1:])
        y = [item for line in y for item in line]

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        fig, ax = plt.subplots(figsize=(18, 4))
        norm = plt.Normalize(min(y), max(y))
        lc = LineCollection(segments, cmap='viridis', norm=norm)
        lc.set_array(y)
        lc.set_linewidth(2)
        line = ax.add_collection(lc)
        # fig.colorbar(line, ax=ax)
        ax.set_xlim(0, point_count)
        ax.set_ylim(0.9, data_max + 0.1)
        plt.scatter(np.linspace(0, point_count-1, point_count), data, c=[item - 0.2 for item in data], vmin=1, vmax=data_max, cmap='viridis')


        plt.xlabel('Переходы')
        plt.ylabel('Состояния')
        plt.yticks(range(1, data_max+1))

        if exp_number != -1:
            plt.title(f'Эксперимент {exp_number}')

        if exp_number == -1 or not dest:
            plt.show()
        else:
            plt.savefig(dest+f'exp{exp_number}.png', bbox_inches='tight')
