import logging
from urllib import parse
import psycopg2

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Database(object):
    def __init__(self, database_url):
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(database_url)

        self.conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

    def add_transaction(self, user_id, group_id, item, price):
        cur = self.conn.cursor()
        logger.info('Adding a new transaction to group {}'.format(group_id))
        cur.execute(
            'INSERT INTO transaction (item, price, payer_id, group_id) VALUES (%s, %s, %s, %s);',
            (item, price, user_id, group_id))
        self.conn.commit()
        cur.close()
        return True
