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
chatbot.switch_llm(0)

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
current_lang = "ru"

@bot.message_handler(commands=['generateTheDatabase', 'generate'])
def set_mode(message):
    global current_mode
    if message.text == '/generateTheDatabase':
        current_mode = 'generateTheDatabase'
        bot.send_message(message.chat.id, translate_text("Режим генерации ответов из базы данных активирован.", current_lang))
    elif message.text == '/generate':
        current_mode = 'generate'
        bot.send_message(message.chat.id, translate_text("Режим генерации ответов активирован.", current_lang))

def create_mode_selection_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    generateTheDatabase_button = types.KeyboardButton(translate_text("Генерация ответа из базы данных", current_lang))
    generate_button = types.KeyboardButton(translate_text("Генерация ответов", current_lang))
    keyboard.add(generateTheDatabase_button, generate_button)
    return keyboard

def create_language_selection_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    en_button = types.KeyboardButton("en")
    ru_button = types.KeyboardButton("ru")
    fr_button = types.KeyboardButton("fr")
    keyboard.add(en_button, ru_button,fr_button)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Welcome! Select the language in the en/ru format."
    bot.send_message(message.chat.id, welcome_text, reply_markup=create_language_selection_keyboard())

@bot.message_handler(func=lambda message: message.text in [translate_text("Генерация ответа из базы данных", current_lang), translate_text("Генерация ответов", current_lang)])
def set_mode(message):
    global current_mode
    if message.text == translate_text("Генерация ответа из базы данных", current_lang):
        current_mode = 'generateTheDatabase'
        bot.send_message(message.chat.id, translate_text("Режим генерации ответов из базы данных активирован.", current_lang), reply_markup=create_mode_selection_keyboard())
    elif message.text == translate_text("Генерация ответов", current_lang):
        current_mode = 'generate'
        bot.send_message(message.chat.id, translate_text("Режим генерации ответов активирован.", current_lang), reply_markup=create_mode_selection_keyboard())

@bot.message_handler(func=lambda message: message.text in ["en", "ru","fr"])
def set_language(message):
    global current_lang
    current_lang = message.text
    data = translate_text(translate_text("Язык установлен на ", current_lang), current_lang)
    bot.send_message(message.chat.id, f"{data} {current_lang}", reply_markup=create_mode_selection_keyboard())

def generate_response(prompt):
    print(prompt)
    message_result = chatbot.chat(prompt)
    return message_result.text

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global current_mode, current_lang
    if current_mode == 'generate':
        prompt = message.text
        response = generate_response(prompt)
        translated_response = translate_text(response, current_lang)
        bot.send_message(message.chat.id, translated_response)
    elif current_mode == 'generateTheDatabase':
        user_message = translate_text(message.text, 'en')
        data = toVec.read_specific_row(int(toVec.load_vectors_and_search(str(message.text))) + 1)
        prompt = user_message + " Based on this data " + data + " Write answer in English"
        try:
            response = generate_response(prompt)
            print(response)
            translated_response = translate_text(response, current_lang)
            bot.send_message(message.chat.id, translated_response)
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

bot.polling()
