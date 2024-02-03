from urllib.parse import urlparse


def validate(url):
    errors = None
    o = urlparse(url)
    url = o.scheme + '://' + o.hostname
    if len(url) >= 255:
        errors = 'link is too long!'
    
    return url, errors
