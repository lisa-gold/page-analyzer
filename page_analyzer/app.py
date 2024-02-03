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


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    urls = []
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls')
            urls = curs.fetchall()
    messages = get_flashed_messages()
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
        flash(errors, 'error')
        return render_template(
            'index/html',
            errors=errors
        ), 422

    today = date.today()
    url_id = -1

    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE name=%s', (str(url),))
            url_old = curs.fetchall()
            if url_old:
                flash('This url has been already added!', 'error')
                return render_template(
                    'list_of_urls.html',
                    errors=errors
                ), 422

            curs.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                         (url, str(today)))
            curs.execute('SELECT id FROM urls WHERE name=%s', (str(url),))
            url_id = curs.fetchone()[0]

    flash('Url successfully added', 'success')
    response = make_response(redirect(url_for('get_url', id=url_id), code=302))
    return response


@app.route('/urls/<id>')
def get_url(id):
    url = {}
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url = curs.fetchall()
    return render_template(
        'show.html',
        url=url
    )
