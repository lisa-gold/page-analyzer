from urllib.parse import urlparse
from validators import url as is_url_valid


def normalize_url(url):
    url_components = urlparse(url)
    url_normalized = f'{url_components.scheme}://{url_components.hostname}'
    return url_normalized


def validate(url):
    if not url:
        return 'Поле URL не может быть пустым'
    if not is_url_valid(url):
        return 'Некорректный URL'
    if len(normalize_url(url)) >= 255:
        return 'Длина URL превышает 254 символа'
