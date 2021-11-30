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

    def user_exists(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT (id) FROM payer WHERE id = (%s);', (user_id, )
        )
        user = cur.fetchone()
        return user

    def create_user(self, user_id, user_name):
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO payer (id, name) VALUES (%s, %s);', (user_id, user_name)
        )
        self.conn.commit()
        logger.info(f'Successfully created user {user_name} with id {user_id}')
        cur.close()

    def add_transaction(self, user_id, group_id, item, price):
        payer_group_id = self.get_payer_group_id(user_id, group_id)
        cur = self.conn.cursor()
        logger.info('Adding a new transaction to group {}'.format(group_id))
        cur.execute(
            'INSERT INTO transaction (item, price, payer_group_id) VALUES (%s, %s, %s);',
            (item, price, payer_group_id))
        self.conn.commit()
        cur.close()
        return True

    def payer_is_in_group(self, payer_id, group_id):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT (payer_id) FROM payer_group WHERE group_id = (%s);',
            (group_id,)
        )
        group_members = [member[0] for member in cur.fetchall()]
        if payer_id in group_members:
            return True

    def insert_payer_to_group(self, payer_id, group_id):
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO payer_group(payer_id, group_id) VALUES (%s, %s);',
            (payer_id, group_id)
        )
        self.conn.commit()
        cur.close()

    def get_payer_group_id(self, payer_id, group_id):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT (id) FROM payer_group WHERE group_id = (%s) AND payer_id = (%s);',
            (group_id, payer_id)
        )
        payer_group_id = cur.fetchone()[0]
        return payer_group_id

    def get_payers(self, group_id):
        cur = self.conn.cursor()
        cur.execute(
            """SELECT id, name FROM payer WHERE payer.id IN (
                SELECT payer_id FROM payer_group WHERE group_id = (%s));""", (group_id, )
        )
        payers = [{'id': payer[0], 'name': payer[1]} for payer in cur.fetchall()]
        logger.info(payers)
