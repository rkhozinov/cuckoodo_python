# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, Job, MessageHandler, Filters
import logging
import re
import datetime
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

pattern_add = re.compile(
    '/([a-zA-Zа-яА-Я]{1,15})(\s[^@\s]+)(\s[@a-zA-Z0-9]+)?(\s[a-zA-Zа-яА-Я]+)*((\s\d{1,2}\s[a-zA-Zа-яА-Я]+)*)',
    re.IGNORECASE)

time_units_hours = re.compile('(\d{1,2})\s(ч(ас)?(а|ов)?)')
time_units_min = re.compile('(\d{1,2})\s(м(ин)?(ут)?(ы)?)')
time_units_sec = re.compile('(\d{1,2})\s(с(ек)?(унд)?(ы|у)?)')

assignee_all_name = 'all'

error_text = 'Не понял'
add_response_text = 'Добавлена заметка {} для {}'
add_reminder_response_text = 'Добавлено напоминание {} для {}, напомню через {}'

storage = {}


class Issue(object):
    def __init__(self, text, owner, created, assignee=None, interval=None):
        self.text = text
        self.owner = owner
        self.created = created
        self.assignee = assignee
        self.interval = interval

    def __str__(self, *args, **kwargs):
        return "text={}, owner={}, created={}, assignee={}, interval={}".format(self.text, self.owner, self.created,
                                                                                self.assignee, self.interval)


def add_issue(bot, update):
    match = pattern_add.match(update.message.text)

    if not match:
        logger.info('message invalid')
        update.message.reply_text = error_text
        return

    command = match.group(1).strip()
    text = match.group(2).strip()
    assignee = match.group(3)
    interval_declaration = match.group(4)
    interval_value = match.group(5)
    owner = update.message.chat.id

    issue = Issue(text, owner, datetime.datetime.today())

    if interval_declaration is not None and interval_value is not None:
        interval_value = interval_value.strip()
        interval_sec = 0
        if time_units_hours.search(interval_value):
            interval_sec += int(time_units_hours.search(interval_value).group(1)) * 3600
        if time_units_min.search(interval_value):
            interval_sec += int(time_units_min.search(interval_value).group(1)) * 60
        if time_units_sec.search(interval_value):
            interval_sec += int(interval_sec.search(interval_value).group(1))
        issue.interval = interval_sec

    if assignee is not None:
        issue.assignee = assignee.strip().replace('@','')
    else:
        issue.assignee = assignee_all_name

    if issue.interval is None:
        update.message.reply_text(add_response_text.format(issue.text, issue.assignee))
    else:
        update.message.reply_text(add_reminder_response_text.format(issue.text, issue.assignee, interval_value))

    logger.info('Add issue ' + str(issue))


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    token = os.environ['TOKEN']
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add_issue))

    # # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()