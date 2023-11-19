from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from pydub import AudioSegment

API_TOKEN = "6564932412:AAGh3RqEZQZvASeM_EOlH10Y2WSw1ZAFnHg"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=['audio'])
async def handle_audio(message: types.Message):
    # Скачиваем аудиофайл
    audio_path = f"audio_{message.from_user.id}.mp3"
    await message.audio.download(audio_path)

    # Создаем клавиатуру для выбора действия
    keyboard = InlineKeyboardMarkup()
    btn_slow = InlineKeyboardButton("Замедлить", callback_data='slow')
    btn_speed = InlineKeyboardButton("Ускорить", callback_data='speed')
    keyboard.row(btn_slow, btn_speed)

    await bot.send_message(message.from_user.id, "Что вы хотите сделать с аудио?", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback(callback_query: types.CallbackQuery):
    action = callback_query.data
    user_id = callback_query.from_user.id

    # Создаем клавиатуру для выбора скорости изменения аудио
    keyboard = InlineKeyboardMarkup()
    text = ""  # Инициализируем переменную text
    speed = 1.0  # Устанавливаем стандартную скорость по умолчанию

    # Для замедления
    if action == 'slow':
        btn_09 = InlineKeyboardButton("0.9", callback_data='slow_09')
        btn_08 = InlineKeyboardButton("0.8", callback_data='slow_08')
        btn_07 = InlineKeyboardButton("0.7", callback_data='slow_07')
        keyboard.row(btn_09, btn_08, btn_07)
        text = "Выберите скорость для замедления:"

    # Для ускорения
    elif action == 'speed':
        btn_12 = InlineKeyboardButton("1.2", callback_data='speed_12')
        btn_13 = InlineKeyboardButton("1.3", callback_data='speed_13')
        btn_14 = InlineKeyboardButton("1.4", callback_data='speed_14')
        keyboard.row(btn_12, btn_13, btn_14)
        text = "Выберите скорость для ускорения:"

    if text:
        await bot.send_message(user_id, text, reply_markup=keyboard)
        await callback_query.answer()  # Ответим, чтобы убрать "часики" в Telegram

    # Продолжение обработки выбора скорости...


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith(('slow_', 'speed_')))
async def process_speed_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    action, speed_value = callback_query.data.split('_')

    audio_path = f"audio_{user_id}.mp3"
    audio = AudioSegment.from_file(audio_path)

    # Устанавливаем скорость в зависимости от выбранной опции
    if action == 'slow':
        speed = float(f"0.{speed_value}")
    elif action == 'speed':
        speed = float(f"1.{speed_value}")

    edited_audio = audio.speedup(playback_speed=speed)
    output_path = f"edited_audio_{user_id}.mp3"
    edited_audio.export(output_path, format="mp3")

    with open(output_path, 'rb') as edited_file:
        await bot.send_audio(user_id, audio=edited_file)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
