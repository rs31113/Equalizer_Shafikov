from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.types import ParseMode, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
import os


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
bot_link = hlink("@proton_equalizer_bot", "https://t.me/proton_equalizer_bot")
mode = ParseMode.HTML


def reply_to_user(kb, message, valid):
    if valid:
        await message.answer(f"what would you like me to do?", reply_markup=kb)
    else:
        await message.answer("hold on, that's not an audio")


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    chat_id = message["chat"]["id"]
    try:
        os.mkdir(f"storage/{chat_id}")
    except FileExistsError:
        pass
    await message.answer("Start")


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    await message.answer("Help")


@dp.message_handler(content_types=["any"])
async def voice_processing(message: types.Message):
    content = message.content_type
    chat_id = message["chat"]["id"]
    path = f"storage/{chat_id}/test.mp3"
    kb = InlineKeyboardMarkup()
    btn_1 = InlineKeyboardButton("speed up", callback_data="speed")
    btn_2 = InlineKeyboardButton("slow down", callback_data="slow")
    kb.add(btn_1, btn_2)
    await message.voice.download(destination_file=path)
    await reply_to_user(kb, message, True)
