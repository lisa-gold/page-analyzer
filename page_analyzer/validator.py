from urllib.parse import urlparse


def validate(url):
    errors = None
    try:
        o = urlparse(url)
        url = o.scheme + '://' + o.hostname
        if len(url) >= 255 or (o.scheme != 'http' and o.scheme != 'https'):
            errors = 'Некорректный URL'
    except BaseException:
        errors = 'Некорректный URL'
    return url, errors
    
