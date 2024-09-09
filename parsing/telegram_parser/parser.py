import os
import json
import logging
import time
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from datetime import datetime
import config

# Настройка логирования
logging.basicConfig(
    filename=config.LOG_FILE,
    level=getattr(logging, config.LOGGING_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('telegram_bot_parser')

# Убедитесь, что существует папка для хранения данных
os.makedirs(config.DATA_FOLDER, exist_ok=True)

def prompt_credentials():
    print('Все необходимые данные можно получить по ссылке https://my.telegram.org/ (нужно создать подключение)')
    api_id = input("Введите ваш API ID: ").strip()
    api_hash = input("Введите ваш API HASH: ").strip()
    phone_number = input("Введите ваш номер телефона (в формате +7... без пробелов и знаков препинания): ").strip()
    return api_id, api_hash, phone_number

def initialize_client(api_id, api_hash, phone_number, proxy=None):
    session_file = 'session_name'
    client = TelegramClient(session_file, api_id, api_hash, proxy=proxy)
    
    if os.path.exists(session_file + '.session'):
        logger.info(f'Файл сессии {session_file}.session существует и будет использован.')
    else:
        logger.info(f'Файл сессии {session_file}.session не найден. Создаем новый.')

    client.connect()
    logger.info('Клиент подключен.')

    if not client.is_user_authorized():
        logger.info('Клиент не авторизован. Начинается процесс авторизации.')
        client.send_code_request(phone_number)
        try:
            client.sign_in(phone_number, input('Введите код (придет сообщением в Telegram, убедитесь, что подключение безопасно): '))
        except SessionPasswordNeededError:
            from getpass import getpass
            client.sign_in(password=getpass('Введите пароль: '))
        logger.info('Аутентификация прошла успешно и сессия была сохранена.')
    else:
        logger.info('Клиент успешно авторизован с использованием сохраненной сессии.')

    return client

def fetch_channel_messages(client, channel):
    try:
        channel_entity = client.get_entity(channel)
        messages = client.get_messages(channel_entity, limit=100)
        return messages
    except Exception as e:
        logger.error(f'Ошибка при получении сообщений из канала {channel}: {e}')
        return []

def save_message(client, channel, message):
    channel_folder = os.path.join(config.DATA_FOLDER, channel.strip('@'))
    os.makedirs(channel_folder, exist_ok=True)

    message_text = message.message if message.message else ''
    if config.CONTENT_FILTERS and not any(filter in message_text for filter in config.CONTENT_FILTERS):
        return

    message_date = message.date.isoformat() if message.date else ''
    message_views = message.views if hasattr(message, 'views') else 0
    message_forwards = message.forwards if hasattr(message, 'forwards') else 0
    message_reactions = message.reactions.to_dict() if message.reactions else None

    message_data = {
        'text': message_text,
        'date': message_date,
        'views': message_views,
        'forwards': message_forwards,
        'reactions': message_reactions,
        'media': []
    }

    if message.photo:
        media_folder = os.path.join(channel_folder, 'media')
        os.makedirs(media_folder, exist_ok=True)
        file_path = client.download_media(message.photo, file=media_folder)
        if file_path:
            message_data['media'].append(file_path)

    if message.media and isinstance(message.media, list):
        for media in message.media:
            if isinstance(media, types.MessageMediaPhoto):
                media_folder = os.path.join(channel_folder, 'media')
                os.makedirs(media_folder, exist_ok=True)
                file_path = client.download_media(media, file=media_folder)
                if file_path:
                    message_data['media'].append(file_path)

    message_file = os.path.join(channel_folder, f'{message.id}.json')
    with open(message_file, 'w', encoding='utf-8') as f:
        json.dump(message_data, f, ensure_ascii=False, indent=4)

def __main__(api_id, api_hash, phone_number, proxy=None):
    logger.debug('Начинаем запрос учетных данных')
    
    client = initialize_client(api_id, api_hash, phone_number, proxy)
    logger.info(f'Успешная авторизация для аккаунта {phone_number}')

    try:
        for channel in config.TELEGRAM_CHANNELS:
            messages = fetch_channel_messages(client, channel)
            for message in messages:
                save_message(client, channel, message)
    finally:
        client.disconnect()
        logger.info(f'Завершено выполнение парсинга для аккаунта {phone_number}')

if __name__ == '__main__':
    api_id, api_hash, phone_number = prompt_credentials()
    
    proxy = None
    if config.PROXY_URL:
        proxy = {
            'proxy_type': 'http',
            'addr': config.PROXY_URL.split(':')[1].strip('//'),
            'port': int(config.PROXY_URL.split(':')[2]),
            'username': config.PROXY_USERNAME,
            'password': config.PROXY_PASSWORD
        }

    try:
        while True:
            client = initialize_client(api_id, api_hash, phone_number, proxy)
            __main__(api_id, api_hash, phone_number, proxy)
            logger.info(f'Ожидание {config.UPDATE_INTERVAL} секунд до следующего запуска')
            time.sleep(config.UPDATE_INTERVAL)
    except FloodWaitError as e:
        logger.warning(f'Частые запросы. Ожидание {e.seconds} секунд.')
        time.sleep(e.seconds)
    except Exception as e:
        logger.error(f'Неопознанная ошибка: {e}')
        time.sleep(60)
