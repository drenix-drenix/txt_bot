import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import time

# Установите ваш токен Telegram бота
API_TOKEN = '6635957067:AAFJpg23oiqchcEZ1NOvvuUjBPG0kL07vaM'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Максимальный размер текстового сообщения в Telegram
MAX_MESSAGE_SIZE = 4096

# Минимальная задержка между отправкой сообщений (в секундах)
MESSAGE_SEND_DELAY = 3  # Например, 3 секунды

# Функция для отправки текста по частям с задержкой
async def send_text_in_parts(chat_id, text):
    for i in range(0, len(text), MAX_MESSAGE_SIZE):
        part = text[i:i + MAX_MESSAGE_SIZE]
        await bot.send_message(chat_id, part)
        time.sleep(MESSAGE_SEND_DELAY)  # Добавляем задержку между отправкой частей текста

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await message.answer("👋 *Привет! Я бот для извлечения текста из текстовых файлов.*\n\n📄 *Отправь мне текстовый файл .txt, я извлеку текст из него и отправлю его тебе.*", parse_mode=ParseMode.MARKDOWN)

# Обработчик для текстовых файлов
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    if message.document.mime_type == 'text/plain':
        file_info = await bot.get_file(message.document.file_id)
        file_path = file_info.file_path

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}') as resp:
                if resp.status == 200:
                    file_data = await resp.read()

                    # Извлекаем текст из файла
                    text = file_data.decode('utf-8')

                    if len(text) > MAX_MESSAGE_SIZE:
                        # Разделяем текст на части и отправляем их по очереди с задержкой
                        await send_text_in_parts(message.chat.id, text)
                    else:
                        # Отправляем извлеченный текст пользователю как обычное текстовое сообщение
                        await message.reply(text)
                else:
                    await message.reply("⚠️ *Не удалось загрузить файл!*", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("⚠️ *Пожалуйста, отправьте текстовый файл с расширением *.txt!*", parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
