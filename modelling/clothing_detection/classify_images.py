import os
import json
import logging
from config import LOG_FILE_CLASSIFY, LOGGING_LEVEL, FORCE_RECALCULATE_SCORES, DATA_FOLDERS

# Импорты моделей для классификации
try:
    from modelling.clothing_detection.model_utils import classify_image_clip_base, classify_image_clip_large
except ImportError:
    try:
        from clothing_detection.model_utils import classify_image_clip_base, classify_image_clip_large
    except ImportError:
        from model_utils import classify_image_clip_base, classify_image_clip_large

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE_CLASSIFY,
    level=getattr(logging, LOGGING_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def process_json_files():
    """
    Обрабатывает JSON-файлы в указанных директориях, выполняя классификацию изображений на наличие одежды
    с использованием двух моделей CLIP: базовой и большой версии.
    """
    for folder in DATA_FOLDERS:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    
                    logger.info(f"Начало обработки файла {file_path}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        message_data = json.load(f)
                    
                    if "media" in message_data:
                        updated = False  # Флаг для проверки, были ли изменения в JSON

                        # Создание пустых списков для скоров, если они не существуют или нужно пересчитать
                        if "media_clothing_score_CLIP_base" not in message_data or FORCE_RECALCULATE_SCORES:
                            message_data["media_clothing_score_CLIP_base"] = [None] * len(message_data["media"])
                        if "media_clothing_score_CLIP_large" not in message_data or FORCE_RECALCULATE_SCORES:
                            message_data["media_clothing_score_CLIP_large"] = [None] * len(message_data["media"])

                        # Проходим по каждому медиа-файлу
                        for i, media_item in enumerate(message_data['media']):
                            # Проверяем, является ли media_item строкой пути к файлу
                            if isinstance(media_item, str):
                                media_path = media_item
                            elif isinstance(media_item, dict) and "file" in media_item:
                                media_path = media_item["file"]
                            else:
                                continue

                            # Проверяем наличие предыдущих скоров и пересчитываем только если нужно
                            if (
                                not FORCE_RECALCULATE_SCORES and
                                message_data["media_clothing_score_CLIP_base"][i] is not None and
                                message_data["media_clothing_score_CLIP_large"][i] is not None
                            ):
                                logger.info(f"Скоры уже существуют для файла {media_path}, пропускаем.")
                                continue

                            if os.path.exists(media_path):
                                # Классифицируем изображение для базовой версии CLIP
                                clothing_score_clip_base = classify_image_clip_base(media_path)
                                # Классифицируем изображение для большой версии CLIP
                                clothing_score_clip_large = classify_image_clip_large(media_path)
                                
                                # Запись скоринга для каждой модели (перезапись при необходимости)
                                message_data["media_clothing_score_CLIP_base"][i] = (clothing_score_clip_base, media_path)
                                message_data["media_clothing_score_CLIP_large"][i] = (clothing_score_clip_large, media_path)

                                updated = True
                                logger.info(f"Обработан файл {media_path} с score CLIP base: {clothing_score_clip_base}, CLIP large: {clothing_score_clip_large}")
                            else:
                                logger.warning(f"Файл не найден: {media_path}")

                        # Сохраняем обновленный JSON только если были изменения
                        if updated:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(message_data, f, ensure_ascii=False, indent=4)
                            logger.info(f"Файл {file_path} успешно обновлён")

if __name__ == "__main__":
    process_json_files()
