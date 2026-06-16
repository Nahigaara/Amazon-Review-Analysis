"""
Точка входа приложения «Анализ отзывов на Amazon».

Запуск: python main.py (из каталога work)

Авторы: Семиненко А., Подойникова Л.
Группа: БИВ256
"""

import runpy
import os
import sys

# Добавить пути к модулям
_work = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_work, 'library'))
sys.path.insert(0, os.path.join(_work, 'scripts'))

# Запустить scripts/main.py как __main__ — сохранит корректный __file__
runpy.run_path(os.path.join(_work, 'scripts', 'main.py'), run_name='__main__')
