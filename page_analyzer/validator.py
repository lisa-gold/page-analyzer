from urllib.parse import urlparse


def validate(url):
    errors = None
    o = urlparse(url)
    url = f'{o.scheme}://{o.hostname}'
    if len(url) >= 255 or (o.scheme != 'http' and o.scheme != 'https'):
        errors = 'Некорректный URL'
    return url, errors
