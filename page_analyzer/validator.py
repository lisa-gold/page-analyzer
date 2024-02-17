from urllib.parse import urlparse
from validators import url as is_url_valid


def normalize_url(url):
    o = urlparse(url)
    url_normalized = f'{o.scheme}://{o.hostname}'
    return url_normalized


def validate(url):
    if is_url_valid(url):
        if len(normalize_url(url)) < 255:
            return None
    return 'Некорректный URL'
