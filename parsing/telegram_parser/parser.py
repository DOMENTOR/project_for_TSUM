import os
import json
import logging
import time
from urllib.parse import urlparse
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from datetime import datetime
try:
    from parsing.telegram_parser import config
except ImportError:
    try:
        from telegram_parser import config
    except ImportError:
        import config


# Настройка логирования (когда скрипт запускается напрямую)
logging.basicConfig(
    filename=config.LOG_FILE,
    level=getattr(logging, config.LOGGING_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('telegram_bot_parser')
logger.info('Логгер инициализирован.')

# Убедитесь, что существует папка для хранения данных
os.makedirs(config.DATA_FOLDER, exist_ok=True)

# Обновляем путь к файлу сессии
session_file = os.path.join('parsing', 'telegram_parser', 'session_name')

def parse_proxy_url(proxy_url):
    result = urlparse(proxy_url)
    
    proxy = {
        'proxy_type': result.scheme,
        'username': result.username,
        'password': result.password,
        'addr': result.hostname,
        'port': result.port
    }
    
    return proxy

def prompt_credentials(phone_number_needed=True):
    print('Все необходимые данные можно получить по ссылке https://my.telegram.org/ (нужно создать подключение)')
    api_id = input("Введите ваш API ID: ").strip()
    api_hash = input("Введите ваш API HASH: ").strip()
    if phone_number_needed:
        phone_number = input("Введите ваш номер телефона (в формате +7... без пробелов и знаков препинания): ").strip()
        return api_id, api_hash, phone_number
    else:
        phone_number = None
        return api_id, api_hash, phone_number

def initialize_client(api_id=None, api_hash=None, phone_number=None, proxy=None):
    session_file = os.path.join('parsing', 'telegram_parser', 'session_name')
    # Проверим, существует ли файл сессии
    if os.path.exists(session_file + '.session'):
        logger.info(f'Файл сессии найден: {session_file}')
        client = TelegramClient(session_file, api_id=api_id, api_hash=api_hash, proxy=proxy)
    else:
        logger.info('Файл сессии не найден. Запрашиваем данные для создания новой сессии.')
        client = TelegramClient(session_file, api_id=api_id, api_hash=api_hash, proxy=proxy)
    client.connect()
    logger.info('Клиент подключен.')

    if not client.is_user_authorized() and phone_number:
        logger.info('Клиент не авторизован. Начинается процесс авторизации.')
        client.send_code_request(phone_number)
        try:
            client.sign_in(phone_number, input('Введите код (придет сообщением в Telegram): '))
        except SessionPasswordNeededError:
            from getpass import getpass
            client.sign_in(password=getpass('Введите пароль: '))
        logger.info('Аутентификация прошла успешно и сессия была сохранена.')
    else:
        logger.info('Клиент уже авторизован.')

    return client

def fetch_channel_messages(client, channel, limit):
    try:
        channel_entity = client.get_entity(channel)
        # Увеличиваем лимит сообщений для получения большего количества
        messages = client.get_messages(channel_entity, limit=limit)
        time.sleep(2)  # Добавляем паузу между запросами
        return messages
    except Exception as e:
        logger.error(f'Ошибка при получении сообщений из канала {channel}: {e}')
        return []

def save_message(client, channel, message, stats):
    channel_folder = os.path.join(config.DATA_FOLDER, channel.strip('@'))
    os.makedirs(channel_folder, exist_ok=True)

    # Фиксируем текст сообщения, с учетом возможных проблем с экранированием
    message_text = message.message if message.message else ''
    if '/' in message_text:
        message_text = message_text.replace('/', '')

    # Проверяем фильтры (если есть)
    if config.CONTENT_FILTERS and not any(filter in message_text for filter in config.CONTENT_FILTERS):
        return

    # Общие данные по сообщению
    message_date = message.date.isoformat() if message.date else ''
    message_views = message.views if hasattr(message, 'views') else 0
    message_forwards = message.forwards if hasattr(message, 'forwards') else 0
    message_reactions = message.reactions.to_dict() if message.reactions else None

    # Обновляем статистику (дата самого старого и самого нового поста)
    post_date = message.date
    if not stats['earliest_post'] or post_date < stats['earliest_post']:
        stats['earliest_post'] = post_date
    if not stats['latest_post'] or post_date > stats['latest_post']:
        stats['latest_post'] = post_date

    # Основная структура для сохранения данных
    message_data = {
        'text': message_text,
        'date': message_date,
        'views': message_views,
        'forwards': message_forwards,
        'reactions': message_reactions,
        'media': []
    }

    media_folder = os.path.join(channel_folder, 'media')
    os.makedirs(media_folder, exist_ok=True)

    # Проверяем, является ли сообщение частью медиа-альбома (используем grouped_id)
    if message.grouped_id:
        # Получаем все сообщения с таким же grouped_id (из альбома)
        grouped_messages = client.get_messages(channel, limit=50)
        media_group = [msg for msg in grouped_messages if msg.grouped_id == message.grouped_id]

        # Обрабатываем все сообщения из альбома
        for msg in media_group:
            if msg.photo:
                media_file = f'{msg.id}.jpg'
                media_path = os.path.join(media_folder, media_file)
                if not os.path.exists(media_path):
                    logger.info(f'Скачиваем {media_file}')
                    print(f'Скачиваем {media_file}')
                    client.download_media(msg.photo, file=media_path)
                message_data['media'].append(media_path)
                stats['media_count'] += 1

            # Объединяем текст, если он есть
            if msg.message and not message_data['text']:
                message_data['text'] = msg.message

            # Объединяем реакции, если они есть
            if msg.reactions and not message_data['reactions']:
                message_data['reactions'] = msg.reactions.to_dict()

    else:
        # Если это одиночное сообщение с медиа
        if message.photo:
            media_file = f'{message.id}.jpg'
            media_path = os.path.join(media_folder, media_file)
            if not os.path.exists(media_path):
                logger.info(f'Скачиваем {media_file}')
                print(f'Скачиваем {media_file}')
                client.download_media(message.photo, file=media_path)
            message_data['media'].append(media_path)
            stats['media_count'] += 1

    # Сохранение информации в JSON файл
    message_file = os.path.join(channel_folder, f'{message.id}.json')

    # Проверка на существование других сообщений с тем же временем или близким (например, в пределах 3 секунд)
    json_files = [f for f in os.listdir(channel_folder) if f.endswith('.json')]
    for json_file in json_files:
        json_path = os.path.join(channel_folder, json_file)
        with open(json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        existing_date = existing_data.get('date', '')
        time_diff = abs((datetime.fromisoformat(existing_date) - message.date).total_seconds())

        if (time_diff <= 3 or existing_data.get('grouped_id') == message.grouped_id):
            existing_data['media'].extend(message_data['media'])
            existing_data['media'] = list(set(existing_data['media']))  # Убираем дубликаты

            if not existing_data['text']:
                existing_data['text'] = message_data['text']

            if not existing_data['reactions']:
                existing_data['reactions'] = message_data['reactions']

            with open(json_path, 'w', encoding='utf-8') as f:
                logger.info(f'Сохраняем {message.id}.json')
                print(f'Сохраняем {message.id}.json')
                json.dump(existing_data, f, ensure_ascii=False, indent=4)

            if os.path.exists(message_file):
                os.remove(message_file)
            return

    with open(message_file, 'w', encoding='utf-8') as f:
        logger.info(f'Сохраняем {message.id}.json')
        print(f'Сохраняем {message.id}.json')
        json.dump(message_data, f, ensure_ascii=False, indent=4)

    stats['post_count'] += 1  # Увеличиваем счетчик постов


def __main__():
    
    # Настройка логирования (когда скрипт запускается из другого файла через вызов __main__())
    logging.basicConfig(
        filename=config.LOG_FILE,
        level=getattr(logging, config.LOGGING_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
        
    logger = logging.getLogger('telegram_bot_parser')
    logger.info('Тестовое сообщение для проверки логгера.')
    
    session_file = os.path.join('parsing', 'telegram_parser', 'session_name')

    if os.path.exists(session_file + '.session'):
        api_id, api_hash, phone_number = prompt_credentials(phone_number_needed=False)
    else:
        api_id, api_hash, phone_number = prompt_credentials(phone_number_needed=True)

    proxy = None
    # Проверяем, нужно ли использовать прокси, исходя из конфигурации
    if getattr(config, 'USE_PROXY', False) and config.PROXY_URL:
        proxy = parse_proxy_url(config.PROXY_URL)
        logger.info(f'Используется прокси (Telegram): {config.PROXY_URL}')
        print(f'Используется прокси (Telegram): {config.PROXY_URL}')
    else:
        logger.info('Прокси не используется (Telegram).')
        print('Прокси не используется (Telegram).')

    try:
        client = initialize_client(api_id, api_hash, phone_number, proxy)
        for channel in config.TELEGRAM_CHANNELS:
            logger.info(f'Начало парсинга канала: {channel}')
            print(f'Начало парсинга канала: {channel}') 
            stats = {
                'post_count': 0,
                'media_count': 0,
                'earliest_post': None,
                'latest_post': None
            }

            messages = fetch_channel_messages(client, channel, config.POST_LIMIT)
            for message in messages:
                save_message(client, channel, message, stats)

            # Логирование результатов
            logger.info(f'Канал: {channel}')
            logger.info(f'Скачано постов: {stats["post_count"]}')
            logger.info(f'Скачано медиафайлов: {stats["media_count"]}')
            logger.info(f'Самый ранний пост: {stats["earliest_post"]}')
            logger.info(f'Самый поздний пост: {stats["latest_post"]}')

            # Вывод в консоль (временно для дебага)
            print(f'Канал: {channel}')
            print(f'Скачано постов: {stats["post_count"]}')
            print(f'Скачано медиафайлов: {stats["media_count"]}')
            print(f'Самый ранний пост: {stats["earliest_post"]}')
            print(f'Самый поздний пост: {stats["latest_post"]}')
            print('-' * 40)

        logger.info(f'Ожидание {config.UPDATE_INTERVAL} секунд до следующего запуска')
        time.sleep(config.UPDATE_INTERVAL)

    except FloodWaitError as e:
        logger.warning(f'Частые запросы. Ожидание {e.seconds} секунд.')
        time.sleep(e.seconds)

    except Exception as e:
        logger.error(f'Неопознанная ошибка: {e}')
        time.sleep(60)



if __name__ == '__main__':
    __main__()
