import instaloader
import os
import json
import logging
import time
from urllib.parse import urlparse
try:
    from parsing.instagram_parser import config
except ImportError:
    try:
        from instagram_parser import config
    except ImportError:
        import config


# Настройка логирования
logging.basicConfig(
    filename=config.LOG_FILE,
    level=getattr(logging, config.LOGGING_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('instagram_parser')

# Убедитесь, что существует папка для хранения данных
os.makedirs(config.DATA_FOLDER, exist_ok=True)

# Путь к файлу сессии
session_file = os.path.join('parsing', 'instagram_parser', 'session_name.session')

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

def prompt_credentials():
    """Запрашиваем учетные данные у пользователя."""
    print('Пожалуйста, введите ваши учетные данные для Instagram.')
    username = input("Введите ваш Instagram логин: ").strip()
    password = input("Введите ваш Instagram пароль: ").strip()
    return username, password

def initialize_instaloader():
    """Инициализация Instaloader с сохранением сессии."""
    loader = instaloader.Instaloader(dirname_pattern=config.DATA_FOLDER)
    if config.PROXY_URL is not None:
        loader.context.proxy = config.PROXY_URL

    # Проверим, существует ли файл сессии
    if os.path.exists(session_file):
        logger.info(f'Файл сессии найден: {session_file}')
        try:
            loader.load_session_from_file(config.INSTAGRAM_USERNAME, session_file)
            logger.info("Сессия загружена успешно.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке сессии: {e}")
            return None
    else:
        logger.info('Файл сессии не найден. Запрашиваем учетные данные для создания новой сессии.')
        username, password = prompt_credentials()

        try:
            loader.login(username, password)
            # Сохраняем сессию, только если логин успешен
            loader.save_session_to_file(session_file)
            logger.info("Сессия успешно создана и сохранена.")
        except instaloader.exceptions.BadCredentialsException:
            logger.error("Неверные учетные данные для входа.")
            return None
        except Exception as e:
            logger.error(f"Ошибка при попытке входа: {e}")
            return None

    return loader

def fetch_profile_posts(loader, profile_name):
    """Получение всех постов профиля."""
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
        
        # Логирование общей информации о профиле
        logger.info(f"Парсинг профиля: {profile_name}")
        logger.info(f"Количество подписчиков: {profile.followers}")
        logger.info(f"Количество публикаций: {profile.mediacount}")
        
        posts = profile.get_posts()
        return posts
    except Exception as e:
        logger.error(f"Ошибка при получении постов профиля {profile_name}: {e}")
        return []

def download_media(post, profile_name):
    """Скачивание только медиафайлов с изображениями в папку media."""
    media_folder = os.path.join(config.DATA_FOLDER, profile_name, 'media')
    os.makedirs(media_folder, exist_ok=True)

    media_paths = []
    
    # Если пост состоит только из видео, мы его игнорируем
    if post.is_video and post.typename != 'GraphSidecar':
        logger.info(f"Пост {post.shortcode} содержит только видео и будет пропущен.")
        return None

    # Если это пост с несколькими медиа (альбом), выбираем только изображения
    if post.typename == 'GraphSidecar':
        for index, node in enumerate(post.get_sidecar_nodes()):
            # Проверяем, является ли это изображением
            if not node.is_video:
                file_path = os.path.join(media_folder, f'{post.shortcode}_{index}.jpg')
                media_paths.append(file_path)
                if not os.path.exists(file_path):  # Скачиваем только если файл не существует
                    post._context.get_and_write_raw(node.display_url, file_path)
            else:
                logger.info(f"Видео в альбоме {post.shortcode} пропущено.")
    else:
        # Если это одиночное изображение
        if not post.is_video:
            file_path = os.path.join(media_folder, f'{post.shortcode}.jpg')
            media_paths.append(file_path)
            if not os.path.exists(file_path):  # Скачиваем только если файл не существует
                post._context.get_and_write_raw(post.url, file_path)
        else:
            logger.info(f"Пост {post.shortcode} содержит только видео и будет пропущен.")

    return media_paths

def save_post_data(post, profile_name, stats):
    """Сохранение данных о посте в JSON файл."""
    # Скачивание медиафайлов и добавление путей в post_data
    media_paths = download_media(post, profile_name)

    # Пропускаем пост, если он состоит только из видео
    if media_paths is None or len(media_paths) == 0:
        logger.info(f"Пост {post.shortcode} пропущен, так как состоит только из видео.")
        return

    post_data = {
        'id': post.shortcode,
        'caption': post.caption,
        'likes': post.likes,
        'comments': None,  # Ставим None по умолчанию
        'views': post.video_view_count if post.is_video and hasattr(post, 'video_view_count') else None,  # Проверяем наличие video_view_count
        'media': media_paths,  # Добавляем только пути к изображениям
        'is_video': post.is_video,
        'date': post.date_utc.isoformat(),
    }

    # Пробуем получить комментарии, если они доступны
    try:
        time.sleep(1)  # Небольшая задержка перед запросом комментариев
        post_data['comments'] = post.comments
    except KeyError:
        logger.warning(f"Поле 'edge_media_to_parent_comment' отсутствует для поста {post.shortcode}. Пропускаем комментарии.")
    except Exception as e:
        logger.error(f"Ошибка при получении комментариев для поста {post.shortcode}: {e}")
    
    # Обновление статистики
    stats['post_count'] += 1
    stats['media_count'] += len(post_data['media'])
    post_date = post.date_utc
    if not stats['earliest_post'] or post_date < stats['earliest_post']:
        stats['earliest_post'] = post_date
    if not stats['latest_post'] or post_date > stats['latest_post']:
        stats['latest_post'] = post_date

    # Сохраняем данные поста в JSON файл (перезаписываем, если файл существует)
    post_folder = os.path.join(config.DATA_FOLDER, profile_name)
    os.makedirs(post_folder, exist_ok=True)
    
    post_file = os.path.join(post_folder, f"{post.shortcode}.json")
    with open(post_file, 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"Сохранены данные поста {post.shortcode}")

def __main__():
    """Главная функция, управляющая процессом парсинга."""
    loader = initialize_instaloader()
    
    if loader is None:
        logger.error("Instaloader не инициализирован.")
        return
    
    for profile_name in config.INSTAGRAM_PROFILES:
        logger.info(f"Начало парсинга профиля: {profile_name}")

        stats = {
            'post_count': 0,
            'media_count': 0,
            'earliest_post': None,
            'latest_post': None
        }

        posts = fetch_profile_posts(loader, profile_name)
        
        # Ограничение по количеству постов (если указано в config)
        post_count = 0
        for post in posts:
            save_post_data(post, profile_name, stats)
            post_count += 1
            time.sleep(2.5)  # Пауза между постами (увеличена до 2.5 секунд)
            if config.POST_LIMIT and post_count >= config.POST_LIMIT:
                break

        # Логирование результатов
        logger.info(f'Профиль: {profile_name}')
        logger.info(f'Скачано постов: {stats["post_count"]}')
        logger.info(f'Скачано медиафайлов: {stats["media_count"]}')
        logger.info(f'Самый ранний пост: {stats["earliest_post"]}')
        logger.info(f'Самый поздний пост: {stats["latest_post"]}')

        # Вывод в консоль
        print(f'Профиль: {profile_name}')
        print(f'Скачано постов: {stats["post_count"]}')
        print(f'Скачано медиафайлов: {stats["media_count"]}')
        print(f'Самый ранний пост: {stats["earliest_post"]}')
        print(f'Самый поздний пост: {stats["latest_post"]}')
        print('-' * 40)

if __name__ == '__main__':
    __main__()
