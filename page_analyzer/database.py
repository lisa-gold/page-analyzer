from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def is_url_new(url):
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE name=%s', (str(url),))
            url_old = curs.fetchall()
            if url_old:
                return False
    return True


def get_id_by_name(name):
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE name=%s', (name,))
            url = curs.fetchall()
            url_id = url[0][0]
    return url_id


def add_url(url):
    url_id = -1
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute("INSERT INTO urls (name) VALUES (%s)",
                         (url,))
            curs.execute('SELECT id FROM urls WHERE name=%s', (str(url),))
            url_id = curs.fetchone()[0]
    return url_id


def select_urls():
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
                         ON t.u_id = url_checks.url_id;')
            urls = curs.fetchall()
    return urls


def select_url(id):
    url = {}
    with connect() as conn:   
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url = curs.fetchall()
    return url


def select_checks(id):
    checks = []
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM url_checks WHERE url_id=%s', (id,))
            checks = curs.fetchall()
    return checks


def add_check(id, status_code, h1, title, description):
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute(
                'INSERT INTO url_checks\
                (url_id, status_code, h1, title, description)\
                VALUES (%s, %s, %s, %s, %s)',
                (id, status_code, h1, title, description)
            )
