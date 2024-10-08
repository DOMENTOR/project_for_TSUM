# Список Telegram каналов для парсинга
TELEGRAM_CHANNELS = [
    'rogov24',
    'mariannaeliseeva',
    'OVECHKIN_NIKOLAY',
    # Добавьте сюда названия или ID каналов
]

# Папка для сохранения парсенных данных
DATA_FOLDER = 'parsing/telegram_parser/data'

# Настройки логирования
LOGGING_LEVEL = 'INFO'  # Может быть 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
LOG_FILE = 'parsing/telegram_parser/parsing.log'

# Опциональные настройки прокси (если необходимо)
PROXY_URL = "https://M6TbCp:vWVdTc@217.29.63.40:12504"  # Пример: 'http://proxy.example.com:1234'
PROXY_USERNAME = 'M6TbCp'
PROXY_PASSWORD = 'vWVdTc'

PROXY = ('http', '217.29.63.40', 12504, 'M6TbCp', 'vWVdTc')

# Интервал обновлений в секундах
UPDATE_INTERVAL = 3600  # Получение обновлений в секундах (каждый час)

# Фильтры контента (например: парсить только сообщения, содержащие определенные ключевые слова)
CONTENT_FILTERS = None # List, ['keyword1', 'keyword2']

# Настройки User-Agent (если необходимо)
USER_AGENT = None # String, 'TelegramParserBot/1.0 (+https://yourwebsite.com/botinfo)'

# Дополнительные настройки API (если необходимо)
API_URL = None # String, 'https://api.telegram.org/bot{}/'.format(TELEGRAM_API_TOKEN)
