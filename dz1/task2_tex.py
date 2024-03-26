import sys
import os
from class_chain import ClassifiedMarkovChain

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from tex_init import tex_init, tex_matrix

def generate_task2_tex(dest, img_src, chain : ClassifiedMarkovChain, experiment_data):
    main_dest = tex_init(dest, 'Моделирование цепей Маркова с значащими и незначащими классами', img_src)
    with open(main_dest, 'w') as doc:
            doc.write('\subsection*{Задание.' + (f' Вариант {chain.variant}.' if chain.variant else '') + '''}
\label{blockN.VariantM}
\\addcontentsline{toc}{subsection}{Задание}
\\noindent Для цепи Маркова, заданной стохастической матрицей переходов:
\\begin{enumerate}
    \item нарисовать граф цепи;
    \item выделить классы существенных и несущественных состояний (вручную – обязательно; программным путём – дополнительное задание для желающих);
    \item перенумеровать состояния системы так, чтобы несущественные состояния и состояния из каждого класса существенных состояний были идентифицированы смежными номерами;
    \item рассчитать предельные распределения вероятностей для всех классов существенных состояний;
    \item не выполняя матричных операций с полной стохастической матрицей переходов сформировать предельную стохастическую матрицу переходов;
    \item провести имитационное моделирование системы, соответствующей рассматриваемой цепи, для этого:
    \\begin{itemize}
        \item перебираем все состояния в качестве исходных;
        \item случайно разыграть переход в новое состояние, учитывая распределение вероятностей перехода;
        \item совершить 100 переходов;
        \item подсчитать число вхождений в каждое из состояний системы;
        \item повторить эксперимент 10 раз для каждого исходного состояния;
        \item построить «графики» переключений состояний цепи (для наглядности соединяем дискретные точки), стартовать по 2 раза внутри каждого класса существенных состояний, 6 раз внутри класса несущественных состояний.
    \end{itemize}
\end{enumerate}
\\newpage

\subsection*{Решение}\label{subsec:2}
\\addcontentsline{toc}{subsection}{Решение}
\\noindent Cтохастическая матрица переходов''' + (f' для варианта {chain.variant}' if chain.variant else '') + ':\n\[' + tex_matrix(chain.transition_matrix) +
'''\]
\subsubsection*{Граф цепи Маркова}
\\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{images/markov-chain.pdf}
    \caption{Граф цепи Маркова}
    \label{fig:chain}
\end{figure}
\\newpage
\subsubsection*{Выделение классов в цепи}
\\renewcommand{\labelenumi}{\Alph{enumi}:}
Несущественный класс:
\\begin{enumerate}
    \setcounter{enumi}{13}
    \item $''' + tex_matrix([chain.N_class_nums]) + '''$
\end{enumerate}

Существенные классы:
\\begin{enumerate}
    \item $''' + '$\n\t\item $'.join([tex_matrix([m_class]) for m_class in chain.closed_classes_nums]) + '''$
\end{enumerate}

\subsubsection*{Перенумерование состояний системы}
\\noindent Матрица была преобразована с целью визуального выделения классов состояний.

\[''' + tex_matrix(chain.ordered_transition_matrix) + '''\]

\subsubsection*{Предельные матрицы переходов существенных классов}
\\begin{multicols}{3}
\\begin{enumerate}
    \item $''' + '$\n\t\item $'.join([tex_matrix(m_class.edge_matrix) for m_class in chain.closed_classes]) + '''$
\end{enumerate}
\end{multicols}
\\newpage

\subsubsection*{Предельная матрица переходов всей системы}
\\noindent Каждый из существенных классов можно свернуть до 1 вершины. Полученная сокращённая матрица приобретает следующий вид:
\[''' + tex_matrix(chain.N_class.transition_matrix) + '''\]

\\noindent Предельная матрица переходов для данной матрицы получена её возведением в $n \\rightarrow \infty$ степень.
В рамках численного метода матрица перемножается сама на себя, пока при поэлементном вычитании матриц
на текущей и предидущей итерациях наибольший модуль разницы не достигнет значения, сопоставимого с машинным $\\varepsilon$.

\\noindent Полученная предельная матрица выглядит следующим образом:
\[''' + tex_matrix(chain.N_class.edge_matrix) + '''\]

\\noindent Расширив сокращенную предельную матрицу предельными матрицами значащих классов,
получена полная предельная матрица для заданной цепи Маркова:
\[''' + tex_matrix(chain.edge_matrix) + '''\]

\\newpage
\subsubsection*{Имитационное моделирование системы}
\\noindent Проведено по 10 экспериментов для каждого начального состояния системы, в каждом из которых
разыграны 100 случайных переходов межу состояниями в соответствии с матрицей переходов.

\\noindent Для каждого начального состояния были рассчитаны частоты вхождений во все состояния системы:
\[''' + tex_matrix([[i+1, *line] for i, line in enumerate(experiment_data)]) + '''\]

\\noindent На рисунке \hyperref[fig:exp]{2} построены 6 графиков для экспериментов с началом из несущественного класса
и по 2 графика для начала из каждого из существенных состояний.

\\begin{figure}[H]
    \centering
    \includegraphics[width=\linewidth]{images/exp1.pdf}
    \caption{График переходов в системе.}
    \label{fig:exp}
\end{figure}
''')
