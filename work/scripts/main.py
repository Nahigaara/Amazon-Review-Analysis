"""
Главный скрипт приложения «Анализ отзывов на Amazon».

Запуск: python main.py (из каталога work)

Авторы: Семиненко А., Подойникова Л.
Группа: БИВ256
"""

import sys
import os

# Добавить пути к модулям проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, os.path.join(WORK_DIR, 'library'))
sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import utils
import app_functions as af

# ──────────────────────────────────────────────────────────────
# Глобальные переменные приложения
# ──────────────────────────────────────────────────────────────
CFG = None
DF_PRODUCTS = pd.DataFrame()
DF_REVIEWS = pd.DataFrame()
DATA_DIR = ''
OUTPUT_DIR = ''
GRAPHICS_DIR = ''


def init_app():
    """Инициализировать приложение: загрузить конфиг и данные."""
    global CFG, DF_PRODUCTS, DF_REVIEWS
    global DATA_DIR, OUTPUT_DIR, GRAPHICS_DIR

    cfg_path = os.path.join(BASE_DIR, 'config.ini')
    CFG = utils.load_config(cfg_path)

    DATA_DIR = os.path.join(WORK_DIR, CFG['paths']['path_data'])
    OUTPUT_DIR = os.path.join(WORK_DIR, CFG['paths']['path_output'])
    GRAPHICS_DIR = os.path.join(WORK_DIR, CFG['paths']['path_graphics'])

    for d in (DATA_DIR, OUTPUT_DIR, GRAPHICS_DIR):
        utils.ensure_dir(d)

    p_path = os.path.join(DATA_DIR, CFG['paths']['file_products'])
    r_path = os.path.join(DATA_DIR, CFG['paths']['file_reviews'])

    loaded_p = utils.load_binary(p_path)
    loaded_r = utils.load_binary(r_path)

    if loaded_p is None or loaded_r is None:
        DF_PRODUCTS, DF_REVIEWS = af.generate_initial_data()
        utils.save_binary(DF_PRODUCTS, p_path)
        utils.save_binary(DF_REVIEWS, r_path)
    else:
        DF_PRODUCTS = loaded_p
        DF_REVIEWS = loaded_r


def save_data():
    """Сохранить оба справочника на диск."""
    p_path = os.path.join(DATA_DIR, CFG['paths']['file_products'])
    r_path = os.path.join(DATA_DIR, CFG['paths']['file_reviews'])
    utils.save_binary(DF_PRODUCTS, p_path)
    utils.save_binary(DF_REVIEWS, r_path)


def get_font(size_key='font_size_main'):
    """Получить шрифт из конфигурации."""
    name = CFG['fonts']['font_main']
    size = int(CFG['fonts'][size_key])
    return (name, size)


def styled_btn(parent, text, command):
    """Создать стилизованную кнопку согласно конфигурации."""
    btn = tk.Button(
        parent, text=text, command=command,
        bg=CFG['colors']['bg_button'],
        fg=CFG['colors']['fg_button'],
        font=get_font('font_size_button'),
        padx=10, pady=4, cursor='hand2'
    )
    return btn


def build_treeview(parent, columns, col_labels, heights=15):
    """Создать стилизованный Treeview (таблицу)."""
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        'Custom.Treeview.Heading',
        background=CFG['colors']['bg_treeview_heading'],
        foreground=CFG['colors']['fg_treeview_heading'],
        font=get_font()
    )
    style.configure(
        'Custom.Treeview',
        background=CFG['colors']['bg_table_odd'],
        rowheight=22,
        fieldbackground=CFG['colors']['bg_table_odd']
    )

    tv = ttk.Treeview(
        parent, columns=columns,
        show='headings', height=heights,
        style='Custom.Treeview'
    )
    for col, label in zip(columns, col_labels):
        tv.heading(col, text=label)
        tv.column(col, anchor='center', width=130)

    sb_y = ttk.Scrollbar(parent, orient='vertical', command=tv.yview)
    sb_x = ttk.Scrollbar(parent, orient='horizontal', command=tv.xview)
    tv.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

    tv.grid(row=0, column=0, sticky='nsew')
    sb_y.grid(row=0, column=1, sticky='ns')
    sb_x.grid(row=1, column=0, sticky='ew')
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)
    return tv


def refresh_treeview(tv, df):
    """Обновить содержимое Treeview данными из DataFrame."""
    for item in tv.get_children():
        tv.delete(item)
    for i, row in df.iterrows():
        tag = 'odd' if i % 2 == 0 else 'even'
        tv.insert('', 'end', values=list(row), tags=(tag,))
    tv.tag_configure('odd', background=CFG['colors']['bg_table_odd'])
    tv.tag_configure('even', background=CFG['colors']['bg_table_even'])


# ──────────────────────────────────────────────────────────────
# Окно справочника ТОВАРЫ
# ──────────────────────────────────────────────────────────────

def open_products_window(root):
    """Открыть окно управления справочником «Товары»."""
    global DF_PRODUCTS
    win = tk.Toplevel(root)
    win.title('Справочник: Товары')
    win.configure(bg=CFG['colors']['bg_main'])
    win.geometry('820x520')

    cols = ['ID_товара', 'Наименование', 'Категория', 'Цена']
    labels = ['ID', 'Наименование', 'Категория', 'Цена (руб.)']

    frame_tv = tk.Frame(win, bg=CFG['colors']['bg_main'])
    frame_tv.pack(fill='both', expand=True, padx=10, pady=10)
    tv = build_treeview(frame_tv, cols, labels)
    refresh_treeview(tv, DF_PRODUCTS)

    frame_btns = tk.Frame(win, bg=CFG['colors']['bg_main'])
    frame_btns.pack(fill='x', padx=10, pady=5)

    def on_add():
        _product_dialog(win, tv, mode='add')

    def on_edit():
        sel = tv.selection()
        if not sel:
            messagebox.showwarning('Предупреждение', 'Выберите товар для редактирования.', parent=win)
            return
        _product_dialog(win, tv, mode='edit', iid=sel[0])

    def on_delete():
        global DF_PRODUCTS, DF_REVIEWS
        sel = tv.selection()
        if not sel:
            messagebox.showwarning('Предупреждение', 'Выберите товар для удаления.', parent=win)
            return
        pid = int(tv.item(sel[0], 'values')[0])
        if not messagebox.askyesno('Подтверждение', f'Удалить товар ID={pid} и все его отзывы?', parent=win):
            return
        mask_p = DF_PRODUCTS['ID_товара'] != pid
        mask_r = DF_REVIEWS['ID_товара'] != pid
        DF_PRODUCTS = DF_PRODUCTS[mask_p].reset_index(drop=True)
        DF_REVIEWS = DF_REVIEWS[mask_r].reset_index(drop=True)
        save_data()
        refresh_treeview(tv, DF_PRODUCTS)

    styled_btn(frame_btns, 'Добавить', on_add).pack(side='left', padx=4)
    styled_btn(frame_btns, 'Редактировать', on_edit).pack(side='left', padx=4)
    styled_btn(frame_btns, 'Удалить', on_delete).pack(side='left', padx=4)


def _product_dialog(parent, tv, mode='add', iid=None):
    """Диалоговое окно добавления / редактирования товара."""
    global DF_PRODUCTS
    dlg = tk.Toplevel(parent)
    title = 'Добавить товар' if mode == 'add' else 'Редактировать товар'
    dlg.title(title)
    dlg.configure(bg=CFG['colors']['bg_frame'])
    dlg.resizable(False, False)

    fields = ['Наименование', 'Категория', 'Цена']
    entries = {}
    defaults = {}

    if mode == 'edit' and iid:
        vals = tv.item(iid, 'values')
        defaults = {'Наименование': vals[1], 'Категория': vals[2], 'Цена': vals[3]}

    for i, field in enumerate(fields):
        tk.Label(dlg, text=field + ':', bg=CFG['colors']['bg_frame'], font=get_font()).grid(row=i, column=0, sticky='e', padx=10, pady=6)
        if field == 'Категория':
            var = tk.StringVar(value=defaults.get(field, af.CATEGORIES[0]))
            cb = ttk.Combobox(dlg, textvariable=var, values=af.CATEGORIES, state='readonly')
            cb.grid(row=i, column=1, padx=10, pady=6, sticky='ew')
            entries[field] = var
        else:
            var = tk.StringVar(value=defaults.get(field, ''))
            ent = tk.Entry(dlg, textvariable=var, bg=CFG['colors']['bg_entry'], fg=CFG['colors']['fg_entry'], font=get_font())
            ent.grid(row=i, column=1, padx=10, pady=6, sticky='ew')
            entries[field] = var

    def on_save():
        global DF_PRODUCTS
        name = entries['Наименование'].get().strip()
        cat = entries['Категория'].get().strip()
        try:
            price = float(entries['Цена'].get().replace(',', '.'))
        except ValueError:
            messagebox.showerror('Ошибка', 'Цена должна быть числом.', parent=dlg)
            return
        if not name:
            messagebox.showerror('Ошибка', 'Введите наименование.', parent=dlg)
            return

        if mode == 'add':
            new_id = af.get_next_product_id(DF_PRODUCTS)
            row = pd.DataFrame([{'ID_товара': new_id, 'Наименование': name, 'Категория': cat, 'Цена': price}])
            DF_PRODUCTS = pd.concat([DF_PRODUCTS, row], ignore_index=True)
        else:
            pid = int(tv.item(iid, 'values')[0])
            mask = DF_PRODUCTS['ID_товара'] == pid
            DF_PRODUCTS.loc[mask, ['Наименование', 'Категория', 'Цена']] = [name, cat, price]

        save_data()
        refresh_treeview(tv, DF_PRODUCTS)
        dlg.destroy()

    styled_btn(dlg, 'Сохранить', on_save).grid(row=len(fields), column=0, columnspan=2, pady=10)


# ──────────────────────────────────────────────────────────────
# Окно справочника ОТЗЫВЫ
# ──────────────────────────────────────────────────────────────

def open_reviews_window(root):
    """Открыть окно управления справочником «Отзывы»."""
    global DF_REVIEWS
    win = tk.Toplevel(root)
    win.title('Справочник: Отзывы')
    win.configure(bg=CFG['colors']['bg_main'])
    win.geometry('900x540')

    cols = ['ID_отзыва', 'ID_товара', 'Оценка', 'Тональность', 'Длина_отзыва']
    labels = ['ID отзыва', 'ID товара', 'Оценка', 'Тональность', 'Длина (слов)']

    frame_tv = tk.Frame(win, bg=CFG['colors']['bg_main'])
    frame_tv.pack(fill='both', expand=True, padx=10, pady=10)
    tv = build_treeview(frame_tv, cols, labels)
    refresh_treeview(tv, DF_REVIEWS)

    frame_btns = tk.Frame(win, bg=CFG['colors']['bg_main'])
    frame_btns.pack(fill='x', padx=10, pady=5)

    def on_add():
        _review_dialog(win, tv, mode='add')

    def on_edit():
        sel = tv.selection()
        if not sel:
            messagebox.showwarning('Предупреждение', 'Выберите отзыв.', parent=win)
            return
        _review_dialog(win, tv, mode='edit', iid=sel[0])

    def on_delete():
        global DF_REVIEWS
        sel = tv.selection()
        if not sel:
            messagebox.showwarning('Предупреждение', 'Выберите отзыв.', parent=win)
            return
        rid = int(tv.item(sel[0], 'values')[0])
        if not messagebox.askyesno('Подтверждение', f'Удалить отзыв ID={rid}?', parent=win):
            return
        mask = DF_REVIEWS['ID_отзыва'] != rid
        DF_REVIEWS = DF_REVIEWS[mask].reset_index(drop=True)
        save_data()
        refresh_treeview(tv, DF_REVIEWS)

    styled_btn(frame_btns, 'Добавить', on_add).pack(side='left', padx=4)
    styled_btn(frame_btns, 'Редактировать', on_edit).pack(side='left', padx=4)
    styled_btn(frame_btns, 'Удалить', on_delete).pack(side='left', padx=4)


def _review_dialog(parent, tv, mode='add', iid=None):
    """Диалоговое окно добавления / редактирования отзыва."""
    global DF_REVIEWS
    dlg = tk.Toplevel(parent)
    title = 'Добавить отзыв' if mode == 'add' else 'Редактировать отзыв'
    dlg.title(title)
    dlg.configure(bg=CFG['colors']['bg_frame'])
    dlg.resizable(False, False)

    product_options = [f"{r['ID_товара']} — {r['Наименование']}" for _, r in DF_PRODUCTS.iterrows()]

    defaults = {}
    if mode == 'edit' and iid:
        vals = tv.item(iid, 'values')
        defaults = {'pid': vals[1], 'score': vals[2], 'sent': vals[3], 'length': vals[4]}

    tk.Label(dlg, text='Товар:', bg=CFG['colors']['bg_frame'], font=get_font()).grid(row=0, column=0, sticky='e', padx=10, pady=6)
    pid_var = tk.StringVar()
    if mode == 'edit':
        pid_str = defaults.get('pid', '')
        matched = next((o for o in product_options if o.startswith(str(pid_str))), product_options[0])
        pid_var.set(matched)
    else:
        pid_var.set(product_options[0] if product_options else '')
    ttk.Combobox(dlg, textvariable=pid_var, values=product_options, state='readonly', width=35).grid(row=0, column=1, padx=10, pady=6)

    tk.Label(dlg, text='Оценка (1–5):', bg=CFG['colors']['bg_frame'], font=get_font()).grid(row=1, column=0, sticky='e', padx=10, pady=6)
    score_var = tk.StringVar(value=defaults.get('score', '5'))
    ttk.Combobox(dlg, textvariable=score_var, values=['1', '2', '3', '4', '5'], state='readonly').grid(row=1, column=1, padx=10, pady=6, sticky='w')

    tk.Label(dlg, text='Тональность:', bg=CFG['colors']['bg_frame'], font=get_font()).grid(row=2, column=0, sticky='e', padx=10, pady=6)
    sent_var = tk.StringVar(value=defaults.get('sent', af.SENTIMENTS[0]))
    ttk.Combobox(dlg, textvariable=sent_var, values=af.SENTIMENTS, state='readonly').grid(row=2, column=1, padx=10, pady=6, sticky='w')

    tk.Label(dlg, text='Длина (слов):', bg=CFG['colors']['bg_frame'], font=get_font()).grid(row=3, column=0, sticky='e', padx=10, pady=6)
    len_var = tk.StringVar(value=defaults.get('length', '50'))
    tk.Entry(dlg, textvariable=len_var, bg=CFG['colors']['bg_entry'], fg=CFG['colors']['fg_entry'], font=get_font()).grid(row=3, column=1, padx=10, pady=6, sticky='ew')

    def on_save():
        global DF_REVIEWS
        pid_raw = pid_var.get().split('—')[0].strip()
        try:
            pid = int(pid_raw)
            score = int(score_var.get())
            length = int(len_var.get())
        except ValueError:
            messagebox.showerror('Ошибка', 'Проверьте введённые данные.', parent=dlg)
            return
        sent = sent_var.get()

        if mode == 'add':
            new_id = af.get_next_review_id(DF_REVIEWS)
            row = pd.DataFrame([{'ID_отзыва': new_id, 'ID_товара': pid, 'Оценка': score, 'Тональность': sent, 'Длина_отзыва': length}])
            DF_REVIEWS = pd.concat([DF_REVIEWS, row], ignore_index=True)
        else:
            rid = int(tv.item(iid, 'values')[0])
            mask = DF_REVIEWS['ID_отзыва'] == rid
            DF_REVIEWS.loc[mask, ['ID_товара', 'Оценка', 'Тональность', 'Длина_отзыва']] = [pid, score, sent, length]

        save_data()
        refresh_treeview(tv, DF_REVIEWS)
        dlg.destroy()

    styled_btn(dlg, 'Сохранить', on_save).grid(row=4, column=0, columnspan=2, pady=10)


# ──────────────────────────────────────────────────────────────
# Окна отчётов
# ──────────────────────────────────────────────────────────────

def open_report_filtered(root):
    """Открыть окно отчёта «Список товаров с оценками»."""
    win = tk.Toplevel(root)
    win.title('Отчёт: Товары с оценками')
    win.configure(bg=CFG['colors']['bg_main'])
    win.geometry('860x560')

    cats = ['Все'] + sorted(DF_PRODUCTS['Категория'].unique().tolist())
    cat_var = tk.StringVar(value='Все')

    top = tk.Frame(win, bg=CFG['colors']['bg_main'])
    top.pack(fill='x', padx=10, pady=6)
    tk.Label(top, text='Категория:', bg=CFG['colors']['bg_main'], font=get_font()).pack(side='left')
    ttk.Combobox(top, textvariable=cat_var, values=cats, state='readonly', width=20).pack(side='left', padx=6)

    frame_tv = tk.Frame(win, bg=CFG['colors']['bg_main'])
    frame_tv.pack(fill='both', expand=True, padx=10, pady=4)
    cols = ['ID_товара', 'Наименование', 'Категория', 'Цена', 'Средняя_оценка']
    labels = ['ID', 'Наименование', 'Категория', 'Цена', 'Ср. оценка']
    tv = build_treeview(frame_tv, cols, labels)

    result_holder = [None]

    def on_build():
        text, df = af.report_filtered_products(DF_PRODUCTS, DF_REVIEWS, cat_var.get())
        refresh_treeview(tv, df)
        result_holder[0] = text

    def on_save():
        if result_holder[0] is None:
            messagebox.showwarning('', 'Сначала постройте отчёт.', parent=win)
            return
        path = filedialog.asksaveasfilename(parent=win, defaultextension='.txt', initialdir=OUTPUT_DIR, title='Сохранить отчёт', filetypes=[('Текстовый файл', '*.txt')])
        if path:
            utils.save_text_report(result_holder[0], path)
            messagebox.showinfo('Готово', f'Отчёт сохранён:\n{path}', parent=win)

    btns = tk.Frame(win, bg=CFG['colors']['bg_main'])
    btns.pack(fill='x', padx=10, pady=4)
    styled_btn(btns, 'Построить', on_build).pack(side='left', padx=4)
    styled_btn(btns, 'Сохранить в файл', on_save).pack(side='left', padx=4)
    on_build()


def open_report_stats(root):
    """Открыть окно статистического отчёта."""
    win = tk.Toplevel(root)
    win.title('Отчёт: Статистика')
    win.configure(bg=CFG['colors']['bg_main'])
    win.geometry('860x600')

    text_widget = tk.Text(win, font=('Courier New', 10), bg=CFG['colors']['bg_entry'], fg=CFG['colors']['fg_main'], wrap='none')
    sb_y = ttk.Scrollbar(win, orient='vertical', command=text_widget.yview)
    sb_x = ttk.Scrollbar(win, orient='horizontal', command=text_widget.xview)
    text_widget.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
    text_widget.pack(fill='both', expand=True, padx=10, pady=10)
    sb_y.pack(side='right', fill='y')
    sb_x.pack(side='bottom', fill='x')

    result_holder = [None]

    def on_build():
        text, _ = af.report_statistics(DF_PRODUCTS, DF_REVIEWS)
        result_holder[0] = text
        text_widget.config(state='normal')
        text_widget.delete('1.0', 'end')
        text_widget.insert('end', text)
        text_widget.config(state='disabled')

    def on_save():
        if result_holder[0] is None:
            messagebox.showwarning('', 'Сначала постройте отчёт.', parent=win)
            return
        path = filedialog.asksaveasfilename(parent=win, defaultextension='.txt', initialdir=OUTPUT_DIR, title='Сохранить', filetypes=[('Текст', '*.txt')])
        if path:
            utils.save_text_report(result_holder[0], path)
            messagebox.showinfo('Готово', f'Сохранено:\n{path}', parent=win)

    btns = tk.Frame(win, bg=CFG['colors']['bg_main'])
    btns.pack(fill='x', padx=10, pady=4)
    styled_btn(btns, 'Построить', on_build).pack(side='left', padx=4)
    styled_btn(btns, 'Сохранить в файл', on_save).pack(side='left', padx=4)
    on_build()


def open_report_pivot(root):
    """Открыть окно отчёта «Сводная таблица»."""
    win = tk.Toplevel(root)
    win.title('Отчёт: Сводная таблица')
    win.configure(bg=CFG['colors']['bg_main'])
    win.geometry('860x580')

    qual_opts = ['Тональность', 'Категория']
    val_opts = ['Оценка', 'Цена', 'Длина_отзыва']
    agg_opts = ['mean', 'sum', 'count', 'min', 'max']

    top = tk.Frame(win, bg=CFG['colors']['bg_main'])
    top.pack(fill='x', padx=10, pady=6)

    def lbl(text):
        return tk.Label(top, text=text, bg=CFG['colors']['bg_main'], font=get_font())

    row_var = tk.StringVar(value='Категория')
    col_var = tk.StringVar(value='Тональность')
    val_var = tk.StringVar(value='Оценка')
    agg_var = tk.StringVar(value='mean')

    params = [('Строки:', row_var, qual_opts), ('Столбцы:', col_var, qual_opts), ('Значение:', val_var, val_opts), ('Агрегация:', agg_var, agg_opts)]
    for i, (text, var, opts) in enumerate(params):
        lbl(text).grid(row=0, column=i * 2, padx=4)
        ttk.Combobox(top, textvariable=var, values=opts, state='readonly', width=14).grid(row=0, column=i * 2 + 1, padx=4)

    text_widget = tk.Text(win, font=('Courier New', 10), bg=CFG['colors']['bg_entry'], fg=CFG['colors']['fg_main'], wrap='none')
    text_widget.pack(fill='both', expand=True, padx=10, pady=6)

    result_holder = [None]

    def on_build():
        if row_var.get() == col_var.get():
            messagebox.showerror('Ошибка', 'Строки и столбцы должны быть разными.', parent=win)
            return
        text, _ = af.report_pivot(DF_PRODUCTS, DF_REVIEWS, row_var.get(), col_var.get(), val_var.get(), agg_var.get())
        result_holder[0] = text
        text_widget.config(state='normal')
        text_widget.delete('1.0', 'end')
        text_widget.insert('end', text)
        text_widget.config(state='disabled')

    def on_save():
        if result_holder[0] is None:
            messagebox.showwarning('', 'Сначала постройте отчёт.', parent=win)
            return
        path = filedialog.asksaveasfilename(parent=win, defaultextension='.txt', initialdir=OUTPUT_DIR, title='Сохранить', filetypes=[('Текст', '*.txt')])
        if path:
            utils.save_text_report(result_holder[0], path)
            messagebox.showinfo('Готово', f'Сохранено:\n{path}', parent=win)

    btns = tk.Frame(win, bg=CFG['colors']['bg_main'])
    btns.pack(fill='x', padx=10, pady=4)
    styled_btn(btns, 'Построить', on_build).pack(side='left', padx=4)
    styled_btn(btns, 'Сохранить', on_save).pack(side='left', padx=4)


def _open_chart_window(root, title, build_func, save_name):
    """Открыть универсальное окно графического отчёта."""
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg=CFG['colors']['bg_main'])
    win.geometry('850x560')

    fig_holder = [None]

    frame_chart = tk.Frame(win, bg=CFG['colors']['bg_main'])
    frame_chart.pack(fill='both', expand=True, padx=10, pady=10)

    def on_build():
        fig = build_func(save_path=None)
        fig_holder[0] = fig
        for widget in frame_chart.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def on_save():
        if fig_holder[0] is None:
            messagebox.showwarning('', 'Сначала постройте отчёт.', parent=win)
            return
        path = filedialog.asksaveasfilename(parent=win, defaultextension='.png', initialdir=GRAPHICS_DIR, initialfile=save_name, title='Сохранить PNG', filetypes=[('PNG', '*.png')])
        if path:
            fig_holder[0].savefig(path, dpi=150, bbox_inches='tight')
            messagebox.showinfo('Готово', f'График сохранён:\n{path}', parent=win)

    btns = tk.Frame(win, bg=CFG['colors']['bg_main'])
    btns.pack(fill='x', padx=10, pady=4)
    styled_btn(btns, 'Построить', on_build).pack(side='left', padx=4)
    styled_btn(btns, 'Сохранить PNG', on_save).pack(side='left', padx=4)


def open_report_bar(root):
    """Открыть окно «Кластеризованная столбчатая диаграмма»."""
    win_cfg = tk.Toplevel(root)
    win_cfg.title('График: Столбчатая диаграмма')
    win_cfg.configure(bg=CFG['colors']['bg_main'])
    win_cfg.resizable(False, False)

    qual_opts = ['Категория', 'Тональность']
    q1_var = tk.StringVar(value='Категория')
    q2_var = tk.StringVar(value='Тональность')

    tk.Label(win_cfg, text='Ось X (группы):', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=0, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=q1_var, values=qual_opts, state='readonly').grid(row=0, column=1, padx=10, pady=8)
    tk.Label(win_cfg, text='Цвет (кластер):', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=1, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=q2_var, values=qual_opts, state='readonly').grid(row=1, column=1, padx=10, pady=8)

    def on_ok():
        v1, v2 = q1_var.get(), q2_var.get()
        win_cfg.destroy()
        def build(save_path=None):
            return af.plot_clustered_bar(DF_PRODUCTS, DF_REVIEWS, v1, v2, save_path)
        _open_chart_window(root, 'Кластеризованная столбчатая диаграмма', build, 'bar_chart.png')

    styled_btn(win_cfg, 'Построить', on_ok).grid(row=2, column=0, columnspan=2, pady=10)


def open_report_hist(root):
    """Открыть окно «Категоризированная гистограмма»."""
    win_cfg = tk.Toplevel(root)
    win_cfg.title('График: Гистограмма')
    win_cfg.configure(bg=CFG['colors']['bg_main'])
    win_cfg.resizable(False, False)

    quant_opts = ['Оценка', 'Цена', 'Длина_отзыва']
    qual_opts = ['Категория', 'Тональность']
    q_var = tk.StringVar(value='Оценка')
    g_var = tk.StringVar(value='Категория')

    tk.Label(win_cfg, text='Количественный атрибут:', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=0, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=q_var, values=quant_opts, state='readonly').grid(row=0, column=1, padx=10, pady=8)
    tk.Label(win_cfg, text='Категории (цвет):', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=1, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=g_var, values=qual_opts, state='readonly').grid(row=1, column=1, padx=10, pady=8)

    def on_ok():
        vq, vg = q_var.get(), g_var.get()
        win_cfg.destroy()
        def build(save_path=None):
            return af.plot_categorized_hist(DF_PRODUCTS, DF_REVIEWS, vq, vg, save_path)
        _open_chart_window(root, 'Категоризированная гистограмма', build, 'histogram.png')

    styled_btn(win_cfg, 'Построить', on_ok).grid(row=2, column=0, columnspan=2, pady=10)


def open_report_box(root):
    """Открыть окно «Диаграмма Бокса-Вискера»."""
    win_cfg = tk.Toplevel(root)
    win_cfg.title('График: Бокс-Вискер')
    win_cfg.configure(bg=CFG['colors']['bg_main'])
    win_cfg.resizable(False, False)

    quant_opts = ['Оценка', 'Цена', 'Длина_отзыва']
    qual_opts = ['Категория', 'Тональность']
    q_var = tk.StringVar(value='Оценка')
    g_var = tk.StringVar(value='Категория')

    tk.Label(win_cfg, text='Количественный атрибут:', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=0, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=q_var, values=quant_opts, state='readonly').grid(row=0, column=1, padx=10)
    tk.Label(win_cfg, text='Категории:', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=1, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=g_var, values=qual_opts, state='readonly').grid(row=1, column=1, padx=10)

    def on_ok():
        vq, vg = q_var.get(), g_var.get()
        win_cfg.destroy()
        def build(save_path=None):
            return af.plot_boxplot(DF_PRODUCTS, DF_REVIEWS, vq, vg, save_path)
        _open_chart_window(root, 'Диаграмма Бокса-Вискера', build, 'boxplot.png')

    styled_btn(win_cfg, 'Построить', on_ok).grid(row=2, column=0, columnspan=2, pady=10)


def open_report_scatter(root):
    """Открыть окно «Диаграмма рассеивания»."""
    win_cfg = tk.Toplevel(root)
    win_cfg.title('График: Диаграмма рассеивания')
    win_cfg.configure(bg=CFG['colors']['bg_main'])
    win_cfg.resizable(False, False)

    quant_opts = ['Оценка', 'Цена', 'Длина_отзыва']
    qual_opts = ['Категория', 'Тональность']
    x_var = tk.StringVar(value='Цена')
    y_var = tk.StringVar(value='Оценка')
    c_var = tk.StringVar(value='Тональность')

    tk.Label(win_cfg, text='Ось X:', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=0, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=x_var, values=quant_opts, state='readonly').grid(row=0, column=1, padx=10)
    tk.Label(win_cfg, text='Ось Y:', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=1, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=y_var, values=quant_opts, state='readonly').grid(row=1, column=1, padx=10)
    tk.Label(win_cfg, text='Цвет:', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=2, column=0, padx=10, pady=8, sticky='e')
    ttk.Combobox(win_cfg, textvariable=c_var, values=qual_opts, state='readonly').grid(row=2, column=1, padx=10)

    def on_ok():
        vx, vy, vc = x_var.get(), y_var.get(), c_var.get()
        win_cfg.destroy()
        def build(save_path=None):
            return af.plot_scatter(DF_PRODUCTS, DF_REVIEWS, vx, vy, vc, save_path)
        _open_chart_window(root, 'Диаграмма рассеивания', build, 'scatter.png')

    styled_btn(win_cfg, 'Построить', on_ok).grid(row=3, column=0, columnspan=2, pady=10)


def open_settings(root):
    """Открыть окно настройки параметров интерфейса."""
    win = tk.Toplevel(root)
    win.title('Настройки интерфейса')
    win.configure(bg=CFG['colors']['bg_main'])
    win.resizable(False, False)

    params = [('bg_main', 'Фон главного окна'), ('bg_button', 'Цвет кнопок'), ('fg_button', 'Текст кнопок'), ('bg_header', 'Цвет заголовка')]
    entries = {}
    for i, (key, label) in enumerate(params):
        tk.Label(win, text=label + ':', bg=CFG['colors']['bg_main'], font=get_font()).grid(row=i, column=0, sticky='e', padx=10, pady=6)
        var = tk.StringVar(value=CFG['colors'][key])
        tk.Entry(win, textvariable=var, bg=CFG['colors']['bg_entry'], font=get_font()).grid(row=i, column=1, padx=10, pady=6)
        entries[key] = var

    def on_save():
        for key, var in entries.items():
            CFG['colors'][key] = var.get()
        cfg_path = os.path.join(BASE_DIR, 'config.ini')
        with open(cfg_path, 'w', encoding='utf-8') as f:
            CFG.write(f)
        messagebox.showinfo('Готово', 'Настройки сохранены. Перезапустите приложение для применения.', parent=win)
        win.destroy()

    styled_btn(win, 'Сохранить', on_save).grid(row=len(params), column=0, columnspan=2, pady=10)


def build_main_window():
    """Создать и запустить главное окно приложения."""
    root = tk.Tk()
    root.title('Анализ отзывов Amazon')
    root.configure(bg=CFG['colors']['bg_main'])
    w = int(CFG['window']['width_main'])
    h = int(CFG['window']['height_main'])
    root.geometry(f'{w}x{h}')

    header = tk.Frame(root, bg=CFG['colors']['bg_header'], height=60)
    header.pack(fill='x')
    tk.Label(header, text='Анализ отзывов Amazon', bg=CFG['colors']['bg_header'], fg=CFG['colors']['fg_header'],
             font=(CFG['fonts']['font_main'], int(CFG['fonts']['font_size_title']), 'bold')).pack(side='left', padx=16, pady=10)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    ref_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='Справочники', menu=ref_menu)
    ref_menu.add_command(label='Товары', command=lambda: open_products_window(root))
    ref_menu.add_command(label='Отзывы', command=lambda: open_reviews_window(root))

    rep_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='Отчёты', menu=rep_menu)
    rep_menu.add_command(label='Товары с оценками', command=lambda: open_report_filtered(root))
    rep_menu.add_command(label='Статистика', command=lambda: open_report_stats(root))
    rep_menu.add_command(label='Сводная таблица', command=lambda: open_report_pivot(root))
    rep_menu.add_separator()
    rep_menu.add_command(label='Столбчатая диаграмма', command=lambda: open_report_bar(root))
    rep_menu.add_command(label='Гистограмма', command=lambda: open_report_hist(root))
    rep_menu.add_command(label='Диаграмма Бокса-Вискера', command=lambda: open_report_box(root))
    rep_menu.add_command(label='Диаграмма рассеивания', command=lambda: open_report_scatter(root))

    menu_bar.add_command(label='Настройки', command=lambda: open_settings(root))

    info_frame = tk.Frame(root, bg=CFG['colors']['bg_frame'], relief='flat', bd=1)
    info_frame.pack(fill='x', padx=16, pady=10)

    def refresh_info():
        for widget in info_frame.winfo_children():
            widget.destroy()
        avg_score = round(DF_REVIEWS['Оценка'].mean(), 2) if not DF_REVIEWS.empty else '—'
        n_cats = DF_PRODUCTS['Категория'].nunique() if not DF_PRODUCTS.empty else 0
        stats = [('Товаров в базе', len(DF_PRODUCTS)), ('Отзывов в базе', len(DF_REVIEWS)), ('Категорий', n_cats), ('Средняя оценка', avg_score)]
        for i, (label, val) in enumerate(stats):
            cell = tk.Frame(info_frame, bg='#000000', padx=20, pady=10)
            cell.grid(row=0, column=i, padx=6, pady=6)
            tk.Label(cell, text=str(val), bg='#000000', fg='#FFFFFF', font=(CFG['fonts']['font_main'], 18, 'bold')).pack()
            tk.Label(cell, text=label, bg='#000000', fg='#FFFFFF', font=get_font()).pack()

    refresh_info()

    ref_frame = tk.LabelFrame(root, text='Справочники', bg=CFG['colors']['bg_main'], fg=CFG['colors']['fg_main'], font=get_font())
    ref_frame.pack(fill='x', padx=16, pady=(6, 2))
    for i, (text, cmd) in enumerate([('Товары', lambda: open_products_window(root)), ('Отзывы', lambda: open_reviews_window(root)), ('Настройки', lambda: open_settings(root))]):
        styled_btn(ref_frame, text, cmd).grid(row=0, column=i, padx=8, pady=6)

    rep_frame = tk.LabelFrame(root, text='Отчёты', bg=CFG['colors']['bg_main'], fg=CFG['colors']['fg_main'], font=get_font())
    rep_frame.pack(fill='x', padx=16, pady=(2, 6))
    rep_buttons = [('Товары с оценками', lambda: open_report_filtered(root)), ('Статистика', lambda: open_report_stats(root)),
                   ('Сводная таблица', lambda: open_report_pivot(root)), ('Столбчатая диаграмма', lambda: open_report_bar(root)),
                   ('Гистограмма', lambda: open_report_hist(root)), ('Бокс-Вискер', lambda: open_report_box(root)),
                   ('Рассеивание', lambda: open_report_scatter(root))]
    for i, (text, cmd) in enumerate(rep_buttons):
        styled_btn(rep_frame, text, cmd).grid(row=i // 4, column=i % 4, padx=8, pady=6)

    status_var = tk.StringVar(value=f'База данных загружена. Товаров: {len(DF_PRODUCTS)}, отзывов: {len(DF_REVIEWS)}')
    status_bar = tk.Label(root, textvariable=status_var, anchor='w', bg='#000000', fg='#FFFFFF', font=get_font())
    status_bar.pack(side='bottom', fill='x')

    root.mainloop()


if __name__ == '__main__':
    init_app()
    build_main_window()