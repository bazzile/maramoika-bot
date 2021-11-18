import os
import logging
from urllib import parse
import psycopg2
from psycopg2 import sql

from config import DATABASE_URL

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(DATABASE_URL)

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)


def add_transaction(user_id, group_id, item_desc, price):
    cur = conn.cursor()
    logger.info('Adding a new transaction to group {}'.format(group_id))
    cur.execute(
        'INSERT INTO transactions (user_id, group_id, item_desc, price) VALUES (%s, %s, %s, %s);',
        (user_id, group_id, item_desc, price))
    conn.commit()
    cur.close()
    return True