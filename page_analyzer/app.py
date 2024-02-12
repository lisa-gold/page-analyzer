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
from page_analyzer.validator import validate, normalize_url
from page_analyzer.database import (
    get_id_by_url_name,
    add_url,
    select_urls_data,
    select_url_data,
    select_url_checks,
    add_url_check)
import requests
from page_analyzer.processing_response import get_information


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
        url = normalize_url(url_original)
        error = validate(url)

        if error:
            flash(error, 'alert alert-danger')
            return render_template(
                'index.html',
                messages=get_flashed_messages(with_categories=True),
                url=url_original
            ), 422

        url_id = get_id_by_url_name(str(url))
        if url_id:
            flash('Страница уже существует', 'alert alert-info')
            return redirect(url_for('get_url', id=url_id), code=302)

        url_id = add_url(url)
        flash('Страница успешно добавлена', 'alert alert-success')
        return make_response(redirect(url_for('get_url', id=url_id), code=302))
    else:
        messages = get_flashed_messages(with_categories=True)
        urls = select_urls_data()
        return render_template(
            'list_of_urls.html',
            urls=urls,
            messages=messages,
        ), 302


@app.route('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = select_url_data(id) or {}
    checks = select_url_checks(id) or []
    return render_template(
        'show.html',
        url=url,
        messages=messages,
        checks=checks
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def check_url(id):
    url = select_url_data(id)['name'] or ''
    response = ''
    error = None

    try:
        response = requests.get(url)
    except BaseException:
        error = 'Произошла ошибка при проверке'

    if error:
        flash(error, 'alert alert-danger')
        return redirect(url_for('get_url', id=id))

    status_code, h1, title, description = get_information(response)

    if status_code >= 500:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        return redirect(url_for('get_url', id=id))
    add_url_check(id, status_code, h1, title, description)
    flash('Страница успешно проверена', 'alert alert-success')
    return redirect(url_for('get_url', id=id), code=302)
