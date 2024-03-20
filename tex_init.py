from distutils.dir_util import copy_tree, remove_tree
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
        
def tex_init(dest, lab_title, images_path = '', clean = True):
    copy_tree('tex_template', dest)
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