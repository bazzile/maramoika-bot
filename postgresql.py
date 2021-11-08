import os
import logging
from urllib import parse
import psycopg2
from psycopg2 import sql

# setting parameters for local / remote environment
if os.environ['USER'] != 'heroku':
    import config_local as config
else:
    import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(config.db_url)

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

