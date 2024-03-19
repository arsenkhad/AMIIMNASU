import numpy as np
from distutils.dir_util import copy_tree
import sys
import os

SCRIPT_PARENT_DIR = os.path.dirname(os.path.abspath(__file__))+'/..'
sys.path.append(os.path.dirname(SCRIPT_PARENT_DIR))
from tex_defines import gen_defines
# from task1 import Markov_chain

def tex_matrix(matrix):
    return '\\begin{bmatrix}\n\t' + ' \\\\\n\t'.join([' & '.join(map(lambda x : str(x) if type(x) == int else f'{x:.2f}', line)) for line in matrix]) + '\n\\end{bmatrix}\n'

def tex_experiment_pic(i):
    i += 1
    return f'''
\\begin{{figure}}[H]
    \centering
    \includegraphics[width=\linewidth]{{images/exp{i}.png}}
    \caption{{Эксперимент {i}}}
    \label{{fig:exp{i}}}
\end{{figure}}
'''

def tex_experiment_table(data, caption, label, columns = 1):
    data_len = len(data[0])
    data = np.array(data).reshape(-1, data_len * columns)
    table_len = len(data)
    return ('''\\begin{table}[H]
    \centering
    \\begin{tabular}{''' +
        ('|' + '|'.join('c' * (data_len + 1)) + '|') * columns +
        '}\n\t\t\hline' +
        '\t& '.join([(' \\textnumero &' + '\t& '.join([str(i+1) for i in range(data_len)]))] * columns) +
        f'''\\\\
        \hline ''' +
        '\\\\\n\t\t\hline '.join([' & '.join([('' if j % data_len else str(i+1 + (j // data_len) * table_len) + ' & ') + str(round(item, 3)) for j, item in enumerate(line)]) for i, line in enumerate(data)]) +
        f'''\\\\
        \hline
    \end{{tabular}}
    \caption{{{caption}}}
    \label{{tab:{label}}}
\end{{table}}''')

def tex_deviation_table(deviations, caption, label):
    data_len = len(deviations[0])
    return ('''\\begin{table}[H]
    \centering
    \\begin{tabular}{''' +
        '|' + '|'.join('c' * (data_len + 1)) + '|' +
        '}\n\t\t\hline' +
        '   &' + '\t& '.join([str(i+1) for i in range(data_len)]) +
        '''\\\\
        \hline      Средняя оценка & ''' + ' & '.join([str(round(item, 3)) for item in deviations[0]]) + '''\\\\
        \hline Исправленная оценка & ''' + ' & '.join([str(round(item, 3)) for item in deviations[1]]) + f'''\\\\
        \hline
    \end{{tabular}}
    \caption{{{caption}}}
    \label{{tab:{label}}}
\end{{table}}''')

# def generate_tex(chain : Markov_chain):
def generate_task1_tex(dest, chain, experiment_data, deviations, pic_number):
        copy_tree(SCRIPT_PARENT_DIR+'/tex_template', dest)
        gen_defines(dest, 'Моделирование цепей Маркова, заданных матрицей переходов')

        A = chain.transition_matrix.transpose() - np.diag([1 for _ in chain.transition_matrix])
        A1 = A.copy()
        A1[-1] = [1] * chain.node_count
        B1 = [0] * (chain.node_count)
        B1[-1] = 1

        with open(dest+'main-project/task-text.tex', 'w') as doc:
            doc.write(f'\subsection*{{Задание. Вариант {chain.variant}.}}' + '''
\label{blockN.VariantM}
\\addcontentsline{toc}{subsection}{Задание}
Для цепи Маркова, заданной стохастической матрицей переходов:
\\begin{enumerate}
    \item нарисовать граф цепи;
    \item проверить выполнение критерия эргодичности;
    \item рассчитать предельные вероятности;
    \item записать предельную матрицу переходов;
    \item провести имитационное моделирование системы, соответствующей рассматриваемой цепи, для этого:
    \\begin{itemize}
        \item случайно выбрать начальное состояние;
        \item случайно разыграть переход в новое состояние, учитывая распределение
вероятностей перехода;
        \item совершить 100 переходов;
        \item подсчитать число вхождений в каждое из состояний системы;
        \item повторить эксперимент 50 раз;
        \item построить «графики» переключений состояний цепи (для наглядности соединяем
дискретные точки) для 3 произвольных экспериментов;
        \item составить таблицу для сравнения относительных частот наблюдений вхождения в
каждое из состояний системы;
        \item рассчитать выборочные средние и исправленные оценки среднеквадратичных
отклонений указанных относительных частот.
    \end{itemize}
\end{enumerate}
\\newpage

\subsection*{Решение}\label{subsec:2}
\\addcontentsline{toc}{subsection}{Решение}
Cтохастическая матрица переходов для варианта '''+chain.variant + ':\n\[' + tex_matrix(chain.transition_matrix) +
'''\]
\subsubsection*{Граф цепи Маркова}
\\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{images/markov-chain.pdf}
    \caption{Граф цепи Маркова}
    \label{fig:diod}
\end{figure}
\\newpage

\subsubsection*{Критерий эргодичности}
Конечная ДЦМ является эргодичной, когда она неразложима (неприводима) и непереодична.  
В заданной цепи нет несущественных классов и из существенных нельзя выделить несколько классов, следовательно, цепь неразложима.

Так же, НОД(n), следовательно, наша цепи непереодична. 
Следовательно, наша ДЦМ эргодична.

\subsubsection*{Предельные вероятности}
Рассчитаем предельные вероятности по формуле:
\[ (P^T - E) \cdot \pi^0 = 0 \]

Для заданной цепи Маркова СЛАУ приобретает следующий вид:
\[''' + tex_matrix(A) + '+' + tex_matrix([[]]) + '=' + tex_matrix([[0]] * chain.node_count) + '''\]

Данная СЛАУ является линейно зависимой и не даёт решений, поэтому последняя строка заменяется на условие $\sum \pi = 1$:

\[''' + tex_matrix(A1) + '+' + tex_matrix([[]]) + '=' + tex_matrix([[item] for item in B1]) + '''\]

При решении данной СЛАУ получены следующие предельные вероятности:

\[''' + tex_matrix([chain.edge_possibilities]) + '''\]

\subsubsection*{Предельная матрица переходов}
На основе полученных предельных вероятностей предельная матрица переходов примет следующий вид:
\[''' + tex_matrix(chain.edge_matrix) + '''\]

\\newpage
\subsubsection*{Имитационное моделирование системы}
Проведено 50 экспериментов, в каждом из которых разыграны 100 переходов межу состояниями.
''' + ''.join([tex_experiment_pic(i) for i in range(pic_number)]) +
'''
\\newpage
Для каждого из экспериментов были рассчитаны относительне частоты наблюдений вхождения в
каждое из состояний системы.

''' + tex_experiment_table(experiment_data, 'Относительные частоты наблюдений для 50 экспериментов', 'freq-experiment', 2) + '''

\\newpage
Выборочная средняя оценка среднеквадратичного отклонения:
\\[ \sigma = \sqrt{\\frac{1}{n}\sum_{i=1}^n(\chi_i-\\bar{\chi})^2} \\]

Выборочная исправленная оценка среднеквадратичного отклонения:
\\[ \sigma = \sqrt{\\frac{1}{n-1}\sum_{i=1}^n(\chi_i-\\bar{\chi})^2} \\]

Согласно данным формулам для полученных относительных частот рассчитаны выборочные средние и исправленные оценки среднеквадратичных
отклонений.

''' + tex_deviation_table(deviations, 'Среднеквадратичные отклонения относительных частот', 'deviations') + '''

''')


        
