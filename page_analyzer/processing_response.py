from bs4 import BeautifulSoup


def get_information(content):
    html = BeautifulSoup(content, 'lxml')

    h1 = html.h1.text if html.find('h1') else ''
    title = html.title.text if html.find('title') else ''

    description = ''
    meta = html.head.find_all('meta', attrs={'name':'description'})[0]
    description = meta['content']

    h1, title, description = map(lambda elem: elem[:252] + '...' if len(elem) >= 255 else elem,
                                 [h1, title, description])

    return h1, title, description
