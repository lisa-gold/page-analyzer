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
from datetime import datetime


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def form():
    return render_template(
        'index.html',
    )


@app.route('/urls')
def get_urls():
    urls = ['test!!!']
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
def urls_post():
    url = request.form.to_dict()
    url, errors = validate(url['url'])

    if errors:
        flash(errors, 'error')
        return render_template(
            'index/html',
            errors=errors
        ), 422

    now = datetime.now()

    with conn.cursor() as curs:
        curs.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                     (str(url), now))

    flash('Url successfully added', 'success')
    response = make_response(redirect(url_for('get_urls'), code=302))
    return response


@app.route('/urls/<id>')
def get_url(id):
    url = {}
    with conn.cursor() as curs:
        curs.execute('SELECT * FROM urls WHERE id=%s', id)
        url = curs.fetchall()
    return render_template(
        'show.html',
        url=url
    )
