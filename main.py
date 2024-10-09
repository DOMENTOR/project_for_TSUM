import sys
import os

# # Добавляем папки 'parsing' и 'modelling' в sys.path
# sys.path.append(os.path.join(os.path.dirname(__file__), 'parsing'))
# sys.path.append(os.path.join(os.path.dirname(__file__), 'modelling'))

# Импорт модулей из обеих веток
from parsing.parsing_main import create_gui
# from modelling.some_module import some_function  # пример для папки modelling

# Запуск GUI
create_gui()
