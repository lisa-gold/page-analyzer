from bs4 import BeautifulSoup


def get_information(content):
    html = BeautifulSoup(content, 'lxml')

    h1 = html.h1.text if html.find('h1') else ''
    title = html.title.text if html.find('title') else ''

    description = ''
    meta = html.head.find('meta', attrs={'name': 'description'})
    description = meta['content']

    h1, title, description = map(lambda elem: elem[:255],
                                 [h1, title, description])

    return h1, title, description
