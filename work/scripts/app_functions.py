"""
Специализированный модуль функций приложения.

Анализ отзывов на Amazon.
Содержит функции генерации данных, аналитики,
формирования отчётов и вспомогательные операции.

Авторы: Семиненко А., Подойникова Л.
Группа: БИВ256
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os  # noqa: F401


CATEGORIES = [
    'Электроника', 'Книги', 'Одежда', 'Кухня',
    'Спорт', 'Красота', 'Игрушки', 'Инструменты'
]

SENTIMENTS = ['Позитивная', 'Нейтральная', 'Негативная']

PRODUCT_NAMES = [
    'Беспроводные наушники SoundPro',
    'Смарт-часы FitX 3',
    'Планшет TechPad 10',
    'Робот-пылесос CleanBot',
    'Камера SnapShot 4K',
    'Ноутбук UltraBook 15',
    'Книга «Python для всех»',
    'Книга «Машинное обучение»',
    'Книга «Алгоритмы и структуры данных»',
    'Роман «Северное сияние»',
    'Футболка SportFit Pro',
    'Куртка OutdoorMax',
    'Джинсы SlimFit 32',
    'Платье EveningStyle',
    'Блендер MixMaster 800',
    'Кофемашина BrewMaster',
    'Сковорода GrillPro 28',
    'Набор ножей ChefSet',
    'Кроссовки RunFast X2',
    'Велосипед MountainX 26',
    'Гантели AdjustFit 20кг',
    'Йога-коврик ZenPad',
    'Крем для лица GlowSkin',
    'Шампунь HairLux Pro',
    'Парфюм NightBloom',
    'Конструктор BrickCity 500',
    'Настольная игра «Монополия»',
    'Мягкая игрушка TeddyFriend',
    'Дрель PowerDrill 18V',
    'Набор отвёрток FixIt Pro',
]


def generate_initial_data():
    """
    Сгенерировать начальные данные: справочники товаров и отзывов.

    Создаёт набор из 30 товаров и 150 отзывов.

    Parameters
    ----------
    None

    Returns
    -------
    tuple
        Кортеж (df_products, df_reviews).

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    np.random.seed(42)

    cat_map = {
        'Электроника': [0, 1, 2, 3, 4, 5],
        'Книги': [6, 7, 8, 9],
        'Одежда': [10, 11, 12, 13],
        'Кухня': [14, 15, 16, 17],
        'Спорт': [18, 19, 20, 21],
        'Красота': [22, 23, 24],
        'Игрушки': [25, 26, 27],
        'Инструменты': [28, 29],
    }

    price_ranges = {
        'Электроника': (3000, 80000),
        'Книги': (300, 1500),
        'Одежда': (800, 8000),
        'Кухня': (600, 15000),
        'Спорт': (500, 25000),
        'Красота': (400, 3000),
        'Игрушки': (500, 4000),
        'Инструменты': (800, 6000),
    }

    products = []
    for pid, name in enumerate(PRODUCT_NAMES, start=1):
        cat = next(
            c for c, idxs in cat_map.items()
            if (pid - 1) in idxs
        )
        lo, hi = price_ranges[cat]
        price = round(np.random.uniform(lo, hi), 2)
        products.append({
            'ID_товара': pid,
            'Наименование': name,
            'Категория': cat,
            'Цена': price,
        })

    df_products = pd.DataFrame(products)

    reviews = []
    probs = [0.08, 0.10, 0.14, 0.30, 0.38]
    for rid in range(1, 151):
        pid = int(np.random.choice(df_products['ID_товара']))
        score = int(np.random.choice([1, 2, 3, 4, 5], p=probs))
        if score >= 4:
            sentiment = 'Позитивная'
        elif score == 3:
            sentiment = 'Нейтральная'
        else:
            sentiment = 'Негативная'
        length = int(np.random.randint(10, 300))
        reviews.append({
            'ID_отзыва': rid,
            'ID_товара': pid,
            'Оценка': score,
            'Тональность': sentiment,
            'Длина_отзыва': length,
        })

    df_reviews = pd.DataFrame(reviews)
    return df_products, df_reviews


def get_next_product_id(df_products):
    """
    Получить следующий свободный идентификатор товара.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.

    Returns
    -------
    int
        Следующий доступный ID.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    if df_products.empty:
        return 1
    return int(df_products['ID_товара'].max()) + 1


def get_next_review_id(df_reviews):
    """
    Получить следующий свободный идентификатор отзыва.

    Parameters
    ----------
    df_reviews : pd.DataFrame
        Справочник отзывов.

    Returns
    -------
    int
        Следующий доступный ID.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    if df_reviews.empty:
        return 1
    return int(df_reviews['ID_отзыва'].max()) + 1


def build_merged(df_products, df_reviews):
    """
    Объединить справочники товаров и отзывов.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.

    Returns
    -------
    pd.DataFrame
        Объединённая таблица с полями обоих справочников.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    return pd.merge(df_reviews, df_products, on='ID_товара', how='left')


def report_filtered_products(df_products, df_reviews, category=None):
    """
    Сформировать отчёт: список товаров со средней оценкой.

    Применяет операции проекции и сокращения.
    Использует объединение таблиц Pandas.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.
    category : str or None
        Категория для фильтрации (None — все).

    Returns
    -------
    tuple
        (str, pd.DataFrame) — текст отчёта и DataFrame.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)
    avg = merged.groupby(
        ['ID_товара', 'Наименование', 'Категория', 'Цена']
    )['Оценка'].mean().reset_index()
    avg.rename(columns={'Оценка': 'Средняя_оценка'}, inplace=True)
    avg['Средняя_оценка'] = avg['Средняя_оценка'].round(2)

    if category and category != 'Все':
        avg = avg[avg['Категория'] == category]

    result = avg[
        ['ID_товара', 'Наименование', 'Категория',
         'Цена', 'Средняя_оценка']
    ].reset_index(drop=True)

    if category and category != 'Все':
        title = f'Товары категории «{category}»'
    else:
        title = 'Все товары'

    lines = [
        f'Отчёт: {title}',
        '=' * 60,
        result.to_string(index=False),
        '',
        f'Всего записей: {len(result)}',
    ]
    return '\n'.join(lines), result


def report_statistics(df_products, df_reviews):
    """
    Сформировать статистический отчёт по атрибутам.

    Для качественных переменных — таблица частот.
    Для количественных — min, max, mean, var, std.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.

    Returns
    -------
    tuple
        (str, dict) — текст отчёта и словарь DataFrame.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)

    qual_cols = ['Тональность', 'Категория']
    quant_cols = ['Оценка', 'Цена', 'Длина_отзыва']

    lines = ['Статистический отчёт', '=' * 60]
    result = {}

    lines.append('\n--- Качественные переменные ---')
    for col in qual_cols:
        freq = merged[col].value_counts().reset_index()
        freq.columns = [col, 'Частота']
        total = freq['Частота'].sum()
        freq['Процент'] = (freq['Частота'] / total * 100).round(2)
        result[col] = freq
        lines.append(f'\n{col}:')
        lines.append(freq.to_string(index=False))

    lines.append('\n--- Количественные переменные ---')
    stats_rows = []
    for col in quant_cols:
        s = merged[col]
        stats_rows.append({
            'Переменная': col,
            'Минимум': round(float(s.min()), 2),
            'Максимум': round(float(s.max()), 2),
            'Среднее': round(float(s.mean()), 2),
            'Дисперсия': round(float(s.var()), 2),
            'Ст. откл.': round(float(s.std()), 2),
        })
    df_stats = pd.DataFrame(stats_rows)
    result['quant'] = df_stats
    lines.append('')
    lines.append(df_stats.to_string(index=False))

    return '\n'.join(lines), result


def report_pivot(df_products, df_reviews,
                 row_col, col_col, val_col, aggfunc):
    """
    Сформировать сводную таблицу.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.
    row_col : str
        Атрибут для строк сводной таблицы.
    col_col : str
        Атрибут для столбцов сводной таблицы.
    val_col : str
        Числовой атрибут для агрегации.
    aggfunc : str
        Функция агрегации (mean, sum, count, min, max).

    Returns
    -------
    tuple
        (str, pd.DataFrame) — текст отчёта и DataFrame.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)
    pivot = pd.pivot_table(
        merged, values=val_col,
        index=row_col, columns=col_col,
        aggfunc=aggfunc
    ).round(2)
    header = (
        f'Сводная таблица: {row_col} × {col_col}'
        f' (значение: {val_col}, агрегация: {aggfunc})'
    )
    lines = [header, '=' * 60, pivot.to_string()]
    return '\n'.join(lines), pivot


def plot_clustered_bar(df_products, df_reviews,
                       qual1, qual2, save_path=None):
    """
    Построить кластеризованную столбчатую диаграмму.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.
    qual1 : str
        Качественный атрибут для оси X (группы).
    qual2 : str
        Качественный атрибут для кластеризации (цвет).
    save_path : str or None
        Путь для сохранения PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Объект фигуры.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)
    ct = pd.crosstab(merged[qual1], merged[qual2])

    fig, ax = plt.subplots(figsize=(10, 5))
    categories = ct.index.tolist()
    sub_cats = ct.columns.tolist()
    x = np.arange(len(categories))
    width = 0.8 / len(sub_cats)
    colors = plt.cm.Set2(np.linspace(0, 1, len(sub_cats)))

    for i, sub in enumerate(sub_cats):
        ax.bar(x + i * width, ct[sub],
               width=width, label=sub, color=colors[i])

    ax.set_xticks(x + width * (len(sub_cats) - 1) / 2)
    ax.set_xticklabels(categories, rotation=30, ha='right')
    ax.set_title(f'Распределение «{qual2}» по «{qual1}»')
    ax.set_ylabel('Количество')
    ax.legend(title=qual2)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def plot_categorized_hist(df_products, df_reviews,
                          quant_col, qual_col, save_path=None):
    """
    Построить категоризированную гистограмму.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.
    quant_col : str
        Количественный атрибут.
    qual_col : str
        Качественный атрибут (категории).
    save_path : str or None
        Путь для сохранения PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Объект фигуры.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)
    groups = merged[qual_col].unique()
    cols = min(3, len(groups))
    rows = int(np.ceil(len(groups) / cols))
    colors = plt.cm.Set3(np.linspace(0, 1, len(groups)))

    fig, axes = plt.subplots(rows, cols,
                             figsize=(5 * cols, 4 * rows))
    axes = np.array(axes).flatten()

    for i, grp in enumerate(groups):
        data = merged[merged[qual_col] == grp][quant_col].dropna()
        axes[i].hist(data, bins=15,
                     color=colors[i], edgecolor='white')
        axes[i].set_title(grp)
        axes[i].set_xlabel(quant_col)
        axes[i].set_ylabel('Частота')

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(
        f'Гистограмма «{quant_col}» по «{qual_col}»',
        fontsize=13
    )
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def plot_boxplot(df_products, df_reviews,
                 quant_col, qual_col, save_path=None):
    """
    Построить категоризированную диаграмму Бокса-Вискера.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.
    quant_col : str
        Количественный атрибут.
    qual_col : str
        Качественный атрибут (категории).
    save_path : str or None
        Путь для сохранения PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Объект фигуры.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)
    groups = sorted(merged[qual_col].unique())
    data_groups = [
        merged[merged[qual_col] == g][quant_col].dropna().values
        for g in groups
    ]

    fig, ax = plt.subplots(figsize=(10, 5))
    bp = ax.boxplot(data_groups, patch_artist=True, notch=False)
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(groups)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    ax.set_xticklabels(groups, rotation=30, ha='right')
    ax.set_title(
        f'Диаграмма Бокса-Вискера: «{quant_col}» по «{qual_col}»'
    )
    ax.set_ylabel(quant_col)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def plot_scatter(df_products, df_reviews,
                 x_col, y_col, color_col, save_path=None):
    """
    Построить категоризированную диаграмму рассеивания.

    Parameters
    ----------
    df_products : pd.DataFrame
        Справочник товаров.
    df_reviews : pd.DataFrame
        Справочник отзывов.
    x_col : str
        Количественный атрибут для оси X.
    y_col : str
        Количественный атрибут для оси Y.
    color_col : str
        Качественный атрибут для цветового разделения.
    save_path : str or None
        Путь для сохранения PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Объект фигуры.

    Authors
    -------
    Семиненко А., Подойникова Л.
    """
    merged = build_merged(df_products, df_reviews)
    groups = sorted(merged[color_col].unique())
    colors = plt.cm.Set1(np.linspace(0, 1, len(groups)))

    fig, ax = plt.subplots(figsize=(9, 5))
    for grp, color in zip(groups, colors):
        sub = merged[merged[color_col] == grp]
        ax.scatter(sub[x_col], sub[y_col],
                   label=grp, color=color, alpha=0.7, s=50)

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(
        f'Диаграмма рассеивания: «{x_col}» vs «{y_col}»'
        f' (цвет: «{color_col}»)'
    )
    ax.legend(title=color_col)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig
