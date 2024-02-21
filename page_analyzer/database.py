from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    connect = psycopg2.connect(DATABASE_URL)
    return connect


def get_id_by_url_name(url_name):
    with connect() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name=%s', (url_name,))
            url_data = cursor.fetchone()
            if url_data:
                return url_data['id']


def add_url(url):
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id",
                           (url,))
            return cursor.fetchone()[0]


def get_urls_data():
    with connect() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT DISTINCT ON (u_id) u_id, name, date, status_code\
                         FROM (\
                         SELECT urls.id AS u_id, urls.name AS name,\
                         max(url_checks.created_at) AS date\
                         FROM urls\
                         LEFT JOIN url_checks ON urls.id = url_checks.url_id\
                         GROUP BY urls.id\
                         ) as table1\
                         LEFT JOIN url_checks\
                         ON table1.u_id = url_checks.url_id;')
            return cursor.fetchall()


def get_url_by_id(id):
    with connect() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE id=%s', (id,))
            return cursor.fetchone()


def get_checks_by_url_id(id):
    with connect() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM url_checks WHERE url_id=%s', (id,))
            return cursor.fetchall()


def add_url_check(id, status_code, h1, title, description):
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO url_checks\
                (url_id, status_code, h1, title, description)\
                VALUES (%s, %s, %s, %s, %s)',
                (id, status_code, h1, title, description)
            )
