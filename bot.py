import calendar
import json
import logging
import os
import random
import time
from datetime import datetime
from random import randrange
from uuid import uuid4
import bs4
import pandas as pd
import requests
from dotenv import load_dotenv
from pyquery import PyQuery as PyQ
from telegram import InlineKeyboardButton, Update, InlineQueryResultArticle, InputTextMessageContent, ParseMode, \
    InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CommandHandler, InlineQueryHandler, ChosenInlineResultHandler
from tinydb import TinyDB, Query
import subprocess
from sys import platform

# Enable logging
logging.basicConfig(
    filename=datetime.now().strftime('logs/log_%H_%M_%d_%m_%Y.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

# TG_BOT_TOKEN
TOKEN = os.getenv("TG_BOT_TOKEN")

def get_raspberry_info():
    if platform == "linux":
        rasp_model = subprocess.run(['cat', '/sys/firmware/devicetree/base/model'], capture_output=True, text=True).stdout.strip("\n")
        temp = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True).stdout.strip("\n")
        return 'Запущено на: ' + rasp_model + ', ' + temp
    else:
        return ''

error_template = 'Попробуйте позднее'
update_template = 'Обновление в 00:00 MSK'
update_template_rnd = 'Обновление в 00:00 MSK, CAKE chat only'
update_cbr_template = 'Обновление каждый час'
info_text = 'Здарова, телеговские :)\n' \
            'Пожелания: @olegsvs (aka SentryWard)\n' \
            'Source code(писался на скорую руку): https://github.com/olegsvs/yepcock-size-bot\n' \
            'Для чата https://t.me/cakestreampage\n' \
            '' + get_raspberry_info()  # \
            # '/anekdot1@yepcock_size_bot - Cлучайный анекдот от anekdotme.ru\n' \
            # '/anekdot2@yepcock_size_bot - Случайный анекдот с rzhunemogu.ru\n' \
            # '/bashim@yepcock_size_bot - Случайная цитата с bashorg.org\n'

sad_emoji = ['😒', '☹️', '😣', '🥺', '😞', '🙄', '😟', '😠', '😕', '😖', '😫', '😩', '😰', '😭']
happy_emoji = ['😀', '😏', '😱', '😂', '😁', '😂', '😉', '😊', '😋', '😎', '☺', '😏']

# Init db
db = TinyDB('users/db.json')
dbCBR = TinyDB('users/dbCBR.json')
dbRANDOM = TinyDB('users/dbRANDOM.json')
UserQuery: Query = Query()

def start(update: Update, _: CallbackContext):
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
    if size >= 15:
        emoji = random.choice(happy_emoji)
    else:
        emoji = random.choice(sad_emoji)
    text = 'Мой кок размером: <b>%s' % size + 'см</b> ' + emoji
    return text


def homo_sexual(userId):
    percent = sync_with_db(userId, "homo_sexual", randrange(101))
    text = " Я на <b>%s</b>" % percent + "<b>%</b>" + " гомосексуал (LGBT) 🏳️‍🌈"
    return text


def iq_test(userId):
    iq = sync_with_db(userId, "iq_test", randrange(161))
    if iq >= 100:
        emoji = random.choice(happy_emoji)
    else:
        emoji = random.choice(sad_emoji)
    if iq > 140:
        hint = 'такой показатель всего у 0,2% человечества'
    if iq <= 140:
        hint = 'такой показатель всего у 2,5% человечества'
    if iq <= 130:
        hint = 'очень высокий'
    if iq <= 120:
        hint = 'высокий'
    if iq <= 110:
        hint = 'выше среднего'
    if iq <= 100:
        hint = 'средний'
    if iq <= 90:
        hint = 'ниже среднего'
    if iq <= 80:
        hint = 'как у приматов'
    if iq <= 76:
        hint = 'как у китов'
    if iq <= 72:
        hint = 'как у слонов'
    if iq <= 68:
        hint = 'как у собак'
    if iq <= 64:
        hint = 'как у кошек'
    if iq <= 60:
        hint = 'как у крысок'
    if iq <= 56:
        hint = 'как у свинок'
    if iq <= 52:
        hint = 'как у белок'
    if iq <= 48:
        hint = 'как у соек'
    if iq <= 44:
        hint = 'как у ворон'
    if iq <= 40:
        hint = 'как у енотов'
    if iq <= 36:
        hint = 'как у морских котиков'
    if iq <= 32:
        hint = 'как у попугаев'
    if iq <= 28:
        hint = 'как у лошадей'
    if iq <= 24:
        hint = 'как у голубей'
    if iq <= 20:
        hint = 'как у овец'
    if iq <= 16:
        hint = 'как у крокодилов'
    if iq <= 12:
        hint = 'как у пчёл'
    if iq <= 8:
        hint = 'как у черепах'
    if iq <= 4:
        hint = 'как у пыли'

    text = 'Мой IQ: <b>%s' % iq + '</b> из 160 баллов, ' + hint + ' ' + emoji
    return text


key_get_my_cock_result = [
    [InlineKeyboardButton('Узнать свой размер 👉👈', switch_inline_query_current_chat='')],
]

key_get_my_IQ_result = [
    [InlineKeyboardButton('Проверь свой интеллект 🧠', switch_inline_query_current_chat='')],
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


def on_result_chosen(update: Update, _: CallbackContext):
    logger.info(update)
    logger.info('\n')


def get_inline_id(prefix: str):
    return prefix + '_' + str(uuid4())


def inlinequery(update: Update, _: CallbackContext):
    logger.info(update)
    results = [
        InlineQueryResultArticle(
            id=get_inline_id('sizer_cock'),
            title="Размер члена...",
            description=update_template,
            thumb_url='https://i.imgur.com/wnV4Le9.png',
            input_message_content=InputTextMessageContent(sizer_cock(update.effective_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(key_get_my_cock_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('homo_sexual'),
            title="Я гомосексуал на...",
            description=update_template,
            thumb_url='https://i.imgur.com/1yqokVW.png',
            input_message_content=InputTextMessageContent(homo_sexual(update.effective_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(key_get_my_gay_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('iq_test'),
            title="Мой IQ...",
            description=update_template,
            thumb_url='https://i.imgur.com/95qsO7Y.png',
            input_message_content=InputTextMessageContent(iq_test(update.effective_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(key_get_my_IQ_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('random_gay'),
            title="Гей дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/0OCN8kR.png',
            input_message_content=InputTextMessageContent(random_gay(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('random_beautiful'),
            title="Красавчик дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/YoLgEiP.png',
            input_message_content=InputTextMessageContent(random_beautiful(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('get_exchange_rates'),
            title="Курс ЦБ-РФ $/€ к ₽",
            description=update_cbr_template,
            thumb_url='https://image.flaticon.com/icons/png/512/893/893078.png',
            input_message_content=InputTextMessageContent(get_exchange_rates(),
                                                          parse_mode=ParseMode.HTML),
        ),
        InlineQueryResultArticle(
            id=get_inline_id('info_text'),
            title="О боте",
            description='Описание',
            thumb_url='https://i.imgur.com/gRBXXvn.png',
            input_message_content=InputTextMessageContent(info_text,
                                                          parse_mode=ParseMode.HTML, disable_web_page_preview=True),
        ),
    ]

    try:
        update.inline_query.answer(results, cache_time=0)
        logger.info('\n')
    except Exception as e:
        logger.error('Failed to update.inline_query.answer: ' + str(e))
        logger.info('\n')


def get_exchange_rates():
    try:
        old_data_usd = dbCBR.search(Query().cbrUSD.exists())
        old_data_eur = dbCBR.search(Query().cbrEUR.exists())
        last_timestamp = dbCBR.search(Query().cbrTS.exists())
        now_ts = calendar.timegm(time.gmtime())
        logger.info('get_exchange: now_ts:'f"{now_ts=}")

        if not last_timestamp:
            need_force_update = True
        else:
            diff = now_ts - last_timestamp[0]['cbrTS']
            logger.info('get_exchange: diff:'f"{diff=}")
            if diff >= 3600:
                need_force_update = True
            else:
                need_force_update = False

        if need_force_update:
            old_data_eur = None
            old_data_usd = None

        if not old_data_usd:
            logger.info('get_exchange: old_data_usd not found, update from cbr-xml-daily...')
            upd_ts = get_formatted_date(now_ts)
            data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
            USD = data['Valute']['USD']['Value']
            EUR = data['Valute']['EUR']['Value']
            dbCBR.drop_tables()
            dbCBR.insert({'cbrUSD': USD})
            dbCBR.insert({'cbrEUR': EUR})
            dbCBR.insert({'cbrTS': now_ts})
            return get_exchange_text(upd_ts, USD, EUR)
        else:
            logger.info('get_exchange: old_data_usd found')
            upd_ts = get_formatted_date(last_timestamp[0]['cbrTS'])
            return get_exchange_text(upd_ts, old_data_usd[0]['cbrUSD'], old_data_eur[0]['cbrEUR'])
    except Exception as e:
        logger.error('Failed to get_exchange_rates: ' + str(e))
        return error_template


def get_exchange_text(upd_ts, usd, eur):
    text = "Обновлено %s MSK" % upd_ts + "\n" \
                                         "USD: <b>%s</b>" % usd + " ₽\n" \
                                                                  "EUR: <b>%s</b>" % eur + " ₽\n" \
                                                                                           "Инфо от ЦБ-РФ"
    return text


def get_formatted_date(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%d.%m.%Y, %H:%M:%S")


# noinspection PyTypeChecker
def sync_with_db(userId, varType, varValue):
    user = db.search(UserQuery.id == userId)
    logger.info('sync_with_db:'f" {user=} "f" {userId=} "f" {varType=} "f" {varValue=} ")
    if not user:
        logger.info('sync_with_db: user not found')
        db.insert({'id': userId, varType: varValue})
        return varValue
    else:
        userByVarType = db.search((UserQuery.id == userId) & (UserQuery[varType].exists()))
        logger.info('sync_with_db: userByVarType:'f"{userByVarType=}")
        if not userByVarType:
            logger.info('sync_with_db: userByVarType none, update value...')
            db.update({'id': userId, varType: varValue}, UserQuery.id == userId)
            return varValue
        else:
            logger.info('sync_with_db: userByVarType exists, get value...')
            return user[0][varType]


def info(update: Update, _: CallbackContext):
    update.message.reply_text(info_text, disable_web_page_preview=True)


def ping(update: Update, _: CallbackContext):
    logger.info("ping request")
    update.message.reply_text('pong', disable_web_page_preview=True)


def anekdot1(update: Update, _: CallbackContext):
    update.message.reply_text(get_anekdot())


def anekdot2(update: Update, _: CallbackContext):
    update.message.reply_text(get_anekdot2())


def bashim(update: Update, _: CallbackContext):
    update.message.reply_text(get_bash_quote())


def get_bash_quote():
    try:
        resp = requests.get('http://bashorg.org/random')
        page = PyQ(resp.content)
        text = page('.quote:first').text()
        quote_id = page('.vote:first').text()
        return quote_id + "\r\n\r\n" + text
    except Exception as e:
        logger.error('Failed to get_bash_quote: ' + str(e))
        return error_template


def get_random_gay_user_from_csv():
    try:
        old_user_id = dbRANDOM.search(Query().gay_id.exists())
        old_user_name = dbRANDOM.search(Query().gay_name.exists())

        if not old_user_id:
            logger.info('get_random_gay: old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            user_name2 = random_user.get('name').to_numpy()
            logger.info('get_random_gay: UserName:'f"{user_name1[0]=}"f"{user_name2=}")
            if is_nan(user_name1):
                user_name = user_name2[0]
            else:
                user_name = user_name1[0]
            logger.info('get_random_gay: Random user:'f"{user_id[0]=}"f"{user_name=}")
            dbRANDOM.insert({'gay_id': int(user_id[0])})
            dbRANDOM.insert({'gay_name': str(user_name)})
            return get_user_link_text(user_id[0], user_name)
        else:
            logger.info('get_random_gay: old_user_id found')
            return get_user_link_text(old_user_id[0]['gay_id'], old_user_name[0]['gay_name'])
    except Exception as e:
        logger.error('Failed to get_random_gay_user_from_csv: ' + str(e))
        return error_template


def get_user_link_text(user_id, user_name):
    text = '<a href="tg://user?id=%s' % user_id + '">@%s' % user_name + '</a>'
    logger.info('get_user_link_text: 'f"{text=}")
    return text


def is_nan(num):
    return num != num


def get_random_beautiful_user_from_csv():
    try:
        old_user_id = dbRANDOM.search(Query().beautiful_id.exists())
        old_user_name = dbRANDOM.search(Query().beautiful_name.exists())

        if not old_user_id:
            logger.info('get_random_beautiful: old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            user_name2 = random_user.get('name').to_numpy()
            logger.info('get_random_beautiful: UserName:'f"{user_name1[0]=}"f"{user_name2=}")
            if is_nan(user_name1):
                user_name = user_name2[0]
            else:
                user_name = user_name1[0]
            logger.info('get_random_beautiful: Random user:'f"{user_id[0]=}"f"{user_name=}")
            dbRANDOM.insert({'beautiful_id': int(user_id[0])})
            dbRANDOM.insert({'beautiful_name': str(user_name)})
            return get_user_link_text(user_id[0], user_name)
        else:
            logger.info('get_random_beautiful: old_user_id found')
            return get_user_link_text(old_user_id[0]['beautiful_id'], old_user_name[0]['beautiful_name'])
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
    dispatcher.add_handler(CommandHandler("ping", ping, run_async=True))
    # dispatcher.add_handler(CommandHandler("anekdot1", anekdot1, run_async=True))
    # dispatcher.add_handler(CommandHandler("anekdot2", anekdot2, run_async=True))
    # dispatcher.add_handler(CommandHandler("bashim", bashim, run_async=True))
    dispatcher.add_handler(InlineQueryHandler(inlinequery, run_async=True))
    dispatcher.add_handler(ChosenInlineResultHandler(on_result_chosen, run_async=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
