#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ToDo a dict with goup ids holding connections
import json
import jsonpickle
import logging

import re
from telegram import (
    Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler,
    Filters, CallbackContext, DictPersistence
)

from table import GoogleSheetsAPI, GroupSpreadSheetManager, Transaction
from postgresql import Database
from helpers import Payment, PayerManager

from config import (
    TELEGRAM_BOT_TOKEN,
    ENV_IS_SERVER,
    PORT,
    DATABASE_URL,
    GOOGLE_BOT_PKEY,
    TEMPLATE_SPREADSHEET_ID
)

global db
global google_sheets_api
heroku_app_name = 'maramoika-bot'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# logger.info(TELEGRAM_BOT_TOKEN)
# logger.info(DATABASE_URL)

# Stages
SELECT_SPLIT_STAGE, SELECT_PAYEES_STAGE, END = range(3)

telegram_user_id_regex = '[0-9]{9}'


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

# ==============================


def create_group_spreadsheet(group_spreadsheet_name):
    sheets_api_client = google_sheets_api
    sheets_api_client.create_spreadsheet_from_template(
        template_spreadsheet_id=TEMPLATE_SPREADSHEET_ID, new_name=group_spreadsheet_name)


def join_user(update: Update, _: CallbackContext):

    # TODO prohibit transactions in private messages (no group id)

    user_id, user_name = update.message.from_user.id, update.message.from_user.first_name
    group_id, group_name = str(update.message.chat.id), update.message.chat.title

    sheets_api_client = google_sheets_api
    group_spreadsheet_name = group_name + group_id

    if not sheets_api_client.group_spreadsheet_exists(group_id):
        create_group_spreadsheet(group_spreadsheet_name)

    sheet_manager = GroupSpreadSheetManager(
        sheets_api_client.open_spreadsheet_by_name(group_spreadsheet_name))

    if sheet_manager.payers.payer_exists(user_id):
        update.message.reply_text('Ви уже есть в группе')
        return

    sheet_manager.payers.add_payer(user_name, user_id)
    update.message.reply_text('Добавил')


# def validate_transaction(update: Update, context: CallbackContext) -> int:
#
#     user_id, user_name = update.message.from_user.id, update.message.from_user.first_name
#     group_id, group_name = str(update.message.chat.id), update.message.chat.title
#
#     sheets_api_client = google_sheets_api
#     group_spreadsheet_name = group_name + group_id
#
#     # if not sheets_api_client.group_spreadsheet_exists(group_id):
#     #     update.message.reply_text('')
#     #     return ConversationHandler.END
#     # sheet_manager = GroupSpreadSheetManager(
#     #     sheets_api_client.open_spreadsheet_by_name(group_spreadsheet_name))
#
#     # TODO prohibit transactions in private messages (no group id)
#     if not db.payer_is_in_group(user_id, group_id):
#         # TODO reply with proper message and return proper id
#         update.message.reply_text('Вы не в группе')
#         return ConversationHandler.END
#
#     pattern = re.search(r'^(\d+(([.,])\d{0,2})?)( +\D{3})?( +.+)$', ' '.join(context.args))
#     if pattern:
#
#         item = ' '.join(context.args[1:])  # .lower()
#         price = context.args[0].replace(',', '.')  # .lower()
#         payment = Payment(item, price)
#         context.user_data['payment'] = payment
#
#         payer_manager = PayerManager(db.get_payers(group_id))
#         context.user_data['payer_manager'] = payer_manager
#
#         select_split(update, context)
#
#         return SELECT_SPLIT_STAGE
#
#     else:
#         update.message.reply_text(
#             'Ой-вей, таки не пытайтесь меня пrовести! Я принимаю шекели в таком виде:\n'
#             '/add СУММА КАТЕГОРИЯ\nнапример:\n/add 150 колбаса')
#         return ConversationHandler.END


# def select_split(update: Update, context: CallbackContext) -> int:
#     keyboard = [
#         [
#             InlineKeyboardButton('Разделить на всех', callback_data='add'),
#             InlineKeyboardButton('Выбрать участниов', callback_data='select'),
#         ]
#     ]
#
#     query = update.callback_query
#
#     if query:
#         query.answer()
#         query.edit_message_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))
#     else:
#         update.message.reply_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))
#
#     return SELECT_SPLIT_STAGE


def select_payees(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    transaction = context.user_data['transaction']

    if re.match(telegram_user_id_regex, query.data):
        selected_payee = query.data
        transaction.toggle_payee(selected_payee)

    context.user_data['transaction'] = transaction

    payer_buttons = [
        InlineKeyboardButton('💵 ' + payee['name'] if payee['is_selected'] else payee['name'],
                             callback_data=payee['telegram_id']) for payee in transaction.payees
    ]

    control_buttons = [[InlineKeyboardButton("✅ Готово", callback_data=str("done"))]] + [[
        InlineKeyboardButton("⬅ Назад", callback_data=str("back")),
        InlineKeyboardButton('Отмена', callback_data='cancel')
        ]]

    keyboard = [[payer_button] for payer_button in payer_buttons] + control_buttons

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Плательщики:", reply_markup=reply_markup
    )

    logger.info(query)

    return SELECT_PAYEES_STAGE


# def add_transaction(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     # works only in group chat
#     user_id = query.from_user.id
#     group_id = query.message.chat.id
#
#     payment = context.user_data['payment']
#     payer_manager = context.user_data['payer_manager']
#     selected_payees_id_list = payer_manager.get_selected_payee_ids()
#
#     db.add_transaction_with_payees(
#         user_id=user_id, group_id=group_id, item=payment.item, price=payment.price,
#         payee_id_list=selected_payees_id_list)
#
#     query.edit_message_text(text="Готово!")
#
#     return ConversationHandler.END

def add_transaction(update: Update, context: CallbackContext) -> int:

    user_id, user_name = update.message.from_user.id, update.message.from_user.first_name
    group_id, group_name = str(update.message.chat.id), update.message.chat.title

    sheets_api_client = google_sheets_api
    group_spreadsheet_name = group_name + group_id

    if not sheets_api_client.group_spreadsheet_exists(group_id):
        update.message.reply_text('Сначала создайте таблицу')
        return ConversationHandler.END

    sheet_manager = GroupSpreadSheetManager(
        sheets_api_client.open_spreadsheet_by_name(group_spreadsheet_name))

    payer = sheet_manager.payers.get_payer_by_id(user_id)
    payers = sheet_manager.payers.list_payers()

    # ToDo payer exists as method?
    if not sheet_manager.payers.payer_exists(user_id):
        update.message.reply_text('Сначала вступите в группу')
        return ConversationHandler.END

    item = ' '.join(context.args[1:])  # .lower()
    price = context.args[0]  # .replace(',', '.')  # .lower()

    transaction = Transaction(item, price, payer, payers)

    if not transaction.is_valid:
        update.message.reply_text(
            'Ой-вей, таки не пытайтесь меня пrовести! Я принимаю шекели в таком виде:\n'
            '/add СУММА КАТЕГОРИЯ\nнапример:\n/add 150 колбаса')
        return ConversationHandler.END
        # payment = Payment(item, price)
        # context.user_data['payment'] = payment

        # payer_manager = PayerManager(db.get_payers(group_id))
        # context.user_data['payer_manager'] = payer_manager

    context.user_data['transaction'] = transaction

    keyboard = [
        [
            InlineKeyboardButton('Разделить на всех', callback_data='add'),
            InlineKeyboardButton('Выбрать участниов', callback_data='select'),
        ]
    ]

    # query = update.callback_query

    # if query:
    #     query.answer()
    #     query.edit_message_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))
    # else:
    #     update.message.reply_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))
    # if query:
    #     query.answer()
    #     query.edit_message_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))
    # else:
    update.message.reply_text('Как внести?', reply_markup=InlineKeyboardMarkup(keyboard))

    return SELECT_SPLIT_STAGE

    # else:
    #     update.message.reply_text(
    #         'Ой-вей, таки не пытайтесь меня пrовести! Я принимаю шекели в таком виде:\n'
    #         '/add СУММА КАТЕГОРИЯ\nнапример:\n/add 150 колбаса')
    #     return ConversationHandler.END
    #

    # query = update.callback_query
    # query.answer()
    # # works only in group chat
    # user_id = query.from_user.id
    # group_id = query.message.chat.id
    #
    # payment = context.user_data['payment']
    # payer_manager = context.user_data['payer_manager']
    # selected_payees_id_list = payer_manager.get_selected_payee_ids()
    #
    # db.add_transaction_with_payees(
    #     user_id=user_id, group_id=group_id, item=payment.item, price=payment.price,
    #     payee_id_list=selected_payees_id_list)
    #
    # query.edit_message_text(text="Готово!")

    # return ConversationHandler.END


# def user_id (user_id, group_id)


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
    global google_sheets_api
    google_sheets_api = GoogleSheetsAPI(pkey=GOOGLE_BOT_PKEY)
    # bot_data_json = json.dumps({'google_sheets_api': jsonpickle.encode(google_sheets_api)})
    # bot_data_json = json.dumps({'google_sheets_api': google_sheets_api})
    # new_sheet = google_sheets_api.create_spreadsheet_from_template(
    #     template_spreadsheet_id=TEMPLATE_SHEET_ID, new_name='NEW_!')
    #
    # payers = PayerSheet(new_sheet, 'payers')
    # payers.add_payer('хуй', '008')

    global db
    db = Database(DATABASE_URL)

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # persistence = DictPersistence(bot_data_json=bot_data_json)
    # updater = Updater(TELEGRAM_BOT_TOKEN, persistence=persistence)
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_transaction, pass_args=True)],
        states={
            SELECT_SPLIT_STAGE: [
                CallbackQueryHandler(select_payees, pattern='^(select)$'),
                # CallbackQueryHandler(add_transaction, pattern='^(add)$'),
            ],
            SELECT_PAYEES_STAGE: [
                CallbackQueryHandler(select_payees, pattern=telegram_user_id_regex),
                CallbackQueryHandler(add_transaction, pattern='^(done)$'),
                # CallbackQueryHandler(select_split, pattern='^(back)$'),
                CallbackQueryHandler(cancel, pattern='^(cancel)$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("join", join_user))

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(conv_handler)

    # finance =================================================================

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
