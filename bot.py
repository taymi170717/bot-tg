from os import getenv
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import F

# Загружаем переменные окружения
load_dotenv()

# Токен и ID из .env
API_TOKEN = getenv("API_TOKEN")
ADMIN_CHAT_ID = int(getenv("ADMIN_CHAT_ID"))
CHANNEL_ID = getenv("CHANNEL_ID")

# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(F.text == "/start")
async def start_command(message: Message):
    # Создаем клавиатуру с кнопкой "Поделиться анонимно"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Поделиться анонимно", callback_data="share_anonymously")]]
    )
    await message.reply("Привет! Нажми на кнопку ниже, чтобы отправить анонимное сообщение.", reply_markup=keyboard)

# Обработка нажатия кнопки "Поделиться анонимно"
@dp.callback_query(F.data == "share_anonymously")
async def handle_share_anonymously(callback: CallbackQuery):
    await callback.message.answer("Напишите сообщение, которое вы хотите отправить анонимно:")
    # Устанавливаем пользователя в состояние "ждет анонимного сообщения"
    dp.message.register(waiting_for_anonymous_message, F.chat.id == callback.message.chat.id)

# Ожидание анонимного сообщения
async def waiting_for_anonymous_message(message: Message):
    # Пересылаем анонимное сообщение админу
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"Поступило анонимное сообщение:\n\n{message.text}\n\nОтветь /publish <текст>, чтобы опубликовать его в канале."
    )
    # Подтверждаем отправку пользователю
    await message.reply("Ваше сообщение отправлено анонимно!")
    # Удаляем обработчик для этого пользователя
    dp.message.unregister(waiting_for_anonymous_message, F.chat.id == message.chat.id)

# Обработка команды /publish от админа
@dp.message(F.text.startswith("/publish") & F.chat.id == ADMIN_CHAT_ID)
async def publish_to_channel(message: Message):
    # Получаем текст для публикации, удаляя команду /publish
    text_to_publish = message.text.replace("/publish", "").strip()

    if not text_to_publish:
        await message.reply("Пожалуйста, добавь текст для публикации после команды /publish.")
        return

    # Добавляем кнопку "Поделиться анонимно" к публикации
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Поделиться анонимно", url=f"https://t.me/{(await bot.me()).username}")]]
    )

    # Отправляем сообщение в канал
    await bot.send_message(CHANNEL_ID, text_to_publish, reply_markup=keyboard)

    # Подтверждаем администратору успешную публикацию
    await message.reply("Сообщение успешно опубликовано в канале!")

# Основная функция запуска
async def main():
    print("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())