import numpy as np
import sympy as sp
import graphviz as gv
import random
import matplotlib.pyplot as plt
from enum import IntEnum
from multipledispatch import dispatch

class State:
    lambda_a = None
    lambda_b = None
    class varID(IntEnum):
        N_a = 0
        N_b = 1
        R_a = 2
        R_b = 3


    @dispatch(int, int, int, int, int, int)
    def __init__(self, N_a, N_b, R_a, R_b, lambda_a, lambda_b):
        State.lambda_a = lambda_a
        State.lambda_b = lambda_b
        self.__init__(N_a, N_b, R_a, R_b)

    @dispatch(int, int, int, int)
    def __init__(self, N_a, N_b, R_a, R_b):
        self.N_a = N_a
        self.N_b = N_b
        self.R_a = R_a
        self.R_b = R_b


    def __str__(self):
        return f'{self.N_a + self.R_a}.{self.N_b + self.R_b}'
    
    def __eq__(self, value: object) -> bool:
        return self.vars == value.vars
    
    def __ne__(self, value: object) -> bool:
        return self.vars != value.vars


    @property
    def vars(self):
        return [self.N_a, self.N_b, self.R_a, self.R_b]


    def next_a(self):
        vars = self.vars
        if self.R_a > 0:
            vars[self.varID.R_a] -= 1
        elif self.N_a > 1:
            vars[self.varID.N_a] -= 1
        else:
            return FailState()
        return State(*vars)
    
    def next_b(self):
        vars = self.vars
        if self.R_b > 0:
            vars[self.varID.R_b] -= 1
            return State(*vars)
        return FailState()


    @property
    def trans_a(self):
        return self.lambda_a * self.N_a
    
    @property
    def trans_b(self):
        return self.lambda_b * self.N_b


class FailState(State):
    def __init__(self):
        super().__init__(0, 0, 0, 0)
    
    def __str__(self):
        return 'F'


class States:
    def __init__(self, N_a, N_b, R_a, R_b, lambda_a, lambda_b):
        self.state_list : list[State] = []
        def addState(state : State):
            if type(state) in (State, FailState):
                if state not in self.state_list:
                    self.state_list.append(state)
                if state != FailState():
                    addState(state.next_a())
                    addState(state.next_b())

        addState(State(N_a, N_b, R_a, R_b, lambda_a, lambda_b))

        sort_states = lambda state : -1 if state == FailState() else (sort_states(state.next_a()) + sort_states(state.next_b()))
        self.state_list.sort(key = sort_states)

        self.state_amount = len(self.state_list)
        self.intens_matrix = np.zeros((self.state_amount, self.state_amount))
        for i, state in enumerate(self.state_list):
            self.intens_matrix[i][self.state_list.index(state.next_a())] += state.trans_a
            self.intens_matrix[i][self.state_list.index(state.next_b())] += state.trans_b
            self.intens_matrix[i][i] = - sum(self.intens_matrix[i])

        self.state_IDs = [*range(1, self.state_amount), 'F']
        self.t = sp.Symbol('t')
        self.SDEK = self.__SDEK__()
        self.reliability = sum(solution.rhs for solution in self.SDEK[:-1])
        self.expected = sp.integrate(self.reliability, (self.t, 0, sp.oo)).evalf()


    def __str__(self) -> str:
        return f'\nМатрица интенсивностей переходов:\n{self.intens_matrix}\n\nМат. ожидание = {self.expected}\n'


    def __SDEK__(self):
        # coef_matrix = self.intens_matrix.T.copy()
        # coef_matrix[-1] = [1] * self.state_amount

        t = self.t
        P = [sp.Function(f'P{i}') for i in self.state_IDs]

        equations=[]
        for i, line in enumerate(self.intens_matrix.T):
            left_side = P[i](t).diff(t, evaluate=False) #if (i < self.state_amount - 1) else 1
            right_side = sum([item*P[j](t) for j, item in enumerate(line) if item])
            equations.append(sp.Eq(left_side, right_side))

        return sp.dsolve(equations, [p(t) for p in P], ics={p(0) : int(not i) for i, p in enumerate(P)})


    def plot_solve(self, dest=''):
        t = self.t
        x_values = np.arange(0, 1, 1e-2)

        plt.figure(figsize=[10, 6])
        for i in range(self.state_amount):
            y_values = [self.SDEK[i].subs(t, x).rhs for x in x_values]
            plt.plot(x_values, y_values, '' if i < self.state_amount - 1 else 'r--', label=f'P_{self.state_IDs[i]}')
        plt.xlabel('t')
        plt.ylabel('P(t)')
        plot('P', dest)

    def plot_reliability(self, dest=''):
        t = self.t
        x_values = np.arange(0, 1, 1e-2)
        y_values = [self.reliability.subs(t, x) for x in x_values]
        plt.figure(figsize=[10, 6])
        plt.plot(x_values, y_values, label='^P_F')
        plt.xlabel('t')
        plt.ylabel('P(t)')
        plot('reliability', dest)


    def generate_dot(self, dest=''):
        pink = '#fbdbe1'
        red  = '#b50000'
        graph = gv.Digraph(graph_attr={'rankdir' : 'TB'}, node_attr={'shape':'circle', 'width': '0.6'})
        for i, line in enumerate(self.intens_matrix):
            for j, weight in enumerate(line):
                if weight > 0:
                    graph.edge(f'P{i+1}\\n{self.state_list[i]}', f'P{j+1}\\n{self.state_list[j]}', label=str(weight), color=red if self.state_list[j] == FailState() else 'black')
        
        get_B = lambda state : state.N_b + state.R_b
        B_set = set()
        for state in self.state_list:
            B_set.add(get_B(state))

        for B in B_set:
            B_cluster = gv.Digraph(f'cluster_{B}', graph_attr={'rankdir' : 'TB', 'rank' : 'same', 'style' : 'invis'})
            for i, state in enumerate(self.state_list):
                if B == get_B(state):
                    B_cluster.node(f'P{i+1}\\n{state}')
            graph.subgraph(B_cluster)

        graph.node(f'P{self.state_amount}\\nF', color=red, fillcolor=pink, style='filled', rank='max', width='1')
        if dest:
            graph.render(filename=dest+'state-graph.gv', engine='dot')
        return graph

    def imitation(self, exp_n, exp_plotted = 10, dest = ''):
        times = []
        random.seed(0)
        if exp_plotted > 0:
            plt.figure(figsize=[14, 6])
        for i in range(exp_n):
            plotting = (i < exp_plotted)
            if plotting:
                plot_vals = [(0, 1)]
            cur_state = self.state_list[0]
            time = 0
            time_a, time_b = 0, 0
            while cur_state != FailState():
                if time == time_a:
                    time_a += random.expovariate(cur_state.trans_a)
                if time == time_b:
                    time_b += random.expovariate(cur_state.trans_b)

                time = min(time_a, time_b)
                if time_a == time:
                    cur_state = cur_state.next_a()
                else:
                    cur_state = cur_state.next_b()

                if plotting:
                    plot_vals.append((time, self.state_list.index(cur_state) + 1))

            times.append(time)
            if plotting:
                plt.step(*zip(*plot_vals), '-o', markersize=5, linewidth=2, where='post', label=f'exp_{i+1}')

        if exp_plotted > 0:
            plt.yticks(range(1, self.state_amount + 1))
            plt.xlim(-max(times[:exp_plotted]) * 0.01, max(times[:exp_plotted]) * 1.01)
            plot('imitation', dest)
        return times

# times = []
# for i in range(100):
#   work_A = 4
#   work_B = 5
#   time_destroy_A = 0.0
#   time_destroy_B = 0.0
#   cur_time = 0.0
#   while work_A > 0 and work_B > 2:
#     if time_destroy_A == cur_time:
#       time_destroy_A += random.expovariate(14 if work_A > 1 else 7)
#     if time_destroy_B == cur_time:
#       time_destroy_B += random.expovariate(work_B * 8)
#     if time_destroy_A < time_destroy_B:
#       cur_time = time_destroy_A
#       work_A -= 1
#     else:
#       cur_time = time_destroy_B
#       work_B -= 1
#   times.append(cur_time)


def plot(filename='', dest=''):
    plt.legend(fontsize='12')
    plt.grid()
    plt.title(filename)
    if dest:
        plt.savefig(dest+filename+'.pdf', format='pdf', bbox_inches='tight')
    else:
        plt.show()
