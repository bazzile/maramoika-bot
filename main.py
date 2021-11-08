#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


# setting parameters for local / remote environment
if os.environ['USER'] == 'vasily':
    import config_local as config
else:
    import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=config.telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    # setting parameters for local / remote environment
    if os.environ['USER'] == 'vasily':
        updater.start_polling()
    else:
        logger.info(f'port # {config.PORT}')
        # Start the webhook
        updater.start_webhook(listen="0.0.0.0",
                              port=config.PORT,
                              url_path=config.telegram_token)
        updater.bot.setWebhook(f"https://{config.heroku_app_name}.herokuapp.com/{config.telegram_token}")
        updater.idle()
    logger.info('Bot started successfully')


if __name__ == '__main__':
    main()
