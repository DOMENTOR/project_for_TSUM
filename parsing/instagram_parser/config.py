# Список Instagram профилей для парсинга
INSTAGRAM_PROFILES = [
    'vogue',
    'gucci',
    'louisvuitton',
    # Добавьте сюда названия профилей для парсинга
]

# Папка для сохранения парсенных данных
DATA_FOLDER = 'parsing/instagram_parser/data'

# Настройки логирования
LOGGING_LEVEL = 'INFO'  # Может быть 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
LOG_FILE = 'parsing/instagram_parser/parsing.log'

# Опциональные настройки прокси (если необходимо)
PROXY_URL = "https://M6TbCp:vWVdTc@217.29.63.40:12504"  # Пример: 'http://proxy.example.com:1234'
PROXY_USERNAME = 'M6TbCp'
PROXY_PASSWORD = 'vWVdTc'

# Интервал обновлений в секундах
UPDATE_INTERVAL = 3600  # Получение обновлений каждые 3600 секунд (каждый час)

# Настройки для входа в Instagram (если необходимо)
INSTAGRAM_USERNAME = 'your_instagram_username'
INSTAGRAM_PASSWORD = 'your_instagram_password'

# Фильтры контента (например: парсить только посты, содержащие определенные ключевые слова)
CONTENT_FILTERS = None  # List, ['fashion', 'style']

# Настройки User-Agent (если необходимо)
USER_AGENT = None  # String, 'InstagramParserBot/1.0 (+https://yourwebsite.com/botinfo)'

# Ограничение количества постов для парсинга (None для снятия ограничения)
POST_LIMIT = 5  # Количество постов, которые нужно парсить с каждого профиля
