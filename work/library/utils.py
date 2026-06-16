"""
Библиотека универсальных вспомогательных функций.

Содержит функции для работы с файлами, конфигурацией и данными,
которые могут использоваться в различных информационно-аналитических
приложениях.

Авторы: Семиненко А., Подойникова Л.
Группа: БИВ256
"""

import pickle
import configparser
import os


def load_config(path):
    """
    Загрузить конфигурационный файл формата INI.

    Parameters
    ----------
    path : str
        Путь к файлу конфигурации.

    Returns
    -------
    configparser.ConfigParser
        Объект с параметрами конфигурации.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding='utf-8')
    return cfg


def save_binary(obj, path):
    """
    Сохранить объект в двоичный файл формата pickle.

    Parameters
    ----------
    obj : object
        Любой сериализуемый объект Python.
    path : str
        Путь для сохранения файла.

    Returns
    -------
    bool
        True при успешном сохранении, False при ошибке.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    try:
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
        return True
    except Exception:
        return False


def load_binary(path):
    """
    Загрузить объект из двоичного файла формата pickle.

    Parameters
    ----------
    path : str
        Путь к файлу.

    Returns
    -------
    object or None
        Загруженный объект или None при ошибке / отсутствии файла.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def ensure_dir(path):
    """
    Создать директорию, если она не существует.

    Parameters
    ----------
    path : str
        Путь к директории.

    Returns
    -------
    None

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    os.makedirs(path, exist_ok=True)


def save_text_report(text, path):
    """
    Сохранить текстовый отчёт в файл.

    Parameters
    ----------
    text : str
        Содержимое отчёта.
    path : str
        Путь для сохранения файла.

    Returns
    -------
    bool
        True при успехе, False при ошибке.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception:
        return False
