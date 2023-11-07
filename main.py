from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.types import ParseMode, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
import os


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
bot_link = hlink("@proton_equalizer_bot", "https://t.me/proton_equalizer_bot")
mode = ParseMode.HTML


async def reply_to_user(kb, message, valid):
    if valid:
        await message.answer(f"what would you like me to do?", reply_markup=kb)
    else:
        await message.answer("hold on, that's not an audio")


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    chat_id = message["chat"]["id"]
    file = open("start_message.txt")
    text = file.read()
    try:
        os.mkdir(f"storage/{chat_id}")
    except FileExistsError:
        pass
    await message.answer(text)


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    file = open("help_message.txt")
    text = file.read()
    await message.answer(text)


@dp.message_handler(content_types=["any"])
async def voice_processing(message: types.Message):
    content = message.content_type
    kb = InlineKeyboardMarkup()
    valid = False
    print(content)
    if content == "audio":
        valid = True
        chat_id = message["chat"]["id"]
        path = f"storage/{chat_id}/test.mp3"
        btn_1 = InlineKeyboardButton("speed up", callback_data="speed")
        btn_2 = InlineKeyboardButton("slow down", callback_data="slow")
        kb.add(btn_1, btn_2)
        await message.audio.download(destination_file=path)
    await reply_to_user(kb, message, valid)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
