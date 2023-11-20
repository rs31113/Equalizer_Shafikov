from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.types import ParseMode, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
import os
from pydub import AudioSegment
import sox
import io
import subprocess


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
bot_link = hlink("@proton_equalizer_bot", "https://t.me/proton_equalizer_bot")
mode = ParseMode.HTML


def clear_storage(chat_id):
    for file in os.listdir(f"storage/{chat_id}"):
        os.remove(f"storage/{chat_id}/{file}")


async def request_processing(message, chat_id):
    await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    await message.answer("обрабатываю...")


async def reply_to_user(kb, message, valid):
    if valid:
        await message.answer(
            f"какие настройки хотите применить?",
            reply_markup=kb,
        )
    else:
        await message.answer("кажется, это не аудио :(")


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
        btn_3 = InlineKeyboardButton("bass boost", callback_data="bass")
        btn_4 = InlineKeyboardButton("vocals boost", callback_data="vocals")
        kb.add(btn_1, btn_2, btn_3, btn_4)
        await message.audio.download(destination_file=source_path)
    await reply_to_user(kb, message, valid)


@dp.callback_query_handler(text=["vocals"])
async def vocals_boost(callback_query: types.CallbackQuery):
    chat_id = callback_query.message["chat"]["id"]
    await request_processing(callback_query.message, chat_id)
    path = f"storage/{chat_id}/"

    subprocess.run(["sox", f"{path}source.mp3", f"{path}vocals_boost.mp3", "treble", "7"])

    await callback_query.message.answer_document(
        InputFile(f"{path}vocals_boost.mp3"),
        caption=bot_link,
        parse_mode=mode,
    )
    clear_storage(chat_id)


@dp.callback_query_handler(text=["bass"])
async def bass_boost(callback_query: types.CallbackQuery):
    chat_id = callback_query.message["chat"]["id"]
    await request_processing(callback_query.message, chat_id)
    path = f"storage/{chat_id}/"

    subprocess.run(["sox", f"{path}source.mp3", f"{path}bass_boost.mp3", "bass", "7"])

    await callback_query.message.answer_document(
        InputFile(f"{path}bass_boost.mp3"),
        caption=bot_link,
        parse_mode=mode,
    )
    clear_storage(chat_id)


@dp.callback_query_handler(text=["speed"])
async def speed_up(callback_query: types.CallbackQuery):
    chat_id = callback_query.message["chat"]["id"]
    await request_processing(callback_query.message, chat_id)
    path = f"storage/{chat_id}/"

    audio = AudioSegment.from_file(f"{path}source.mp3")
    slowed_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 1.2)})
    slowed_audio = slowed_audio.set_frame_rate(audio.frame_rate)
    slowed_audio.export(f"{path}speed.mp3", format="mp3")
    effects = sox.Transformer()
    effects.reverb(reverberance=30)
    effects.build(input_filepath=f"{path}speed.mp3", output_filepath=f"{path}speed_up.mp3")

    await callback_query.message.answer_document(
        InputFile(f"{path}speed_up.mp3"),
        caption=bot_link,
        parse_mode=mode,
    )
    clear_storage(chat_id)


@dp.callback_query_handler(text=["slow"])
async def slowed_reverb(callback_query: types.CallbackQuery):
    chat_id = callback_query.message["chat"]["id"]
    await request_processing(callback_query.message, chat_id)
    path = f"storage/{chat_id}/"

    audio = AudioSegment.from_file(f"{path}source.mp3")
    slowed_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.80)})
    slowed_audio = slowed_audio.set_frame_rate(audio.frame_rate)
    slowed_audio.export(f"{path}slowed.mp3", format="mp3")
    effects = sox.Transformer()
    effects.reverb(reverberance=30)
    effects.build(input_filepath=f"{path}slowed.mp3", output_filepath=f"{path}slowed_reverb.mp3")

    await callback_query.message.answer_document(
        InputFile(f"{path}slowed_reverb.mp3"),
        caption=bot_link,
        parse_mode=mode,
    )
    clear_storage(chat_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
