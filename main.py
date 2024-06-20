import os
import telebot
from dotenv import load_dotenv
import g4f
import openai
from g4f.client import Client
import asyncio
import toVec
from translate import Translator
from langdetect import detect
from hugchat import hugchat
from hugchat.login import Login

EMAIL = "polumeevm@gmail.com"
PASSWD = "AGj-3Ax-5qY-Zuc"
cookie_path_dir = "./HvZyzLKSweHTVsGZLduDjNVPnOuuVAMbPcHzueufxKpwDkFJtBzWTbVngUYEYBnMZYQYSqlSVNkCJejuMhQkyGdHoySXjhwPfmCiMDRcTzkzRUtxIKhkYVdBBilrIWNQ/" # NOTE: trailing slash (/) is required to avoid errors
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
api_key = "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"
openai.api_key = api_key
openai.api_base = "http://127.0.0.1:1337"


client = Client()
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

bot = telebot.TeleBot("7294195287:AAENfP12AU3wqr3iobWyuFrJHpuUdkF_Gf8")

def generate_response(prompt):
    print(prompt)

    # Если не будет работать эта версия гпт
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": prompt}],
    #     stream=False,
    #     provider=g4f.Provider.FreeGpt,
    # )

    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return response.choices[0].message.content
    message_result = chatbot.chat(prompt)
    return message_result.text

@bot.message_handler(func=lambda message: True)
def handle_message(message):
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
