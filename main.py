import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery

import regular_update
from keyboards import main, callback
import smartphone

logging.basicConfig(level=logging.ERROR,
                    filename='bot.log',
                    format='%(asctime)s %(name)s: %(levelname)s [%(process)d] %(message)s')
bot = Bot(token='...')

dp = Dispatcher(bot)
b = main.Brand()
m = ''
brand_name = ''
model_name = ''
ram = ''
storage = ''


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    k = b.keyboard_generator()
    await message.answer('Выберите смартфон:', reply_markup=k)


@dp.callback_query_handler(callback.choice.filter(which='start'))
async def to_beginning(call: CallbackQuery):
    await call.answer(cache_time=1)
    global b
    b._items_used = 0
    k = b.keyboard_generator()
    await call.message.edit_reply_markup(reply_markup=k)


@dp.callback_query_handler(callback.choice.filter(what='brand'))
async def brand_choice(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    item = callback_data.get('which')
    if item == 'next':
        b.next_page()
        k = b.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    elif item == 'prev':
        b.prev_page()
        k = b.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    else:
        global brand_name
        brand_name = item
        b.increase_top_value(brand_name)
        global m
        m = main.Model(brand_name)
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)


@dp.callback_query_handler(callback.choice.filter(what='model'))
async def model_choice(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    item = callback_data.get('which')
    if item == 'next':
        m.next_page()
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    elif item == 'prev':
        m.prev_page()
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    else:
        global model_name
        model_name = item
        r = main.Ram(brand_name, model_name)
        ram_value_list = r.items
        if len(ram_value_list) > 1:
            k = r.keyboard_generator()
            await call.message.edit_reply_markup(reply_markup=k)
        else:
            global ram
            ram = ram_value_list[0]
            s = main.Storage(brand_name, model_name, ram)
            storage_value_list = s.items
            if len(storage_value_list) > 1:
                k = s.keyboard_generator()
                await call.message.edit_reply_markup(reply_markup=k)
            else:
                global storage
                storage = storage_value_list[0]
                f = smartphone.FinaleMessage(brand_name, model_name, ram, storage)
                img = f.image()
                about = f.specifications()
                k = f.generate()
                await call.message.delete_reply_markup()
                await call.message.answer_photo(img)
                await call.message.answer(about, reply_markup=k)


@dp.callback_query_handler(callback.choice.filter(what='ram'))
async def ram_choice(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    item = callback_data.get('which')
    if item == 'next':
        m.next_page()
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    elif item == 'prev':
        m.prev_page()
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    else:
        global ram
        ram = item
        s = main.Storage(brand_name, model_name, ram)
        storage_value_list = s.items
        if len(storage_value_list) > 1:
            k = s.keyboard_generator()
            await call.message.edit_reply_markup(reply_markup=k)
        else:
            global storage
            storage = storage_value_list[0]
            f = smartphone.FinaleMessage(brand_name, model_name, ram, storage)
            img = f.image()
            about = f.specifications()
            k = f.generate()
            await call.message.delete_reply_markup()
            await call.message.answer_photo(img)
            await call.message.answer(about, reply_markup=k)


@dp.callback_query_handler(callback.choice.filter(what='storage'))
async def storage_choice(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=1)
    item = callback_data.get('which')
    if item == 'next':
        m.next_page()
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    elif item == 'prev':
        m.prev_page()
        k = m.keyboard_generator()
        await call.message.edit_reply_markup(reply_markup=k)
    else:
        global storage
        storage = item
        f = smartphone.FinaleMessage(brand_name, model_name, ram, storage)
        img = f.image()
        about = f.specifications()
        k = f.generate()
        await call.message.delete_reply_markup()
        await call.message.answer_photo(img)
        await call.message.answer(about, reply_markup=k)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    regular_update.ekatalog_update()

# реализовать парсинг искомого телефона на авито и юле parsing/Main-894
# добавить результат в базу смартфонов с екаталога "smarphones"
# если происходит парсинг, реализовать выдачу последовательную выдачу финального сообщения:
# сперва то, что есть в базе (характеристики и имг), после парсинга цены
