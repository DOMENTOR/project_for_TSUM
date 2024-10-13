# classify_config.py

# Путь к лог-файлу для классификации изображений
LOG_FILE_CLASSIFY = "modelling/clothing_detection/classify_images.log"

# Уровень логирования (может быть INFO, DEBUG, WARNING и т.д.)
LOGGING_LEVEL = "INFO"

# Принудительный пересчёт всех скоров (если True, пересчитываются все скоры, даже если они уже существуют)
FORCE_RECALCULATE_SCORES = True # False - default

# Пути к папкам с данными (JSON, внутри папка media с фотографиями)
DATA_FOLDERS = ["parsing/telegram_parser/data", "parsing/instagram_parser/data"]
