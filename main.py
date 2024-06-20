import os
import telebot
from dotenv import load_dotenv
import asyncio
import toVec
from telebot import types
from translate import Translator
from langdetect import detect
from hugchat import hugchat
from hugchat.login import Login




load_dotenv('key.env')
EMAIL = os.getenv('EMAIL')
PASSWD = os.getenv('PASSWD')
cookie_path_dir = os.getenv('COOKIE')
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
sign = Login(EMAIL, PASSWD)


cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())


def translate_text(text, to_lang, chunk_size=500):
    translator = Translator(to_lang=to_lang, from_lang=detect(text))
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    translation = ""
    for chunk in chunks:
        translated_chunk = translator.translate(chunk)
        translation += translated_chunk + " "
    return translation.strip()

os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

current_mode = "generateTheDatabase"

@bot.message_handler(commands=['generateTheDatabase', 'generate'])
def set_mode(message):
    global current_mode
    if message.text == '/generateTheDatabase':
        current_mode = 'translate'
        bot.send_message(message.chat.id, "Режим перевода активирован.")
    elif message.text == '/generate':
        current_mode = 'generate'
        bot.send_message(message.chat.id, "Режим генерации ответов активирован.")

def create_mode_selection_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    generateTheDatabase_button = types.KeyboardButton("Генерация ответа из базы данных")
    generate_button = types.KeyboardButton("Генерация ответов")
    keyboard.add(generateTheDatabase_button, generate_button)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Добро пожаловать! Пожалуйста, выберите режим работы."
    bot.send_message(message.chat.id, welcome_text, reply_markup=create_mode_selection_keyboard())

@bot.message_handler(func=lambda message: message.text in ["Генерация ответа из базы данных", "Генерация ответов"])
def set_mode(message):
    global current_mode
    if message.text == 'Генерация ответа из базы данных':
        current_mode = 'generateTheDatabase'
        bot.send_message(message.chat.id, "Режим генерации ответов из базы данных активирован.", reply_markup=create_mode_selection_keyboard())
    elif message.text == 'Генерация ответов':
        current_mode = 'generate'
        bot.send_message(message.chat.id, "Режим генерации ответов активирован.", reply_markup=create_mode_selection_keyboard())


def generate_response(prompt):
    print(prompt)
    message_result = chatbot.chat(prompt)
    return message_result.text

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global current_mode
    if current_mode == 'generate':
        user_message = translate_text(message.text, 'en')
        prompt = user_message
        response = generate_response(prompt)
        translated_response = translate_text(response, 'ru')
        bot.send_message(message.chat.id, translated_response)
    elif current_mode == 'generateTheDatabase':
        user_message = translate_text(message.text, 'en')
        data = toVec.read_specific_row(int(toVec.load_vectors_and_search(str(user_message))) + 1)
        prompt = user_message + " Based on this data " + data + " Write answer in English"
        try:
            response = generate_response(prompt)
            print(response)
            translated_response = translate_text(response, 'ru')
            bot.send_message(message.chat.id, translated_response)
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

bot.polling()
