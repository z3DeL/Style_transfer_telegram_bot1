import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton



from copy import deepcopy


from style_transfer import *
from config import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

photo_buffer = {}

start_kb = InlineKeyboardMarkup()
start_kb.add( InlineKeyboardButton('Перенос стиля',
                                    callback_data='1_st') )
cancel_kb = InlineKeyboardMarkup()
cancel_kb.add( InlineKeyboardButton('Отмена', callback_data='main_menu'))

class InfoAboutUser:
    def __init__(self):
        self.photos = []


@dp.message_handler(commands=['start'])
async def send_welcome(message):

    await bot.send_message(message.chat.id,
        f"Привет, {message.from_user.first_name}!\n " +
        "что делаем?", reply_markup=start_kb)

    photo_buffer[message.chat.id] = InfoAboutUser()


@dp.message_handler(commands=['help'])
async def send_help(message):

    await bot.send_message(message.chat.id,
        "что делаем?", reply_markup=start_kb)


@dp.callback_query_handler(lambda c: c.data == 'main_menu')
async def main_menu(callback_query):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text("что делаем?:")
    await callback_query.message.edit_reply_markup(reply_markup=start_kb)


@dp.callback_query_handler(lambda c: c.data == '1_st')
async def st_1_style(callback_query):
    await bot.answer_callback_query(callback_query.id)

    if callback_query.from_user.id not in photo_buffer:
        photo_buffer[callback_query.from_user.id] = InfoAboutUser()


    await callback_query.message.edit_text(
                                            "Отправь мне картинку, стиль с которой нужно перенести. ")

    photo_buffer[callback_query.from_user.id].need_photos = 2

    await callback_query.message.edit_reply_markup(reply_markup=cancel_kb)


@dp.message_handler(content_types=['photo', 'document'])
async def get_image(message):
    img = message.photo[-1]

    file_info = await bot.get_file(img.file_id)
    photo = await bot.download_file(file_info.file_path)

    photo_buffer[message.chat.id].photos.append(photo)

    if photo_buffer[message.chat.id].need_photos == 2:
        photo_buffer[message.chat.id].need_photos = 1

        await bot.send_message(message.chat.id,
                                       "Отправь фото, на которое нужно перенести стиль ",
                                       reply_markup=cancel_kb)

    elif photo_buffer[message.chat.id].need_photos == 1:
        await bot.send_message(message.chat.id, "ожидайте")
        output = Simple_style_transfer([photo_buffer[message.chat.id].photos[0], photo_buffer[message.chat.id].photos[1]])

        await bot.send_document(message.chat.id, deepcopy(output))
        await bot.send_photo(message.chat.id, output)

        await bot.send_message(message.chat.id,
                                   "что еще будем делать?", reply_markup=start_kb)

        del photo_buffer[message.chat.id]


@dp.message_handler(content_types=['text'])
async def get_text(message):

    await bot.send_message(message.chat.id,
                           "вот мои функции:", reply_markup=start_kb)





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
