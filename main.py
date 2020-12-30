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
import pycountry_convert as pc
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
    country = np.random.choice([c for c in countries if not c.alpha_2 in ['SJ']])
    url = alpha_2_to_url(a2=country.alpha_2, size=320)
    return country, url

def country_alpha2_to_continent_code(a2):
        if a2 == 'AQ': return 'AN'
        elif a2 == 'TF': return 'AF'
        elif a2 == 'EH': return 'AF'
        elif a2 == 'PN': return 'OC'
        elif a2 == 'SX': return 'NA'
        elif a2 == 'TL': return 'AS'
        elif a2 == 'UM': return 'NA'
        elif a2 == 'VA': return 'EU'
        else: return pc.country_alpha2_to_continent_code(a2)

def continents():
  return sorted(list(set(pc.convert_country_alpha2_to_continent_code.COUNTRY_ALPHA2_TO_CONTINENT_CODE.values())))

def get_countries(code):
  return sorted([c.alpha_2 for c in countries if country_alpha2_to_continent_code(c.alpha_2) == code])

def select_continent(update,context,replace=True):
  button_list = []
  for code in continents():
    label = "{}".format(pc.convert_continent_code_to_continent_name(code))
    button_list.append(InlineKeyboardButton(label, callback_data="continent_{}".format(code)))
  reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=2)) #n_cols = 1 is for single column and mutliple rows
  bot = update.message if update.message else update.callback_query.message
  if not replace:
    bot.reply_text(text='Welcher Kontinent?',reply_markup=reply_markup)
  else:
    update.callback_query.edit_message_text(text='Welcher Kontinent?',reply_markup=reply_markup)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

def start(update, context):
    country, url = get_country_flag()
    context.bot_data["correct_country"] = country
    message = update.message if update.message else update.callback_query.message
    message.reply_photo(url)
    select_continent(update, context, replace=False)

def make_callback(cb):
  def f(update, context):
    button_list = []
    for code in get_countries(cb):
      name = pc.country_alpha2_to_country_name(code)
      label = "{}({})".format(name, code)
      button_list.append(InlineKeyboardButton(label, callback_data="country_{}".format(code)))
    button_list.append(InlineKeyboardButton('Zurück', callback_data='select_continent'))
    reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=2)) #n_cols = 1 is for single column and mutliple rows
    update.callback_query.edit_message_text(text='Welches Land ist das?',reply_markup=reply_markup)
  return f

def make_country_callback(selected_country):
  def f(update, context):
    correct_country = context.bot_data['correct_country']
    if selected_country == correct_country.alpha_2:
        txt = "{} - {}".format(correct_country.name, np.random.choice(positive_feedback, 1)[0])
    else:
        txt = "{} - {} Richtig wäre gewesen:\n{} ({}), {}".format(selected_country, np.random.choice(negative_feedback, 1)[0], correct_country.name, correct_country.alpha_2, pc.convert_continent_code_to_continent_name(country_alpha2_to_continent_code(correct_country.alpha_2)))
    
    # store
    user_id = update.callback_query.message.chat.id
    country_id = correct_country.alpha_2
    answer_country_id = selected_country
    data = database.insert_answer(user_id=user_id, country_id=country_id, answer_country_id=answer_country_id)
    logger.info("Created data point")
    logger.info(data)
    
    update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[]]))
    time.sleep(1)
    start(update, context)
  return f

def validate(update, context, choice):
    global choices
    global current_idx
    keyboard = [[]]
    correct_answer = choices[current_idx]
    user_answer = choices[choice]
    if choice == current_idx:
        txt = "{}".format(np.random.choice(positive_feedback, 1)[0])
    else:
        txt = "{} - {} Richtig wäre gewesen: {}".format(,np.random.choice(negative_feedback, 1)[0], correct_answer.name)
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
    dispatcher.add_handler(CallbackQueryHandler(select_continent, pattern="select_continent"))
    for code in continents():
      dispatcher.add_handler(CallbackQueryHandler(make_callback(code), pattern="continent_{}".format(code)))
      for country in get_countries(code):
        dispatcher.add_handler(CallbackQueryHandler(make_country_callback(country), pattern="country_{}".format(country)))



    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()