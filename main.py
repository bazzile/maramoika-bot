#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import re
from telegram import (
    Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler,
    Filters, CallbackContext
)

import json

from postgresql import Database
from helpers import Payment, PayerManager

from config import (
    TELEGRAM_BOT_TOKEN,
    ENV_IS_SERVER,
    PORT,
    DATABASE_URL,
)

global db
heroku_app_name = 'maramoika-bot'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# logger.info(TELEGRAM_BOT_TOKEN)
# logger.info(DATABASE_URL)

# Stages
SELECT_SPLIT_STAGE, SELECT_PAYEES_STAGE, END = range(3)


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


def join(update: Update, context: CallbackContext):
    # works only in group chat
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    group_id = update.message.chat.id

    if not db.user_exists(user_id):
        db.create_user(user_id, user_name)

    # TODO prohibit transactions in private messages (no group id)
    if db.payer_is_in_group(user_id, group_id):
        update.message.reply_text('Ви уже есть в группе')
        return

    db.insert_payer_to_group(user_id, group_id)
    update.message.reply_text('Добавил')
    # logger.info(f'Successfully inserted user {user_id} into group {group_id}')


def validate_transaction(update: Update, context: CallbackContext) -> int:
    # works only in group chat
    user_id = update.message.from_user.id
    group_id = update.message.chat.id
    # TODO prohibit transactions in private messages (no group id)
    if not db.payer_is_in_group(user_id, group_id):
        # TODO reply with proper message and return proper id
        update.message.reply_text('Вы не в группе')
        return ConversationHandler.END

    pattern = re.search(r'^(\d+(([.,])\d{0,2})?)( +\D{3})?( +.+)$', ' '.join(context.args))
    if pattern:

        item = ' '.join(context.args[1:])  # .lower()
        price = context.args[0].replace(',', '.')  # .lower()
        payment = Payment(item, price)

        context.user_data['payment'] = payment

        select_split(update, context)

        return SELECT_SPLIT_STAGE

    else:
        update.message.reply_text(
            'Ой-вей, таки не пытайтесь меня пrовести! Я принимаю шекели в таком виде:\n'
            '/add СУММА КАТЕГОРИЯ\nнапример:\n/add 150 колбаса')
        return ConversationHandler.END


def select_split(update: Update, context: CallbackContext) -> int:

    keyboard = [
        [
            InlineKeyboardButton('Разделить на всех', callback_data='split')
        ],
        [
            InlineKeyboardButton('Выбрать участниов', callback_data='select'),
            InlineKeyboardButton('Отмена', callback_data='cancel')
        ]
    ]

    query = update.callback_query

    if query:
        query.answer()
        query.edit_message_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))

    return SELECT_SPLIT_STAGE


def select_payees(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    group_id = query.message.chat.id
    payer_manager = PayerManager(db.get_payers(group_id))

    payer_buttons = [
        InlineKeyboardButton(payer['name'], callback_data=payer['id']) for payer in payer_manager.payers
    ]

    control_buttons = [
        InlineKeyboardButton("⬅ Назад", callback_data=str("back")),
        InlineKeyboardButton("✅ Готово", callback_data=str("done"))]

    keyboard = [[payer_button] for payer_button in payer_buttons] + [control_buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Плательщики:", reply_markup=reply_markup
    )

    return SELECT_PAYEES_STAGE


def add_transaction(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    # works only in group chat
    user_id = query.from_user.id
    group_id = query.message.chat.id

    payment = context.user_data['payment']

    db.add_transaction(
        user_id=user_id, group_id=group_id, item=payment.item, price=payment.price)

    query.edit_message_text(text="Готово!")

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """

    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Отмена")
    return ConversationHandler.END


# ==============================


def main() -> None:
    # initialize db
    global db
    db = Database(DATABASE_URL)

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', validate_transaction, pass_args=True)],
        states={
            SELECT_SPLIT_STAGE: [
                CallbackQueryHandler(select_payees, pattern='^(select)$'),
                CallbackQueryHandler(cancel, pattern='^(cancel)$'),
            ],
            SELECT_PAYEES_STAGE: [
                CallbackQueryHandler(select_payees, pattern=f'^\\d{9}$'),
                CallbackQueryHandler(add_transaction, pattern='^(done)$'),
                CallbackQueryHandler(select_split, pattern='^(back)$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("join", join))

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(conv_handler)

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # finance =================================================================
    # dispatcher.add_handler(CommandHandler("add", add_transaction, pass_args=True))

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
