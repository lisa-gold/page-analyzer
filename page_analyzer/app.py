from flask import (
    Flask,
    render_template,
    url_for,
    request,
    make_response,
    redirect,
    flash,
    get_flashed_messages)
from dotenv import load_dotenv
import os
import psycopg2
from page_analyzer.validator import validate
from datetime import date
import requests
from bs4 import BeautifulSoup


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/')
def ask_url():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        messages=messages
    )


@app.get('/urls')
def get_urls():
    urls = []
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT DISTINCT ON (u_id) u_id, n, date, status_code\
                          FROM (\
                          SELECT urls.id AS u_id, urls.name AS n,\
                          max(url_checks.created_at) AS date\
                          FROM urls\
                          LEFT JOIN url_checks ON urls.id = url_checks.url_id\
                          GROUP BY urls.id\
                          ) as t\
                          LEFT JOIN url_checks\
                          ON t.u_id = url_checks.url_id;'
                         )
            urls = curs.fetchall()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'list_of_urls.html',
        urls=urls,
        messages=messages
    )


@app.post('/urls')
def post_urls():
    url = request.form['url']
    url, errors = validate(url)

    if errors:
        flash(errors, 'alert alert-danger')
        return redirect(url_for('ask_url'))

    today = date.today()
    url_id = -1

    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE name=%s', (str(url),))
            url_old = curs.fetchall()
            if url_old:
                flash('Страница уже существует', 'alert alert-info')
                url_id = url_old[0][0]
                return redirect(url_for('get_url', id=url_id), code=302)

            curs.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                         (url, str(today)))
            curs.execute('SELECT id FROM urls WHERE name=%s', (str(url),))
            url_id = curs.fetchone()[0]

    flash('Страница успешно добавлена', 'alert alert-success')
    response = make_response(redirect(url_for('get_url', id=url_id), code=302))
    return response


@app.route('/urls/<id>')
def get_url(id):
    url = {}
    checks = []
    messages = get_flashed_messages(with_categories=True)
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url = curs.fetchall()
            curs.execute('SELECT * FROM url_checks WHERE url_id=%s', (id,))
            checks = curs.fetchall()
    return render_template(
        'show.html',
        url=url,
        messages=messages,
        checks=checks
    )


def get_url_name(id):
    url = ''
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url = curs.fetchone()
    return url[1]


def make_request(url):
    response = ''
    errors = None

    try:
        response = requests.get(url)
    except BaseException:
        errors = 'Произошла ошибка при проверке'

    return response, errors


def get_information(response):
    today = date.today()
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

    return status_code, h1, title, description, str(today)


@app.route('/urls/<id>/checks', methods=['POST'])
def check_url(id):
    url = get_url_name(id)
    response, errors = make_request(url)

    if errors:
        flash(errors, 'alert alert-danger')
        return redirect(url_for('get_url', id=id), code=422)

    status_code, h1, title, description, today = get_information(response)

    if status_code >= 500:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        return redirect(url_for('get_url', id=id), code=422)
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute(
                'INSERT INTO url_checks\
                (url_id, status_code, h1, title, description, created_at)\
                VALUES (%s, %s, %s, %s, %s, %s)',
                (id, status_code, h1, title, description, today)
            )
    flash('Страница успешно проверена', 'alert alert-success')
    return redirect(url_for('get_url', id=id), code=302)
