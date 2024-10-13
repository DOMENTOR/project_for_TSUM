import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import shutil
import os
# import threading
try:
    from parsing.instagram_parser.parser import __main__ as instagram_main
    from parsing.telegram_parser.parser import __main__ as telegram_main
    from parsing.instagram_parser import config as insta_config
    from parsing.telegram_parser import config as tg_config
except ImportError:
    from instagram_parser.parser import __main__ as instagram_main
    from telegram_parser.parser import __main__ as telegram_main
    from instagram_parser import config as insta_config
    from telegram_parser import config as tg_config

# Функция для скачивания готового шаблона Excel
def download_excel_template():
    try:
        # Указываем путь к шаблону
        template_path = os.path.join('parsing', 'template.xlsx')

        # Диалог для выбора места сохранения файла с предзаполненным именем
        download_location = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="template.xlsx"  # Имя файла по умолчанию
        )
        
        if download_location:
            # Копируем шаблон на выбранный путь
            shutil.copy(template_path, download_location)
            messagebox.showinfo("Успешно", "Шаблон Excel успешно скачан!")
        else:
            messagebox.showwarning("Отмена", "Операция скачивания отменена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось скачать шаблон: {e}")

# Функция для загрузки списка из Excel
def load_from_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        try:
            data = pd.read_excel(file_path)
            insta_channels = data['insta_channels'].dropna().drop_duplicates().tolist()
            if insta_channels is not None:
                print(f'Список Instagram аккаунтов: {', '.join(insta_channels)}')
            tg_channels = data['tg_channels'].dropna().drop_duplicates().tolist()
            if tg_channels is not None:
                print(f'Список Telegram аккаунтов: {', '.join(tg_channels)}')
            return insta_channels, tg_channels
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    return [], []

# Функция для запуска парсинга Telegram
def start_telegram_only(telegram_channels, post_limit_tg, use_proxy_var_tg):
    tg_config.TELEGRAM_CHANNELS = telegram_channels
    tg_config.POST_LIMIT = post_limit_tg
    tg_config.USE_PROXY = use_proxy_var_tg.get()
    telegram_main()

# Функция для запуска парсинга Instagram
def start_instagram_only(instagram_accounts, post_limit_inst, use_proxy_var_inst):
    insta_config.INSTAGRAM_PROFILES = instagram_accounts
    insta_config.POST_LIMIT = post_limit_inst
    insta_config.USE_PROXY = use_proxy_var_inst.get()
    instagram_main()

# Функция для полного парсинга (Telegram + Instagram)
def start_full_parsing(telegram_channels, instagram_accounts, post_limit_tg, post_limit_inst, use_proxy_var_tg, use_proxy_var_inst):
    start_telegram_only(telegram_channels, post_limit_tg, use_proxy_var_tg)
    start_instagram_only(instagram_accounts, post_limit_inst, use_proxy_var_inst)

# GUI (Graphical User Interface)
def create_gui():
    root = tk.Tk()
    root.title("Парсер для Instagram и Telegram")
    root.geometry("400x400")

    # Создаём переменные use_proxy_var_inst и use_proxy_var_tg после инициализации root
    global use_proxy_var_inst, use_proxy_var_tg
    use_proxy_var_inst = tk.BooleanVar()
    use_proxy_var_tg = tk.BooleanVar()

    # Кнопка для скачивания шаблона Excel
    tk.Button(root, text="Скачать шаблон Excel", command=download_excel_template).grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    # Кнопка для загрузки списка каналов из Excel
    tk.Button(root, text="Загрузить список из Excel", command=load_channels_from_excel).grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    # Поле для ввода количества постов для Telegram
    tk.Label(root, text="Количество постов для Telegram:").grid(row=2, column=0, padx=10, sticky="w")
    global post_limit_tg_entry
    post_limit_tg_entry = tk.Entry(root, width=10)
    post_limit_tg_entry.grid(row=2, column=1, padx=10)
    post_limit_tg_entry.insert(0, "5")

    # Поле для ввода количества постов для Instagram
    tk.Label(root, text="Количество постов для Instagram:").grid(row=3, column=0, padx=10, sticky="w")
    global post_limit_inst_entry
    post_limit_inst_entry = tk.Entry(root, width=10)
    post_limit_inst_entry.grid(row=3, column=1, padx=10)
    post_limit_inst_entry.insert(0, "5")

    # Флажок для выбора использования прокси TG
    proxy_checkbox_tg = tk.Checkbutton(root, text="Использовать прокси TG", variable=use_proxy_var_tg)
    proxy_checkbox_tg.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky="w")

    # Флажок для выбора использования прокси Inst
    proxy_checkbox_inst = tk.Checkbutton(root, text="Использовать прокси Inst", variable=use_proxy_var_inst)
    proxy_checkbox_inst.grid(row=5, column=0, columnspan=2, pady=5, padx=10, sticky="w")

    # Кнопка для запуска парсинга только Telegram
    tk.Button(root, text="Запустить парсинг Telegram", command=lambda: start_telegram_only(tg_channels, int(post_limit_tg_entry.get()), use_proxy_var_tg)).grid(row=6, column=0, pady=10, padx=10, sticky="ew")

    # Кнопка для запуска парсинга только Instagram
    tk.Button(root, text="Запустить парсинг Instagram", command=lambda: start_instagram_only(insta_channels, int(post_limit_inst_entry.get()), use_proxy_var_inst)).grid(row=7, column=0, pady=10, padx=10, sticky="ew")

    # Кнопка для запуска полного парсинга (Telegram + Instagram)
    tk.Button(root, text="Полный парсинг (Telegram + Instagram)", command=lambda: start_full_parsing(tg_channels, insta_channels, int(post_limit_tg_entry.get()), int(post_limit_inst_entry.get()), use_proxy_var_tg, use_proxy_var_inst)).grid(row=8, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    root.mainloop()



# Функция для загрузки каналов из Excel и сохранения в переменные
def load_channels_from_excel():
    global insta_channels, tg_channels
    insta_channels, tg_channels = load_from_excel()
    if not insta_channels and not tg_channels:
        messagebox.showinfo("Информация", "Ни одного канала не указано для парсинга.")

# Функция для подсчёта JSON и медиафайлов
def count_files():
    insta_folder = 'instagram_parser/data'
    tg_folder = 'telegram_parser/data'

    insta_json_count, insta_media_count = count_directory_files(insta_folder)
    tg_json_count, tg_media_count = count_directory_files(tg_folder)

    messagebox.showinfo(
        "Результаты",
        f"Instagram: JSON файлов - {insta_json_count}, Медиафайлов - {insta_media_count}\n"
        f"Telegram: JSON файлов - {tg_json_count}, Медиафайлов - {tg_media_count}"
    )

# Функция для подсчёта файлов в директории
def count_directory_files(folder):
    json_count = 0
    media_count = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.json'):
                json_count += 1
            elif file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                media_count += 1
    return json_count, media_count

if __name__ == "__main__":
    insta_channels, tg_channels = [], []
    create_gui()
