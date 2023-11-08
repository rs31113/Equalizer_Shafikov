from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.types import ParseMode, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
import os


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
bot_link = hlink("@proton_equalizer_bot", "https://t.me/proton_equalizer_bot")
mode = ParseMode.HTML


def clear_storage(chat_id):
    for file in os.listdir(f"storage/{chat_id}"):
        os.remove(f"storage/{chat_id}/{file}")


async def request_processing(message, chat_id):
    await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    await message.answer("processing...")


async def reply_to_user(kb, message, valid):
    if valid:
        await message.answer(
            f"what would you like me to do?",
            reply_markup=kb,
        )
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
    if content == "audio":
        valid = True
        chat_id = message["chat"]["id"]
        source_path = f"storage/{chat_id}/source.mp3"
        btn_1 = InlineKeyboardButton("speed up", callback_data="speed")
        btn_2 = InlineKeyboardButton("slow down", callback_data="slow")
        kb.add(btn_1, btn_2)
        await message.audio.download(destination_file=source_path)
    await reply_to_user(kb, message, valid)


@dp.callback_query_handler(text=["speed"])
async def speed_up(callback_query: types.CallbackQuery):
    chat_id = callback_query.message['chat']['id']
    await request_processing(callback_query.message, chat_id)
    source_path = f"storage/{chat_id}/source.mp3"
    result_path = f"storage/{chat_id}/result.mp3"
    await callback_query.message.answer_document(
        InputFile(result_path),
        caption=bot_link,
        parse_mode=mode,
    )
    clear_storage(chat_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
