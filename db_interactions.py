import os
from dotenv import load_dotenv
from typing import Tuple
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager


load_dotenv()
database_url = os.environ['DATABASE_URL']
pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=database_url)

@contextmanager
def get_connection():
    connection = pool.getconn()
    try:
        yield connection
    finally:
        pool.putconn(connection)

with get_connection() as connection:
    c = connection.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS polls (poll_id SERIAL PRIMARY KEY, poll_question TEXT, owner TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS options (option_id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS votes (option_id INTEGER, users_name TEXT, utc_timestamp INT)""")
    connection.commit()


class DbInteractions:
    @classmethod
    def save_poll_to_db(cls, poll_question, owner):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""INSERT INTO polls (poll_question, owner) VALUES (%s, %s) RETURNING poll_id""", (poll_question, owner))
            connection.commit()
            poll_id = c.fetchone()
            return poll_id


    @classmethod
    def save_option_to_db(cls, option_text, poll_id):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""INSERT INTO options (option_text, poll_id) VALUES (%s, %s)""", (option_text, poll_id))
            connection.commit()

    @classmethod
    def save_vote_to_db(cls, users_vote, users_name, utc_timestamp):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""INSERT INTO votes VALUES (%s, %s, %s)""", (users_vote, users_name, utc_timestamp))
            connection.commit()

    @classmethod
    def select_all_polls(cls):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""SELECT * FROM polls""")
            all_polls = c.fetchall()
            return all_polls

    @classmethod
    def select_poll_by_id(cls, poll_id) -> Tuple:
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("SELECT * FROM polls WHERE poll_id = %s", (poll_id,))
            poll_question = c.fetchone()
            return poll_question

    @classmethod
    def select_options_by_poll_id(cls, poll_id):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("SELECT * FROM options WHERE poll_id = %s", (poll_id,))
            options_tuple = c.fetchall()
            return options_tuple

    @classmethod
    def show_poll_options(cls, poll_id):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""
            SELECT 
            options.option_id,
            options.option_text
            FROM polls
            JOIN options ON polls.poll_id = options.poll_id     
            WHERE polls.poll_id = %s
            """, (poll_id,))

            poll_options = c.fetchall()
            return poll_options

    @classmethod
    def show_vote_stats(cls, poll_id):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""
            SELECT
            votes.option_id,
            COUNT(votes.option_id) AS no_of_votes,
            COUNT(votes.option_id)/SUM(COUNT(votes.option_id)) OVER () * 100 AS pct_of_votes
            FROM votes
            LEFT JOIN options ON votes.option_id = options.option_id
            WHERE options.poll_id = %s
            GROUP BY votes.option_id
            ORDER BY no_of_votes DESC
            """, (poll_id,))

            stats = c.fetchall()
            return stats

    @classmethod
    def draw_random_winner(cls, poll_id, start_utc_timestamp, end_utc_timestamp):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""
            SELECT * FROM votes
            JOIN options on votes.option_id = options.option_id
            JOIN polls on options.poll_id = polls.poll_id
            WHERE polls.poll_id = %s AND votes.utc_timestamp >= %s AND votes.utc_timestamp <= %s
            ORDER BY RANDOM()
            LIMIT 1""", (poll_id, start_utc_timestamp, end_utc_timestamp))
            random_winner = c.fetchone()
            return random_winner

    @classmethod
    def show_poll_ids(cls):
        with get_connection() as connection:
            c = connection.cursor()
            c.execute("""SELECT poll_id FROM polls""")
            return c.fetchall()

