#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# telegram credentials
telegram_token = os.environ.get('telegram_bot_token')
heroku_app_name = 'maramoika-bot'

# Port given by Heroku
PORT = int(os.environ.get('PORT', '8443'))

# postgresql
db_url = os.environ['DATABASE_URL']
