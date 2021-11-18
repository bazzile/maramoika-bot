#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from config import (
    TELEGRAM_BOT_TOKEN,
    ENV_IS_SERVER,
    PORT,
    DATABASE_URL,
)

heroku_app_name = 'maramoika-bot'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(ENV_IS_SERVER)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

# ==============================


def add_transaction(update: Update, context: CallbackContext) -> None:
    # works only in group chat
    user_id = update.message.from_user.id
    group_id, group_name = update.message.chat.id, update.message.chat.title

# ==============================


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # finance =================================================================
    dispatcher.add_handler(CommandHandler("add", add_transaction, pass_args=True))

    # Start the Bot
    if ENV_IS_SERVER:  # running on server
        logger.info('Running on server...')
        # Start the webhook
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"https://{heroku_app_name}.herokuapp.com/{TELEGRAM_BOT_TOKEN}")
        updater.idle()
    else:  # running locally
        logger.info('Running locally...')
        updater.start_polling()
    logger.info('Bot started successfully')


if __name__ == '__main__':
    main()

