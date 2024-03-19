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