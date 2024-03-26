from distutils.dir_util import copy_tree, remove_tree
import numpy as np
import os

author = 'Хадарцев Арсений Витальевич'
group = 'РК6-83Б'
teacher = 'Берчун Ю.В.'
year = '2024'
__nameprt = author.split()
author_short = __nameprt[0] + '~' + ''.join([part[0]+'.' for part in __nameprt[1:]])

def gen_defines(dest, lab_title):
    with open(dest+'main-project/defines.tex', 'w') as defines:
        defines.write(f'''\\newcommand{{\\Title}}{{Отчет о выполнении домашнего задания}}
\\newcommand{{\\TaskType}}{{Домашнее задание}}
\\newcommand{{\\SubTitle}}{{по дисциплине <<Аналитические модели и имитационное моделирование на системном уровне>>}}
\\newcommand{{\\LabTitle}}{{{lab_title}}}
\\newcommand{{\\Faculty}}{{<<Робототехники и комплексной автоматизации>>}}
\\newcommand{{\\Department}}{{<<Системы автоматизированного проектирования (РК-6)>>}}
\\newcommand{{\\AuthorFull}}{{{author}}}
\\newcommand{{\\Author}}{{{author_short}}}
\\newcommand{{\\Teacher}}{{{teacher}}}
\\newcommand{{\\group}}{{{group}}}
\\newcommand{{\\Semestr}}{{Весенний семестр}}
\\newcommand{{\\Year}}{{{year}}}
\\newcommand{{\\Country}}{{Россия}}
\\newcommand{{\\City}}{{Москва}}''')
        
def tex_matrix(matrix):
    return '\\begin{bmatrix}\n\t' + ' \\\\\n\t'.join([' & '.join(map(lambda x : f'{x:.2f}' if type(x) in (float, np.float64) else str(x), line)) for line in matrix]) + '\n\\end{bmatrix}\n'

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
        
def tex_init(dest : str, lab_title : str, images_path = '', clean = True):
    if dest[-1] != '/':
        dest += '/'
    copy_tree('tex_template', dest)
    main_title = dest.split('/')[-2]
    if main_title and main_title != '.':
        os.rename(dest+'main.tex', dest+main_title+'.tex')
    main_folder = dest+'main-project'
    try:
        os.mkdir(main_folder)
    except FileExistsError:
        pass
    if images_path:
        copy_tree(images_path, dest+'images')
        if clean:
            remove_tree(images_path)

    gen_defines(dest, lab_title)
    return main_folder + '/task-text.tex'
