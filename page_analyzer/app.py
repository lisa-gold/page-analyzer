from flask import (
    Flask,
    render_template,
    url_for,
    request,
    make_response,
    redirect,
    flash)
import os
from page_analyzer.validator import validate, normalize_url
from page_analyzer.database import (
    get_id_by_url_name,
    add_url,
    get_urls_data,
    get_url_by_id,
    get_checks_by_url_id,
    add_url_check)
import requests
from page_analyzer.html import get_information


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def ask_url():
    return render_template(
        'index.html'
    )


@app.get('/urls')
def get_urls():
    urls = get_urls_data()
    return render_template(
        'list_of_urls.html',
        urls=urls,
    )


@app.post('/urls')
def post_urls():
    url_original = request.form['url']
    error = validate(url_original)

    if error:
        flash(error, 'alert alert-danger')
        return render_template(
            'index.html',
            url=url_original
        ), 422

    url = normalize_url(url_original)
    url_id = get_id_by_url_name(url)
    if url_id:
        flash('Страница уже существует', 'alert alert-info')
        return redirect(url_for('get_url', id=url_id), code=302)

    url_id = add_url(url)
    flash('Страница успешно добавлена', 'alert alert-success')
    return make_response(redirect(url_for('get_url', id=url_id), code=302))


@app.route('/urls/<id>')
def get_url(id):
    url = get_url_by_id(id) or {}
    checks = get_checks_by_url_id(id) or []
    return render_template(
        'show.html',
        url=url,
        checks=checks
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def check_url(id):
    url = get_url_by_id(id)['name'] or ''

    try:
        response = requests.get(url)
        response.raise_for_status()
        status_code = response.status_code
        h1, title, description = get_information(response.text)
        add_url_check(id, status_code, h1, title, description)
        flash('Страница успешно проверена', 'alert alert-success')
        return redirect(url_for('get_url', id=id), code=302)

    except BaseException:
        error = 'Произошла ошибка при проверке'
        flash(error, 'alert alert-danger')
        return redirect(url_for('get_url', id=id))
