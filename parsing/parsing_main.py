import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import shutil
import os
import threading
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

# Функция для запуска парсинга Instagram
def start_instagram(instagram_accounts, post_limit):
    def run():
        insta_config.INSTAGRAM_PROFILES = instagram_accounts
        insta_config.POST_LIMIT = post_limit
        instagram_main()

    threading.Thread(target=run).start()

# Функция для запуска парсинга Telegram
def start_telegram(telegram_channels, post_limit):
    def run():
        tg_config.TELEGRAM_CHANNELS = telegram_channels
        telegram_main()  # Здесь больше не нужно передавать client
    threading.Thread(target=run).start()

# Функция для запуска всего процесса парсинга
def start_parsing():
    # Получение значений из загруженного Excel файла
    post_limit = post_limit_entry.get()  # Получаем количество постов
    if post_limit.isdigit():
        post_limit = int(post_limit)
    else:
        messagebox.showwarning("Ошибка", "Введите корректное число для лимита постов")
        return

    if not insta_channels and not tg_channels:
        messagebox.showwarning("Предупреждение", "Не указаны ни Instagram аккаунты, ни Telegram каналы.")
        return

    # Запуск парсинга Instagram и Telegram в разных потоках
    if insta_channels:
        start_instagram(insta_channels, post_limit)
    
    if tg_channels:
        start_telegram(tg_channels, post_limit)

# Кнопка для запуска парсинга
def create_gui():
    root = tk.Tk()
    root.title("Парсер для Instagram и Telegram")

    # Кнопка для скачивания шаблона Excel
    tk.Button(root, text="Скачать шаблон Excel", command=download_excel_template).grid(row=0, column=0, columnspan=2, pady=10)

    # Кнопка для загрузки списка каналов из Excel
    tk.Button(root, text="Загрузить список из Excel", command=load_channels_from_excel).grid(row=1, column=0, columnspan=2, pady=10)

    # Кнопка для пропуска парсинга
    tk.Button(root, text="Пропустить парсинг", command=count_files).grid(row=2, column=0, columnspan=2, pady=10)

    # Поле для ввода количества постов
    tk.Label(root, text="Количество постов для парсинга:").grid(row=3, column=0)
    global post_limit_entry
    post_limit_entry = tk.Entry(root, width=10)
    post_limit_entry.grid(row=3, column=1)
    post_limit_entry.insert(0, "5")

    # Кнопка для запуска парсинга
    tk.Button(root, text="Запустить парсинг", command=start_parsing).grid(row=4, column=0, columnspan=2, pady=10)

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
