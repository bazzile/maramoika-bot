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

    def payer_is_in_group(self, payer_id, group_id):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT (payer_telegram_id) FROM payer_group WHERE group_telegram_id = (%s);',
            (group_id,)
        )
        group_members = [member[0] for member in cur.fetchall()]
        if payer_id in group_members:
            return True

    def insert_payer(self, payer_id, group_id):
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO payer_group(payer_telegram_id, group_telegram_id) VALUES (%s, %s);',
            (payer_id, group_id)
        )
        self.conn.commit()
        cur.close()


