from bs4 import BeautifulSoup


def get_information(response):
    html = BeautifulSoup(response.text, 'lxml')
    status_code = response.status_code

    h1 = html.h1.text if html.find('h1') else ''
    title = html.title.text if html.find('title') else ''

    description = ''
    metas = html.head.find_all('meta')
    for meta in metas:
        if meta.get('name') == 'description':
            description = meta['content']

    if len(description) >= 500:
        description = description[:497] + '...'

    return status_code, h1, title, description
