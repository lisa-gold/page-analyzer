from flask import (
    Flask,
    render_template,
    url_for,
    request,
    make_response,
    redirect)
from dotenv import load_dotenv
import os
import json


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def get_url():
    return render_template(
        'index.html',
    )


@app.route('/urls')
def get_urls():
    urls = request.cookies.get('urls') or {}
    urls = json.loads(urls)
    return render_template(
        'list_of_urls.html',
        urls=urls
    )


@app.post('/urls')
def urls_post():
    url = request.form.to_dict()
    urls = json.loads(request.cookies.get('urls', json.dumps({})))
    urls.update(url)
    urls = json.dumps(urls)
    response = make_response(redirect(url_for('get_urls'), code=302))
    response.set_cookie('urls', urls)
    return response
