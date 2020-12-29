#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from pycountry import countries
import numpy as np
import time
from database import Database
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    PollHandler,
    CallbackQueryHandler,
    PollAnswerHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

database = Database(os.environ['DATABASE_FILE'])

positive_feedback = ['Jawohl!', 'Genau!', 'Treffer!', 'Treffer. Versenkt!', 'Super!']
negative_feedback = ['Ach watt!', 'Blödsinn.', 'Nein.', 'Quatsch.', 'Leider nicht, nein.']
delay = 1 # seconds
n_choices = 4
global choices
global current_idx

def alpha_2_to_url(a2, size=1280):
    assert size in [20, 40, 80, 160, 320, 640, 1280, 2560]
    return "https://flagcdn.com/w{}/{}.png".format(size, a2.lower())

def get_country_flag():
    country = np.random.choice([c for c in countries])
    url = alpha_2_to_url(a2=country.alpha_2, size=640)
    return url

def build_question(update,context):
  global choices
  global current_idx
  choices = np.random.choice([c for c in countries], size=n_choices, replace=False)
  message = update.message if update.message else update.callback_query.message
  current_idx = np.random.randint(0,n_choices)
  message.reply_photo(alpha_2_to_url(choices[current_idx].alpha_2, size=640))
  button_list = []

  for i,country in enumerate(choices):
    label = "{} ({})".format(country.name, country.alpha_2)
    button_list.append(InlineKeyboardButton(label, callback_data=str(i)))
  reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
  message.reply_text(text='Welches Land ist das?',reply_markup=reply_markup)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

def start(update, context):
    build_question(update, context)

def validate(update, context, choice):
    global choices
    global current_idx
    keyboard = [[]]
    correct_answer = choices[current_idx]
    user_answer = choices[choice]
    if choice == current_idx:
        txt = "{}".format(np.random.choice(positive_feedback, 1)[0])
    else:
        txt = "{} Richtig wäre gewesen: {}".format(np.random.choice(negative_feedback, 1)[0], correct_answer.name)
    update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(keyboard))
    user_id = update.callback_query.message.chat.id
    country_id = correct_answer.alpha_2
    answer_country_id = user_answer.alpha_2
    data = database.insert_answer(user_id=user_id, country_id=country_id, answer_country_id=answer_country_id)
    logger.info("Created data point")
    logger.info(data)
    time.sleep(delay)
    build_question(update, context)

def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(lambda update, context: validate(update, context, 0), pattern=str(0)))
    dispatcher.add_handler(CallbackQueryHandler(lambda update, context: validate(update, context, 1), pattern=str(1)))
    dispatcher.add_handler(CallbackQueryHandler(lambda update, context: validate(update, context, 2), pattern=str(2)))
    dispatcher.add_handler(CallbackQueryHandler(lambda update, context: validate(update, context, 3), pattern=str(3)))



    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()