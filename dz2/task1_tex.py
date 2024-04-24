import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tex_init import tex_init, tex_matrix

def generate_task1_tex(dest, images_src, states, deviations):
        main_dest = tex_init(dest, images_path=images_src, lab_title='Теория надёжности')
        with open(main_dest, 'w') as doc:
            doc.write('''\subsection*{Задание.} \label{sec:task}
Система состоит из устройств типа $A$ и типа $B$, интенсивности отказов $\lambda_A$ и $\lambda_B$ известны.
Для функционирования системы требуется хотя бы одно устройство типа $A$ и хотя бы $N_b$
устройств типа $B$. Также имеются резервные устройства в количествах $R_A$ и $R_B$
соответственно, причём в нормальном состоянии одновременно включены сразу $N_A$
устройств типа $A$.
Если $N$ – номер зачётной книжки, а $G$ \--- последняя цифра в номере группы, то параметры системы определяются следующим образом:
\\begin{align*}
''' + f'''    \lambda_A &= G + (N \\text{{ mod }} 3) = {states.state_list[0].lambda_a} \\\\
    \lambda_B &= G + (N \\text{{ mod }} 5) = {states.state_list[0].lambda_b} \\\\
    N_A &= 2 + (G \\text{{ mod }} 2) = {states.state_list[0].N_a} \\\\
    N_B &= 1 + (N \\text{{ mod }} 2) = {states.state_list[0].N_b} \\\\
    R_A &= 1 + (G \\text{{ mod }} 2) = {states.state_list[0].R_a} \\\\
    R_B &= 2 – (G \\text{{ mod }} 2) = {states.state_list[0].R_b} ''' + '''
\end{align*}
Требуется:
\\begin{enumerate}
    \item нарисовать граф состояний системы;
    \item составить матрицу интенсивностей переходов;
    \item записать дифференциальные уравнения Колмогорова;
    \item методами численного интегрирования решить полученную систему дифференциальных уравнений, исходя из того, что в начальный момент времени все устройства исправны;
    \item построить графики вероятностей нахождения системы в каждом из возможных состояний с течением времени;
    \item построить график функции надёжности системы;
    \item рассчитать математическое ожидание времени безотказной работы;
    \item провести имитационное моделирование системы в терминах непрерывных марковских
цепей 100 раз, рассчитать среднее выборочное значение и стандартное отклонение
времени безотказной работы системы.
\end{enumerate}
\\newpage

\subsection*{Решение}\label{subsec:2}
\subsubsection*{Граф состояний системы}

\\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\linewidth]{images/state-graph.gv.pdf}
    \caption{График функции надёжности.}
    \label{fig:rel}
\end{figure}

\subsubsection*{Матрица интенсивностей переходов}
Матрица интенсивностей переходов имеет следующий вид:

''' + tex_matrix(states.intens_matrix) + '''

\subsubsection*{Дифференциальные уравнения Колмогорова}
Уравнения Колмогорова можно представить в следующем виде:

\\[Q^T \pi = \dot{\pi}, \\]
где $Q$ \--- матрица интенсивностей переходов, $\pi$ \--- вектор вероятностей.

Численно решив данную систему, можно построить графики вероятностей нахождения в каждом из состояний.

\\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{images/P.pdf}
    \caption{График вероятностей системы от времени.}
    \label{fig:P}
\end{figure}

\subsubsection*{Функция надежности системы}
Функция надежности системы выражается следующей формулой:

\[\\bar{P}(t) = 1 - P_F(t)\]

График функции надёжности построен на \hyperref[fig:rel]{рисунке 3}.

\\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{images/reliability.pdf}
    \caption{График функции надёжности.}
    \label{fig:rel}
\end{figure}

\subsubsection*{Математическое ожидание}
Формула математического ожидания времени безотказной работы:

\[M = \int_0^{+\infty} \\bar{P}(t)dt\]

''' + f'Для данной системы математическое ожидание принимает значение $M = {states.expected:.5f}$.' + '''

\subsubsection*{Имитационное моделирование системы}
Было проведено 100 испытаний, в результате которых были получены среднее время работы системы и стандартное отклонение:
''' + f'\[T_{{cp}} = {deviations[0]:.5f}, \qquad \sigma = {deviations[2]:.5f} \]' + '''
\\begin{figure}[H]
    \centering
    \includegraphics[width=\linewidth]{images/imitation.pdf}
    \caption{График переходов между состояниями для 10 экспериментов.}
    \label{fig:exp}
\end{figure}
''')
