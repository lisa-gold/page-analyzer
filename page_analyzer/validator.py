from urllib.parse import urlparse


def validate(url):
    error = None
    o = urlparse(url)
    url_norm = f'{o.scheme}://{o.hostname}'
    if len(url) >= 255 or (o.scheme != 'http' and o.scheme != 'https'):
        error = 'Некорректный URL'
    return url_norm, error
