from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def get_id_by_url_name(url_name):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE name=%s', (url_name,))
            url_data = curs.fetchone()
            if url_data:
                return url_data['id']
    return False


def add_url(url):
    url_id = -1
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute("INSERT INTO urls (name) VALUES (%s)",
                         (url,))
            curs.execute('SELECT id FROM urls WHERE name=%s', (url,))
            url_id = curs.fetchone()['id']
    return url_id


def select_urls_data():
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT DISTINCT ON (u_id) u_id, name, date, status_code\
                         FROM (\
                         SELECT urls.id AS u_id, urls.name AS name,\
                         max(url_checks.created_at) AS date\
                         FROM urls\
                         LEFT JOIN url_checks ON urls.id = url_checks.url_id\
                         GROUP BY urls.id\
                         ) as table1\
                         LEFT JOIN url_checks\
                         ON table1.u_id = url_checks.url_id;')
            urls_data = curs.fetchall()
    return urls_data


def select_url_data(id):
    url_data = {}
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url_data = curs.fetchone()
    return url_data


def select_url_checks(id):
    checks = []
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM url_checks WHERE url_id=%s', (id,))
            checks = curs.fetchall()
    return checks


def add_url_check(id, status_code, h1, title, description):
    with connect() as conn:
        with conn.cursor() as curs:
            curs.execute(
                'INSERT INTO url_checks\
                (url_id, status_code, h1, title, description)\
                VALUES (%s, %s, %s, %s, %s)',
                (id, status_code, h1, title, description)
            )
