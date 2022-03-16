import json
import logging
from datetime import datetime
from random import randrange
import random
from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tinydb import TinyDB, Query
import requests, bs4
from pyquery import PyQuery as pq
import calendar
import time
import os
from dotenv import load_dotenv
import pandas as pd

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

error_template = 'Попробуйте позднее'
update_template = 'Обновление в 00:00 MSK'
update_template_rnd = 'Обновление в 00:00 MSK, CAKE chat only'
update_cbr_template = 'Обновление каждый час'
info_text = 'Здарова, телеговские :)\n' \
            'Пожелания: @olegsvs (aka SentryWard)\n' \
            'Source code(писался на скорую руку): https://github.com/olegsvs/yepcock-size-bot\n' \
            'Для чата https://t.me/cakestreampage\n'  # \
            # '/anekdot1@yepcock_size_bot - Cлучайный анекдот от anekdotme.ru\n' \
            # '/anekdot2@yepcock_size_bot - Случайный анекдот с rzhunemogu.ru\n' \
            # '/bashim@yepcock_size_bot - Случайная цитата с bashorg.org\n'
            
# Init db
db = TinyDB('users/db.json')
dbCBR = TinyDB('users/dbCBR.json')
dbRANDOM = TinyDB('users/dbRANDOM.json')
UserQuery: Query = Query()

# TG_BOT_TOKEN
TOKEN = os.getenv("TG_BOT_TOKEN")


def start(update: Update, context: CallbackContext):
    key_board = [
        [InlineKeyboardButton('НАЧАТЬ', switch_inline_query_current_chat='')],
    ]

    update.message.reply_text(info_text, reply_markup=InlineKeyboardMarkup(key_board))

def get_anekdot():
    try:
        z = ''
        s = requests.get('http://anekdotme.ru/random')
        b = bs4.BeautifulSoup(s.text, "html.parser")
        p = b.select('.anekdot_text')
        for x in p:
            s = (x.getText().strip())
            z = z + s + '\n\n'
        return s
    except Exception as e:
        logger.error('Failed to get_anekdot: ' + str(e))
        return error_template


def get_anekdot2():
    try:
        res = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=1')
        content = json.JSONDecoder(strict=False).decode(res.content.decode('windows-1251'))
        return content['content']
    except Exception as e:
        logger.error('Failed to get_anekdot2: ' + str(e))
        return error_template


def sizer_cock(userId):
    size = sync_with_db(userId, "sizer_cock", randrange(30))
    type = 'см'
    if size >= 15:
        emoji = random.choice(['😏', '😱', '😂', '😁'])
    if size <= 14:
        emoji = random.choice(['😒', '☹️', '😣', '🥺'])
    text = 'Мой кок размером: <b>%s' % size + type + '</b> ' + emoji
    return text


def homo_sexual(userId):
    percent = sync_with_db(userId, "homo_sexual", randrange(101))
    text = " Я на <b>%s</b>" % percent + "<b>%</b>" + " гомосексуал (LGBT) 🏳️‍🌈"
    return text


key_get_my_cock_result = [
    [InlineKeyboardButton('Узнать свой размер 👉👈', switch_inline_query_current_chat='')],
]

key_get_my_gay_result = [
    [InlineKeyboardButton('Узнать свои шансы 🏳️‍🌈', switch_inline_query_current_chat='')],
]


def random_gay():
    user_text = get_random_gay_user_from_csv()
    text = '🎉 Сегодня ГЕЙ 🌈 дня - ' + user_text
    return text


def random_beautiful():
    user_text = get_random_beautiful_user_from_csv()
    text = '🎉 Сегодня КРАСАВЧИК 😊 дня - ' + user_text
    return text


def inlinequery(update: Update, _: CallbackContext):
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Размер члена...",
            description=update_template,
            thumb_url='https://i.imgur.com/wnV4Le9.png',
            input_message_content=InputTextMessageContent(sizer_cock(update.effective_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(key_get_my_cock_result)
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Я гомосексуал на...",
            description=update_template,
            thumb_url='https://i.imgur.com/1yqokVW.png',
            input_message_content=InputTextMessageContent(homo_sexual(update.effective_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(key_get_my_gay_result)
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Гей дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/0OCN8kR.png',
            input_message_content=InputTextMessageContent(random_gay(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Красавчик дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/YoLgEiP.png',
            input_message_content=InputTextMessageContent(random_beautiful(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Курс ЦБ-РФ $/€ к ₽",
            description=update_cbr_template,
            thumb_url='https://image.flaticon.com/icons/png/512/893/893078.png',
            input_message_content=InputTextMessageContent(get_exchange_rates(),
                                                          parse_mode=ParseMode.HTML),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="О боте",
            description='Описание',
            thumb_url='https://i.imgur.com/gRBXXvn.png',
            input_message_content=InputTextMessageContent(info_text,
                                                          parse_mode=ParseMode.HTML, disable_web_page_preview=True),
        ),
    ]
    if update.effective_chat:
        logger.info(update.effective_chat.id)
    logger.info(update)
    logger.info('\n\n')
    update.inline_query.answer(results, cache_time=0)


def get_exchange_rates():
    try:
        old_data_usd = dbCBR.search(Query().cbrUSD.exists())
        old_data_eur = dbCBR.search(Query().cbrEUR.exists())
        last_timestamp = dbCBR.search(Query().cbrTS.exists())
        now_ts = calendar.timegm(time.gmtime())
        logger.info('now_ts:'f"{now_ts=}")

        if not last_timestamp:
            need_force_update = True
        else:
            diff = now_ts - last_timestamp[0]['cbrTS']
            logger.info('diff:'f"{diff=}")
            if diff >= 3600:
                need_force_update = True
            else:
                need_force_update = False

        if need_force_update:
            old_data_eur = None
            old_data_usd = None

        if not old_data_usd:
            logger.info('old_data_usd not found, update from cbr-xml-daily...')
            upd_ts = get_formatted_date(now_ts)
            data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
            USD = data['Valute']['USD']['Value']
            EUR = data['Valute']['EUR']['Value']
            dbCBR.drop_tables()
            dbCBR.insert({'cbrUSD': USD})
            dbCBR.insert({'cbrEUR': EUR})
            dbCBR.insert({'cbrTS': now_ts})
            text = "Обновлено %s MSK" % upd_ts + "\n" \
                                                 "USD: <b>%s</b>" % USD + " ₽\n" \
                                                                          "EUR: <b>%s</b>" % EUR + " ₽"
            return text
        else:
            logger.info('old_data_usd found')
            upd_ts = get_formatted_date(last_timestamp[0]['cbrTS'])
            text = "Обновлено %s MSK" % upd_ts + "\n" \
                                                 "USD: <b>%s</b>" % old_data_usd[0]['cbrUSD'] + " ₽\n" \
                                                                                                "EUR: <b>%s</b>" % \
                   old_data_eur[0]['cbrEUR'] + " ₽"
            return text
    except Exception as e:
        logger.error('Failed to get_exchange_rates: ' + str(e))
        return error_template


def get_formatted_date(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%d.%m.%Y, %H:%M:%S")


def sync_with_db(userId, varType, varValue):
    user = db.search(UserQuery.id == userId)
    logger.info('userInDb:'f"{user=}")
    logger.info('userId:'f"{userId=}")
    logger.info('varType:'f"{varType=}")
    logger.info('varValue:'f"{varValue=}")
    if not user:
        logger.info('user not found')
        db.insert({'id': userId, varType: varValue})
        return varValue
    else:
        userByVarType = db.search((UserQuery.id == userId) & (UserQuery[varType].exists()))
        logger.info('userByVarType:'f"{userByVarType=}")
        if not userByVarType:
            logger.info('userByVarType none, update value...')
            db.update({'id': userId, varType: varValue}, UserQuery.id == userId)
            return varValue
        else:
            logger.info('userByVarType exists, get value...')
            return user[0][varType]


def info(update: Update, context: CallbackContext):
    update.message.reply_text(info_text, disable_web_page_preview=True)


def anekdot1(update: Update, context: CallbackContext):
    update.message.reply_text(get_anekdot())


def anekdot2(update: Update, context: CallbackContext):
    update.message.reply_text(get_anekdot2())


def bashim(update: Update, context: CallbackContext):
    update.message.reply_text(get_bash_quote())


def get_bash_quote():
    try:
        resp = requests.get('http://bashorg.org/random')
        page = pq(resp.content)
        text = page('.quote:first').text()
        id = page('.vote:first').text()
        return id + "\r\n\r\n" + text
    except Exception as e:
        logger.error('Failed to get_bash_quote: ' + str(e))
        return error_template


def get_random_gay_user_from_csv():
    try:
        logger.info('Getting gay user...')
        old_user_id = dbRANDOM.search(Query().gay_id.exists())
        old_user_name = dbRANDOM.search(Query().gay_name.exists())

        if not old_user_id:
            logger.info('old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            user_name2 = random_user.get('name').to_numpy()
            logger.info('UserName:'f"{user_name1[0]=}"f"{user_name2=}")
            if isNaN(user_name1):
                user_name = user_name2[0]
            else:
                user_name = user_name1[0]
            logger.info('Random user:'f"{user_id[0]=}"f"{user_name=}")
            dbRANDOM.insert({'gay_id': int(user_id[0])})
            dbRANDOM.insert({'gay_name': str(user_name)})
            text = '<a href="tg://user?id=%s' % user_id[0] + '">@%s' % user_name + '</a>'
            print(text)
            return text
        else:
            logger.info('old_user_id found')
            text = '<a href="tg://user?id=%s' % old_user_id[0]['gay_id'] + '">@%s' % old_user_name[0][
                'gay_name'] + '</a>'
            print(text)
            return text
            # return '<a href="tg://user?id=%s' % 220117151 + '"><b>%s' % 'Oleg Sinelnikov' + '</b></a>'
    except Exception as e:
        logger.error('Failed to get_random_gay_user_from_csv: ' + str(e))
        return error_template


def isNaN(num):
    return num != num


def get_random_beautiful_user_from_csv():
    try:
        logger.info('Getting beautiful user...')
        old_user_id = dbRANDOM.search(Query().beautiful_id.exists())
        old_user_name = dbRANDOM.search(Query().beautiful_name.exists())

        if not old_user_id:
            logger.info('old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            user_name2 = random_user.get('name').to_numpy()
            logger.info('UserName:'f"{user_name1[0]=}"f"{user_name2=}")
            if isNaN(user_name1):
                user_name = user_name2[0]
            else:
                user_name = user_name1[0]
            logger.info('Random user:'f"{user_id[0]=}"f"{user_name=}")
            dbRANDOM.insert({'beautiful_id': int(user_id[0])})
            dbRANDOM.insert({'beautiful_name': str(user_name)})
            text = '<a href="tg://user?id=%s' % user_id[0] + '">@%s' % user_name + '</a>'
            print(text)
            return text
        else:
            logger.info('old_user_id found')
            text = '<a href="tg://user?id=%s' % old_user_id[0]['beautiful_id'] + '">@%s' % old_user_name[0][
                'beautiful_name'] + '</a>'
            print(text)
            return text
    except Exception as e:
        logger.error('Failed to get_random_beautiful_user_from_csv: ' + str(e))
        return error_template


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))
    dispatcher.add_handler(CommandHandler("info", info, run_async=True))
    # dispatcher.add_handler(CommandHandler("anekdot1", anekdot1, run_async=True))
    # dispatcher.add_handler(CommandHandler("anekdot2", anekdot2, run_async=True))
    # dispatcher.add_handler(CommandHandler("bashim", bashim, run_async=True))
    dispatcher.add_handler(InlineQueryHandler(inlinequery, run_async=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
