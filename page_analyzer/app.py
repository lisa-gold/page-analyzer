from flask import (
    Flask,
    render_template,
    url_for,
    request,
    make_response,
    redirect,
    flash,
    get_flashed_messages)
import os
from page_analyzer.validator import validate
from page_analyzer.database import (
    is_url_new,
    get_id_by_name,
    add_url,
    select_urls,
    select_url,
    select_checks,
    add_check)
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def ask_url():
    return render_template(
        'index.html'
    )


@app.route('/urls', methods=['POST', 'GET'])
def get_urls():
    if request.method == 'POST':
        url_original = request.form['url']
        url, error = validate(url_original)

        if error:
            return render_template(
                'index.html',
                messages=[('alert alert-danger', error)],
                url=url_original
            ), 422

        if not is_url_new(url):
            flash('Страница уже существует', 'alert alert-info')
            url_id = get_id_by_name(str(url))
            return redirect(url_for('get_url', id=url_id), code=302)

        url_id = add_url(url)
        flash('Страница успешно добавлена', 'alert alert-success')
        return make_response(redirect(url_for('get_url', id=url_id), code=302))
    else:
        messages = get_flashed_messages(with_categories=True)
        urls = select_urls()
        return render_template(
            'list_of_urls.html',
            urls=urls,
            messages=messages,
        ), 302


@app.route('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = select_url(id) or {}
    checks = select_checks(id) or []
    return render_template(
        'show.html',
        url=url,
        messages=messages,
        checks=checks
    )


def get_url_name(id):
    url = select_url(id)[0][1] or ''
    return url


def make_request(url):
    response = ''
    error = None

    try:
        response = requests.get(url)
    except BaseException:
        error = 'Произошла ошибка при проверке'

    return response, error


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


@app.route('/urls/<id>/checks', methods=['POST'])
def check_url(id):
    url = get_url_name(id)
    response, error = make_request(url)

    if error:
        flash(error, 'alert alert-danger')
        return redirect(url_for('get_url', id=id))

    status_code, h1, title, description = get_information(response)

    if status_code >= 500:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        return redirect(url_for('get_url', id=id))
    add_check(id, status_code, h1, title, description)
    flash('Страница успешно проверена', 'alert alert-success')
    return redirect(url_for('get_url', id=id), code=302)
