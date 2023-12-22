from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from test import *

mainmenu_getsites = KeyboardButton('/get_sites')
mainmenu_getnews = KeyboardButton('/get_news')
mainmenu = ReplyKeyboardMarkup(resize_keyboard=True).row(mainmenu_getsites, mainmenu_getnews)



