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

positive_feedback = ['Jawohl!', 'Genau!', 'Treffer!', 'Treffer. Versenkt!', 'Super!']
negative_feedback = ['Ach watt!', 'Blödsinn.', 'Nein.', 'Quatsch.', 'Leider nicht, nein.']
delay = 1 # seconds
current_answer = None
correct_answer = None
stopped = True

def alpha_2_to_url(a2, size=1280):
    assert size in [20, 40, 80, 160, 320, 640, 1280, 2560]
    return "https://flagcdn.com/w{}/{}.png".format(size, a2.lower())

def get_country_flag():
    country = np.random.choice([c for c in countries])
    url = alpha_2_to_url(a2=country.alpha_2, size=640)
    return url

def build_question(update,context):
  global correct_answer
  global running
  if not running: return
  choices = np.random.choice([c for c in countries], size=4, replace=False)
  message = update.message if update.message else update.callback_query.message
  i = np.random.randint(0,4)
  correct_answer = choices[i].name
  message.reply_photo(alpha_2_to_url(choices[i].alpha_2, size=640))
  button_list = []
  for j, each in enumerate([c.name for c in choices]):
     button_list.append(InlineKeyboardButton(each, callback_data=('correct' if i==j else 'wrong')))
  reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
  message.reply_text(text='Zu welchem Land gehört die Flagge?',reply_markup=reply_markup)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

def start(update, context):
    global running
    running = True
    build_question(update, context)

def slow(update, context):
    global delay
    delay = 10

def fast(update, context):
    global delay
    delay = 1

def correct(update, context):
    global delay
    keyboard = [[]]
    update.callback_query.edit_message_text(np.random.choice(positive_feedback, 1)[0], reply_markup=InlineKeyboardMarkup(keyboard))
    time.sleep(delay)
    build_question(update, context)

def wrong(update, context):
    global delay
    global correct_answer
    keyboard = [[]]
    txt = "{} Richtig wäre gewesen: {}".format(np.random.choice(negative_feedback, 1)[0], correct_answer)
    update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(keyboard))
    time.sleep(delay)
    build_question(update, context)

def stop(update, context):
    update.message.reply_text('Gestoppt.', reply_markup=ReplyKeyboardRemove())
    running = False 

def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('stop', stop))
    dispatcher.add_handler(CommandHandler('langsam', slow))
    dispatcher.add_handler(CommandHandler('schnell', fast))
    dispatcher.add_handler(CallbackQueryHandler(correct, pattern='correct'))
    dispatcher.add_handler(CallbackQueryHandler(wrong, pattern='wrong'))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()