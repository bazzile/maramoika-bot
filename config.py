#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# telegram credentials
telegram_token = os.environ.get('telegram_bot_token')
heroku_app_name = 'maramoika-bot'

# Port given by Heroku
port = os.environ.get('PORT', '8443')
