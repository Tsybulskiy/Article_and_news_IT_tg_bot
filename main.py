import array
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiomysql
from aiogram.utils.markdown import hlink
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

import filters
from keyboards import *
from config import *
from filters import *

bot = Bot(token=TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()

h = 0


class KZI(StatesGroup):
    filter = State()
    start = State()
    site_name = State()
    categories = State()
    links_categories = State()
    next_links_categories = State()
    links = State()
    next_links = State()
    starting_level_links = State()
    starting_level_next_links = State()
    feedback_insert = State()
    favourites_select = State()
    favourites_insert_categories = State()
    favourites_insert_links = State()
    favourites_categories = State()
    next_links_favourites_categories = State()
    next_links_favourites_links = State()
    get_news = State()
    next_news = State()


async def filter_start(message: types.Message, state: FSMContext):
    if message.text == "/get_sites":
        await get_sites(message, state)
    elif message.text == "/get_categories":
        await get_categories(message, state)
    elif message.text == "/starting_level":
        await starting_level(message, state)
    elif message.text == "/feedback":
        await feedback(message, state)
    elif message.text == "/favourites":
        await favourites(message, state)
    elif message.text == "/get_news":
        await get_news(message, state)
    else:
        await bot.send_message(message.chat.id, "Введите команду из списка доступных команд")


async def feedback(message: types.Message, state: FSMContext):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        user_id = message.from_user.id
        res = "INSERT INTO feedback (userid, username)  SELECT Id, UserName FROM users WHERE Id like %s"
        val = (user_id,)
        await cursor.execute(res, val)
        await conn.commit()
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, "Опишите проблему или предложите какое-либо улучшение",
                               reply_markup=markup, disable_web_page_preview=True)
        await state.set_state(KZI.feedback_insert.state)
        print("aa")
    except Exception as e:
        print(e)


async def feedback_insert(message: types.Message, state: FSMContext):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "SELECT idfeedback FROM feedback ORDER BY idfeedback DESC LIMIT 1"
        await cursor.execute(res)
        result = await cursor.fetchall()
        feedbackid = []
        for x in result:
            for c in x:
                feedbackid.append(c)
        if message.text == "Вернуться к списку команд":
            await state.finish()
            await start(message, state)
        else:
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            cursor = await conn.cursor()
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            res = "UPDATE feedback SET feedback = %s WHERE idfeedback = %s"
            val = (message.text, feedbackid)
            await cursor.execute(res, val)
            await conn.commit()
            btnback1 = KeyboardButton("Вернуться к списку команд")
            markup.add(btnback1)
            await cursor.close()
            conn.close()
            await bot.send_message(message.chat.id, "Спасибо за ваше сообщение", reply_markup=markup,
                                   disable_web_page_preview=True)
            await start(message, state)
    except Exception as e:
        print(e)


async def get_news(message: types.Message, state: FSMContext):
    try:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        global h, b
        cursor = await conn.cursor()
        res = "SELECT title FROM news where date = curdate() limit %s, 10"
        val = (h)
        await cursor.execute(res, val)
        await conn.commit()
        result = await cursor.fetchall()
        i = []
        for x in result:
            for c in x:
                i.append(c)
        res = "SELECT LINK FROM news WHERE date = curdate() limit %s, 10"
        val = (h)
        await cursor.execute(res, val)
        await conn.commit()
        result = await cursor.fetchall()
        global items
        items = []
        for x in result:
            for c in x:
                items.append(c)
        a = 'Новости за сегодня:' + '\n'
        for n in range(0, len(items)):
            b = "— " + i[n] + '\n'
            c = items[n]
            a = a + hlink(title=b, url=c)
        btn2 = KeyboardButton("Вернуться к списку команд")
        markup.add(btn2)
        btn4 = KeyboardButton("Добавить ссылку в избранное")
        markup.add(btn4)
        btn5 = KeyboardButton("Далее")
        markup.add(btn5)
        await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                               disable_web_page_preview=True)
        await state.set_state(KZI.next_news.state)
    except Exception as e:
        print(e)


async def next_button_news(message, state: FSMContext):
    if message.text == "Далее" and len(items) >= 10:
        global h
        h += 10
        await state.finish()
        await get_news(message, state)
    elif message.text == "Далее" and len(items) <= 10:
        h = 0
        await bot.send_message(message.chat.id, "Новости закончились")
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку команд':
        h = 0
        await state.finish()
        await start(message, state)
    elif message.text == 'Добавить ссылку в избранное':
        await state.finish()
        await favourites_insert(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру")
        await state.set_state(KZI.next_news.state)


async def start(message: types.Message, state: FSMContext):
    try:
        markup = ReplyKeyboardRemove()
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "SELECT Id FROM users"
        await cursor.execute(res)
        result = await cursor.fetchall()
        user_items = []
        for x in result:
            for c in x:
                user_items.append(c)
        user_id = message.from_user.id
        username = message.from_user.username
        if user_id not in user_items:
            markup = ReplyKeyboardRemove()
            sql = "INSERT INTO users (Id, UserName) VALUES (%s, %s)"
            val = (user_id, username,)
            await cursor.execute(sql, val)
            await conn.commit()
            await bot.send_message(message.from_user.id,
                                   "Привет, {0.first_name}! Ты впервые в этом боте, поэтому лови список команд".format(
                                       message.from_user) + '\n' +
                                   "Доступные команды:" + '\n' +
                                   "Получить ссылки на статьи по ИБ - /get_sites" + '\n' +
                                   "Получить новости по ИБ за сегодня - /get_news" + '\n' +
                                   "Получить категории со всех сайтов - /get_categories" + '\n' +
                                   "Введите эту команду, если у вас начальный уровень в сфере ИБ - /starting_level" + '\n' +
                                   "Введите эту команду, если хотите увидеть свои избранные категории или ссылки - /favourites" + '\n' +
                                   "Введите эту команду, если хотите оставить feedback - /feedback" + '\n' +
                                   "Либо просто напишите админу бота @dagkspwe"
                                   , reply_markup=markup)
        elif user_id in user_items:
            markup = ReplyKeyboardRemove()
            await bot.send_message(message.from_user.id,
                                   "Привет, {0.first_name}! Рад видеть тебя ещё раз".format(message.from_user) + '\n' +
                                   "Доступные команды:" + '\n' +
                                   "Получить ссылки на статьи по ИБ - /get_sites" + '\n' +
                                   "Получить новости по ИБ за сегодня - /get_news" + '\n' +
                                   "Получить категории со всех сайтов - /get_categories" + '\n' +
                                   "Введите эту команду, если у вас начальный уровень в сфере ИБ - /starting_level" + '\n' +
                                   "Введите эту команду, если хотите увидеть свои избранные категории или ссылки - /favourites" + '\n' +
                                   "Введите эту команду, если хотите оставить feedback - /feedback" + '\n' +
                                   "Либо просто напишите админу бота @dagkspwe"
                                   , reply_markup=markup)
        await state.set_state(KZI.filter.state)
    except Exception as e:
        print(e)


async def get_sites(message: types.Message, state: FSMContext):
    try:
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        res = "SELECT SiteName FROM sites where sitecategory='Article'"
        await cursor.execute(res)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        a = 'Имеющиеся сайты:' + '\n'
        for item in items:
            filters.sites_items.append(item)
            a = a + "• " + item + '\n'
        keys = items
        row = [KeyboardButton(x) for x in keys[:1000]]
        markup.add(*row)
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, a, reply_markup=markup, disable_web_page_preview=True)
        await state.set_state(KZI.site_name.state)
    except Exception as e:
        print(e)


async def get_categories(message: types.Message, state: FSMContext):
    try:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "select distinct category from links"
        await cursor.execute(res)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        a = 'Категории, которые есть:' + '\n'
        for item in items:
            filters.get_categories_items.append(item)
            a = a + "• " + item + '\n'
        keys = items
        row = [KeyboardButton(x) for x in keys[:1000]]
        markup.add(*row)
        btn1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btn1)
        await message.answer(a, reply_markup=markup)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, "Выберите категорию")
        await state.set_state(KZI.links_categories.state)
    except Exception as e:
        print(e)


async def links_categories(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к выбору категорий':
            await state.finish()
            await get_categories(message, state)
        elif message.text in filters.get_categories_items:
            global category
            category = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к выбору категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить категорию в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn4)
            btn5 = KeyboardButton("Далее")
            markup.add(btn5)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links_categories.state)
        else:
            await bot.send_message(message.chat.id,
                                   "Ты написал что-то не то, нажми на клавиатуру или пошли мне категорию из списка доступных категорий")
            await state.set_state(KZI.links_categories.state)
    except Exception as e:
        print(e)


async def next_links_categories(message: types.Message, state: FSMContext):
    try:
        print(message.text)
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к выбору категорий':
            await state.finish()
            await get_categories(message, state)
        elif message.text == 'Добавить категорию в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == 'Добавить ссылку в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == "Далее":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к выбору категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить категорию в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn4)
            btn5 = KeyboardButton("Далее")
            markup.add(btn5)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links_categories.state)
    except Exception as e:
        print(e)


async def next_button_categories(message, state: FSMContext):
    if message.text == "Далее" and len(items) >= 10:
        global h
        h += 10
        await state.finish()
        await next_links_categories(message, state)
    elif message.text == "Далее" and len(items) <= 10:
        h = 0
        await bot.send_message(message.chat.id, "Статьи закончились")
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку команд':
        h = 0
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к выбору категорий':
        h = 0
        await state.finish()
        await get_categories(message, state)
    elif message.text == 'Добавить категорию в избранное':
        await state.finish()
        await favourites_insert(message, state)
    elif message.text == 'Добавить ссылку в избранное':
        await state.finish()
        await favourites_insert(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру")
        await state.set_state(KZI.next_links.state)


async def get_sites_categories(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text in filters.sites_items:
            global sait
            sait = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            cursor = await conn.cursor()
            res = "select distinct category from links where link regexp (select sitename from sites where sitename like %s)"
            val = (sait,)
            await cursor.execute(res, val)
            result = await cursor.fetchall()
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Категории, которые есть на этом сайте:' + '\n'
            for item in items:
                filters.categories_items.append(item)
                a = a + "• " + item + '\n'
            keys = items
            row = [KeyboardButton(x) for x in keys[:1000]]
            markup.add(*row)
            btnback = KeyboardButton("Вернуться к выбору сайтов")
            markup.add(btnback)
            btnback1 = KeyboardButton("Вернуться к списку команд")
            markup.add(btnback1)
            await message.answer(a, reply_markup=markup)
            await cursor.close()
            conn.close()
            await bot.send_message(message.chat.id, "Выберите категорию")
            await state.set_state(KZI.links.state)
        else:
            await bot.send_message(message.chat.id,
                                   "Ты написал что-то не то, нажми на клавиатуру или пошли мне ссылку из списка доступных сайтов")
            await state.set_state(KZI.site_name.state)
    except Exception as e:
        print(e)


async def get_links(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к выбору сайтов':
            await state.finish()
            await get_sites(message, state)
        elif message.text in filters.categories_items:
            global category
            category = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s and link regexp (select sitename from sites where sitename like %s) limit %s, 10"
            val = (category, sait, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s and link regexp (select sitename from sites where sitename like %s) limit %s, 10"
            val = (category, sait, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к выбору сайтов")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить категорию в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn4)
            btn5 = KeyboardButton("Далее")
            markup.add(btn5)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links.state)
        else:
            await bot.send_message(message.chat.id,
                                   "Ты написал что-то не то, нажми на клавиатуру или пошли мне категорию из списка доступных категорий")
            await state.set_state(KZI.links.state)
    except Exception as e:
        print(e)


async def next_links(message: types.Message, state: FSMContext):
    try:
        print(message.text)
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к выбору сайтов':
            await state.finish()
            await get_sites(message, state)
        elif message.text == 'Добавить категорию в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == 'Добавить ссылку в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == "Далее":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s and link regexp (select sitename from sites where sitename like %s) limit %s, 10"
            val = (category, sait, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s and link regexp (select sitename from sites where sitename like %s) limit %s, 10"
            val = (category, sait, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к выбору сайтов")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить категорию в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Добавить категорию в избранное")
            markup.add(btn4)
            btn5 = KeyboardButton("Далее")
            markup.add(btn5)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links.state)
    except Exception as e:
        print(e)


async def next_button_sites(message, state: FSMContext):
    if message.text == "Далее" and len(items) >= 10:
        global h
        h += 10
        await state.finish()
        await next_links(message, state)
    elif message.text == "Далее" and len(items) <= 10:
        h = 0
        await bot.send_message(message.chat.id, "Статьи закончились")
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку команд':
        h = 0
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к выбору сайтов':
        h = 0
        await state.finish()
        await get_sites(message, state)
    elif message.text == 'Добавить категорию в избранное':
        await state.finish()
        await favourites_insert(message, state)
    elif message.text == 'Добавить ссылку в избранное':
        await state.finish()
        await favourites_insert(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру")
        await state.set_state(KZI.next_links.state)


async def starting_level(message, state: FSMContext):
    try:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "select distinct category from starting_level"
        await cursor.execute(res)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        a = 'Категории, которые подойдут для начинающих:' + '\n'
        for item in items:
            starting_level_categories_items.append(item)
            a = a + "• " + item + '\n'
        keys = items
        row = [KeyboardButton(x) for x in keys[:1000]]
        markup.add(*row)
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await message.answer(a, reply_markup=markup)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, "Выберите категорию")
        await state.set_state(KZI.starting_level_links.state)
    except Exception as e:
        print(e)


async def starting_level_links(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text in filters.starting_level_categories_items:
            global category
            category = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к списку категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Далее")
            markup.add(btn3)
            btn4 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn4)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.starting_level_next_links.state)
        else:
            await bot.send_message(message.chat.id,
                                   "Ты написал что-то не то, нажми на клавиатуру или пошли мне категорию из списка доступных категорий")
            await state.set_state(KZI.starting_level_links.state)
    except Exception as e:
        print(e)


async def starting_level_next_links(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к списку категорий':
            await state.finish()
            await starting_level(message, state)
        elif message.text == 'Добавить ссылку в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == "Далее":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            print(len(items))
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к списку категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Далее")
            markup.add(btn3)
            btn4 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn4)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.starting_level_next_links.state)
    except Exception as e:
        print(e)


async def starting_level_next_links_button(message, state: FSMContext):
    if message.text == "Далее" and len(items) >= 10:
        global h
        h += 10
        await state.finish()
        await starting_level_next_links(message, state)
    elif message.text == "Далее" and len(items) <= 10:
        h = 0
        await bot.send_message(message.chat.id, "Статьи закончились")
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку команд':
        h = 0
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку категорий':
        h = 0
        await state.finish()
        await starting_level(message, state)
    elif message.text == 'Добавить ссылку в избранное':
        await state.finish()
        await favourites_insert(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру")
        await state.set_state(KZI.starting_level_next_links.state)


async def favourites(message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_id = message.from_user.id
    btn1 = KeyboardButton("Категории")
    markup.add(btn1)
    btn2 = KeyboardButton("Ссылки на статьи")
    markup.add(btn2)
    btn3 = KeyboardButton("Вернуться к списку команд")
    markup.add(btn3)
    await bot.send_message(message.chat.id, "Выберите нужный раздел избранного", reply_markup=markup, parse_mode='html',
                           disable_web_page_preview=True)
    await state.set_state(KZI.favourites_select.state)


async def favourites_select(message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    user_id = message.from_user.id
    global items
    if message.text == "Категории" or message.text == "Вернуться к выбору избранных категорий":
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "select FavouriteCategory from favourites where UserId = %s"
        val = (user_id,)
        await cursor.execute(res, val)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        a = 'Категории, которые есть в избранном:' + '\n'
        keys = []
        for item in items:
            if str(item) not in "None":
                filters.get_categories_items.append(item)
                keys.append(item)
                a = a + "• " + str(item) + '\n'
        row = [KeyboardButton(x) for x in keys[:1000]]
        markup.add(*row)
        btn1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btn1)
        await message.answer(a, reply_markup=markup)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, "Выберите категорию")
        await state.set_state(KZI.favourites_categories.state)
    elif message.text == "Ссылки на статьи":
        global h, b
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "select FavouriteLink from favourites where UserId = %s and FavouriteLink is not null limit %s, 10"
        val = (user_id, h)
        await conn.commit()
        await cursor.execute(res, val)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        for item in items:
            filters.distinct_links_items.append(item)
        title = []
        res = "SELECT title FROM favourites where UserId = %s and Title  is not null limit %s, 10"
        val = (user_id, h)
        await cursor.execute(res, val)
        await conn.commit()
        result = await cursor.fetchall()
        for o in result:
            for c in o:
                title.append(c)
        a = 'Ссылки, которые есть в избранном:' + '\n'
        for n in range(0, len(items)):
            b = "— " + title[n] + '\n'
            c = items[n]
            a = a + hlink(title=b, url=c)
        btn1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btn1)
        btn2 = KeyboardButton("Далее")
        markup.add(btn2)
        await cursor.close()
        conn.close()
        distinct_links_items.clear()
        title.clear()
        await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                               disable_web_page_preview=True)
        await state.set_state(KZI.next_links_favourites_links.state)
    elif message.text == "Вернуться к списку команд":
        await state.finish()
        await start(message, state)
    else:
        await bot.send_message(message.chat.id, "Выберите нужный раздел избранного", reply_markup=markup,
                               parse_mode='html',
                               disable_web_page_preview=True)
        await state.set_state(KZI.favourites_select.state)


async def favourites_categories(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text in filters.get_categories_items:
            global category
            category = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к выбору избранных категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Далее")
            markup.add(btn4)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links_favourites_categories.state)
        else:
            await bot.send_message(message.chat.id,
                                   "Ты написал что-то не то, нажми на клавиатуру или пошли мне категорию из списка доступных категорий")
            await state.set_state(KZI.favourites_categories.state)
    except Exception as e:
        print(e)


async def next_links_favourites_categories(message: types.Message, state: FSMContext):
    try:
        print(message.text)
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к выбору избранных категорий':
            await state.finish()
            await favourites_select(message, state)
        elif message.text == 'Добавить категорию в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == 'Добавить ссылку в избранное':
            await state.finish()
            await favourites_insert(message, state)
        elif message.text == "Далее":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            global h, b
            cursor = await conn.cursor()
            res = "SELECT title FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            i = []
            for x in result:
                for c in x:
                    i.append(c)
            res = "SELECT link FROM links where category like %s limit %s, 10"
            val = (category, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            a = 'Статьи из заданной категории:' + '\n'
            for n in range(0, len(items)):
                b = "— " + i[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            btn1 = KeyboardButton("Вернуться к выбору избранных категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Далее")
            markup.add(btn4)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links_favourites_categories.state)
    except Exception as e:
        print(e)


async def next_button_favourites_categories(message, state: FSMContext):
    if message.text == "Далее" and len(items) >= 10:
        global h
        h += 10
        await state.finish()
        await next_links_favourites_categories(message, state)
    elif message.text == "Далее" and len(items) <= 10:
        h = 0
        await bot.send_message(message.chat.id, "Статьи закончились")
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку команд':
        h = 0
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к выбору избранных категорий':
        h = 0
        await state.finish()
        await favourites_select(message, state)
    elif message.text == 'Добавить ссылку в избранное':
        await state.finish()
        await favourites_insert(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру")
        await state.set_state(KZI.next_links.state)


async def next_links_favourites_links(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        if message.text == 'Вернуться к списку команд':
            await state.finish()
            await start(message, state)
        elif message.text == 'Вернуться к выбору избранных категорий':
            await state.finish()
            await favourites_select(message, state)
        elif message.text == "Далее":
            global h, b
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                          user='root', password='12345678', db='bot',
                                          loop=loop)
            cursor = await conn.cursor()
            res = "select FavouriteLink from favourites where UserId = %s and FavouriteLink is not null limit %s, 10"
            val = (user_id, h)
            await conn.commit()
            await cursor.execute(res, val)
            result = await cursor.fetchall()
            global items
            items = []
            for x in result:
                for c in x:
                    items.append(c)
            for item in items:
                filters.distinct_links_items.append(item)
            title = []
            res = "SELECT title FROM favourites where UserId = %s and FavouriteLink is not null limit %s, 10"
            val = (user_id, h)
            await cursor.execute(res, val)
            await conn.commit()
            result = await cursor.fetchall()
            for o in result:
                for c in o:
                    title.append(c)
            a = 'Ссылки, которые есть в избранном:' + '\n'
            for n in range(0, len(items)):
                b = "— " + title[n] + '\n'
                c = items[n]
                a = a + hlink(title=b, url=c)
            await cursor.close()
            conn.close()
            btn1 = KeyboardButton("Вернуться к выбору избранных категорий")
            markup.add(btn1)
            btn2 = KeyboardButton("Вернуться к списку команд")
            markup.add(btn2)
            btn3 = KeyboardButton("Добавить ссылку в избранное")
            markup.add(btn3)
            btn4 = KeyboardButton("Далее")
            markup.add(btn4)
            await bot.send_message(message.chat.id, a, reply_markup=markup, parse_mode='html',
                                   disable_web_page_preview=True)
            await state.set_state(KZI.next_links_favourites_links.state)
    except Exception as e:
        print(e)


async def next_button_favourites_links(message, state: FSMContext):
    if message.text == "Далее" and len(items) >= 10:
        global h
        h += 10
        await state.finish()
        await next_links_favourites_links(message, state)
    elif message.text == "Далее" and len(items) <= 10:
        h = 0
        await bot.send_message(message.chat.id, "Статьи закончились")
        await state.finish()
        await start(message, state)
    elif message.text == 'Вернуться к списку команд':
        h = 0
        await state.finish()
        await start(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру")
        await state.set_state(KZI.next_links.state)


async def favourites_insert(message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                  user='root', password='12345678', db='bot',
                                  loop=loop)
    cursor = await conn.cursor()
    user_id = message.from_user.id
    res = "INSERT INTO favourites (UserId)  VALUES (%s)"
    val = (user_id,)
    await cursor.execute(res, val)
    await conn.commit()
    print(message.text)
    if message.text == "Добавить категорию в избранное":
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "select distinct category from links"
        await cursor.execute(res)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        a = 'Категории, которые есть:' + '\n'
        for item in items:
            filters.get_categories_items.append(item)
            a = a + "• " + item + '\n'
        keys = items
        row = [KeyboardButton(x) for x in keys[:1000]]
        markup.add(*row)
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await message.answer(a, reply_markup=markup)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id,
                               "Выберите понравившуюся вам категорию из списка, вы можете как написать вручную, так и воспользоваться клавиатурой")
        await state.set_state(KZI.favourites_insert_categories.state)
    elif message.text == "Добавить ссылку в избранное":
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "select Link from links"
        await cursor.execute(res)
        result = await cursor.fetchall()
        items = []
        for x in result:
            for c in x:
                items.append(c)
        for item in items:
            filters.get_links_items.append(item)
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id,
                               "Выберите понравившуюся вам статью из списка ранее, скопируйте ссылку и отправьте мне",
                               reply_markup=markup)
        await state.set_state(KZI.favourites_insert_links.state)


async def favourites_insert_categories(message, state: FSMContext):
    conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                  user='root', password='12345678', db='bot',
                                  loop=loop)
    cursor = await conn.cursor()
    res = "SELECT Id FROM favourites ORDER BY Id DESC LIMIT 1"
    await cursor.execute(res)
    result = await cursor.fetchall()
    favouritesid = []
    for x in result:
        for c in x:
            favouritesid.append(c)
            print(favouritesid)
    await cursor.close()
    conn.close()
    if message.text == 'Вернуться к списку команд':
        await state.finish()
        await start(message, state)
    elif message.text in filters.get_categories_items:
        global category
        category = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res = "UPDATE favourites SET FavouriteCategory = %s WHERE Id = %s"
        val = (category, favouritesid)
        print(category, favouritesid)
        await cursor.execute(res, val)
        await conn.commit()
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, "Категория успешно записана в избранное")
        await start(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру или пошли мне категорию из списка доступных категорий")
        await state.set_state(KZI.favourites_insert_categories.state)


async def favourites_insert_links(message, state: FSMContext):
    conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                  user='root', password='12345678', db='bot',
                                  loop=loop)
    cursor = await conn.cursor()
    res = "SELECT Id FROM favourites ORDER BY Id DESC LIMIT 1"
    await cursor.execute(res)
    result = await cursor.fetchall()
    favouritesid = []
    for x in result:
        for c in x:
            favouritesid.append(c)
            print(favouritesid)
    await cursor.close()
    conn.close()
    if message.text == 'Вернуться к списку команд':
        await state.finish()
        await start(message, state)
    elif message.text in filters.get_links_items:
        global link
        link = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                      user='root', password='12345678', db='bot',
                                      loop=loop)
        cursor = await conn.cursor()
        res1 = "UPDATE favourites SET FavouriteLink = %s WHERE Id = %s"
        val1 = (link, favouritesid)
        await cursor.execute(res1, val1)
        await conn.commit()
        res2 = "SELECT Title FROM links where link= %s"
        val2 = (link,)
        await cursor.execute(res2, val2)
        result = await cursor.fetchall()
        titles = []
        for x in result:
            for c in x:
                titles.append(c)
        res3 = "UPDATE favourites SET Title = %s WHERE Id = %s"
        val3 = (titles, favouritesid)
        await cursor.execute(res3, val3)
        await conn.commit()
        btnback1 = KeyboardButton("Вернуться к списку команд")
        markup.add(btnback1)
        await cursor.close()
        conn.close()
        await bot.send_message(message.chat.id, "Статья успешно записана в избранное")
        await start(message, state)
    else:
        await bot.send_message(message.chat.id,
                               "Ты написал что-то не то, нажми на клавиатуру или пошли мне категорию из списка доступных категорий")
        await state.set_state(KZI.favourites_insert_categories.state)


def register_client():
    dp.register_message_handler(filter_start, state=KZI.filter)
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(get_sites, commands=['get_sites'])
    dp.register_message_handler(feedback, commands=['feedback'])
    dp.register_message_handler(get_categories, commands=['get_categories'])
    dp.register_message_handler(next_button_categories, state=KZI.next_links_categories)
    dp.register_message_handler(links_categories, state=KZI.links_categories)
    dp.register_message_handler(get_sites_categories, state=KZI.site_name)
    dp.register_message_handler(get_links, state=KZI.links)
    dp.register_message_handler(next_button_sites, state=KZI.next_links)
    dp.register_message_handler(starting_level, commands=['starting_level'])
    dp.register_message_handler(starting_level_links, state=KZI.starting_level_links)
    dp.register_message_handler(starting_level_next_links_button, state=KZI.starting_level_next_links)
    dp.register_message_handler(feedback_insert, state=KZI.feedback_insert)
    dp.register_message_handler(favourites, commands=['favourites'])
    dp.register_message_handler(favourites_select, state=KZI.favourites_select)
    dp.register_message_handler(favourites_insert_categories, state=KZI.favourites_insert_categories)
    dp.register_message_handler(favourites_insert_links, state=KZI.favourites_insert_links)
    dp.register_message_handler(favourites_categories, state=KZI.favourites_categories)
    dp.register_message_handler(next_button_favourites_categories, state=KZI.next_links_favourites_categories)
    dp.register_message_handler(next_button_favourites_links, state=KZI.next_links_favourites_links)
    dp.register_message_handler(get_news, state=KZI.get_news)
    dp.register_message_handler(next_button_news, state=KZI.next_news)


register_client()

# async def on_startup(dp: Dispatcher):
# print('~~~ Bot успешно запущен! ~~~')
# scheduler.add_job(news_1.get_news_from_cisoclub, 'interval', seconds=5)
# scheduler.add_job(news_1.get_news_from_securitymedia, 'interval', seconds=5)

# scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
# scheduler.start()
executor.start_polling(dp, skip_updates=True)  # on_startup=on_startup)
