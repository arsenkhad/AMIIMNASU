import numpy as np
import graphviz as gv
import matplotlib.pyplot as plt
from markov_chain import MarkovChain

class ClassifiedMarkovChain(MarkovChain):
    def __init__(self, input: str) -> None:
        super().__init__(input)

        components = self.get_components()
        self._N_class_num = components[0]
        self._closed_classes_num = components[1:]
        self._closed_classes = [MarkovChain(self.get_submatrix(self._trans_matrix, comp_set)) for comp_set in self._closed_classes_num]

        self._bridges = [0] * (len(self._closed_classes_num))
        for i, line in enumerate(self._trans_matrix):
            for j, item in enumerate(line):
                if item:
                    for k, comp in enumerate(components):
                        if j in comp and i not in comp:
                            self._bridges[k-1] = (self._trans_matrix[i][j], i, j)

        N = self.get_submatrix(self._trans_matrix, self._N_class_num)
        N_len = len(N)
        N = np.pad(N, (0, len(self._closed_classes_num)))
        for i in range(len(self._closed_classes_num)):
            N[self._N_class_num.index(self._bridges[i][1])][N_len + i] = self._bridges[i][0]
            N[N_len + i][N_len + i] = 1

        self._N_class = MarkovChain(N, mult=True)

        offset = N_len
        self._edge_matrix.fill(0)
        for k, m_class in enumerate(self._closed_classes):
            ln = m_class.node_count
            trans_line = components[k+1].index(self._bridges[k][2])
            class_trans = np.matmul([[line[N_len+k]] for line in self._N_class.edge_matrix[:N_len]], [m_class.edge_matrix[trans_line]])
            for i in range(N_len):
                for j in range(ln):
                    self._edge_matrix[         i][offset + j] = class_trans[i][j]
            for i in range(ln):
                for j in range(ln):
                    self._edge_matrix[offset + i][offset + j] = m_class.edge_matrix[i][j]
            offset += ln

        self._P = list(map(np.average, zip(*self._edge_matrix[:N_len])))

        swap = []
        for comp in components:
            for index in comp:
                line = [0] * self.node_count
                line[index] = 1
                swap.append(line)
        self._order_trans_matrix = np.matmul(np.matmul(swap, self._trans_matrix), np.transpose(swap))


    def __str__(self) -> str:
        return (
            f'{self.N_class}'
            f'{"".join([str(m_c) for m_c in self.closed_classes])}'
            f'\nМатрица переходов:\n{MarkovChain.matrix_to_string(self._trans_matrix)}\n'
            f'\nПредельные вероятности при начале в несущественном классе:\n{MarkovChain.matrix_to_string([self._P])}\n'
            f'\nПредельная матрица переходов:\n{MarkovChain.matrix_to_string(self._edge_matrix)}\n'
        )


    @staticmethod
    def get_submatrix(matrix, indexes):
        return [[item for j, item in enumerate(line) if j in indexes] for i, line in enumerate(matrix) if i in indexes]

    @property
    def closed_classes_nums(self):
        return self._closed_classes_num

    @property
    def closed_classes(self):
        return self._closed_classes

    @property
    def N_class_nums(self):
        return self._N_class_num

    @property
    def N_class(self):
        return self._N_class

    @property
    def class_bridges(self):
        return self._bridges

    @property
    def ordered_transition_matrix(self):
        return self._order_trans_matrix

    def generate_dot(self, dest):
        graph = gv.Digraph(graph_attr={'rankdir' : 'TB'})
        components = self.get_components()
        for k, component in enumerate(components):
            subgraph = gv.Digraph(f'cluster_{k}', engine='fdp', node_attr={'rank' : 'min' if k else 'max'})
            for i in component:
                for j, trans in enumerate(self.transition_matrix[i]):
                    if j in component:
                        subgraph.edge(str(i+1), str(j+1), label=str(trans))
                    elif trans:
                        graph.edge(str(i+1), str(j+1), label=str(trans))
            graph.subgraph(subgraph)

        if dest:
            graph.render(filename=dest+'markov-chain', engine='circo')
        return graph
    
    def __random_transition(self, line : int) -> int:
        return np.random.choice(self._node_amount, p=self._order_trans_matrix[line])

    def run_experiment(self, num_transitions: int = 100, start_choice=None, plot=False, plot_dest='', exp_number=-1, rand_func=__random_transition) -> list:
        return super().run_experiment(num_transitions, start_choice, plot, plot_dest, exp_number, rand_func)

    def get_components(self):
        def dfs1(vert):
            used.append(vert)
            for i, item in enumerate(self.transition_matrix[vert]):
                if item and i not in used:
                    dfs1(i)
            order.append(vert)

        def dfs2(vert):
            used.append(vert)
            component.append(vert)

            for i, item in enumerate(self.transition_matrix[:, vert]):
                if item and i not in used:
                    dfs2(i)

        used = []
        order = []
        for i in range(self.node_count):
            if i not in used:
                dfs1(i)

        component = []
        components = []
        used.clear()
        for vert in reversed(order):
            if vert not in used:
                dfs2(vert)
                components.append(component.copy())
                component.clear()
        return components
    
    @staticmethod
    def plot_transitions(data = [], dest='', fig = None, show = False):
        plt.rcParams.update({'font.size': 18})
        if data:
            data = [point+1 for point in data]
            data_max = max(data)
            if not fig:
                fig = plt.figure(0, figsize=(20, 8))
                plt.xlim(-0.3, len(data) - 0.7)
                plt.ylim(0.5, data_max + 0.5)
                plt.yticks(range(1, data_max+1))

            plt.plot(data, '-o', linewidth=1.5, markersize=3)

        if show or dest:
            plt.xlabel('Переходы')
            plt.ylabel('Состояния')
            plt.grid()

        if show:
            plt.show()
        if dest:
            plt.savefig(dest+'exp1.pdf', format='pdf', bbox_inches='tight')
