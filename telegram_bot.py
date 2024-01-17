from variables import BOT_TOKEN
import os
import telebot
from ollama_handler import initialize_ollama
import whisper
import variables
from pydub import AudioSegment
import requests
from ultralytics import YOLO
from PIL import Image

bot = telebot.TeleBot(BOT_TOKEN)

def check_chat_id(message):
    if message.chat.id in variables.chat_ids:
        return True

def ask_ollama(message,text):
    if check_chat_id(message):
        ollama = initialize_ollama()
        response = str(ollama(text))
        return response
    else:
        return "Ollama doesn't want to talk to you"

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, str(message.chat.id))
    bot.reply_to(message, "Add your chat_id your variables so I can start talking to you ;)")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, ask_ollama(message,message.text))


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('./temp/new_file.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    sound = AudioSegment.from_ogg("./temp/new_file.ogg")
    sound.export("./temp/new_file.mp3",format="mp3")
    
     
    model = whisper.load_model("small")
    result = model.transcribe("./temp/new_file.mp3")
    bot.reply_to(message, f"Text transcribed from your audio: \n\n{result['text']}")
    bot.reply_to(message, ask_ollama(message,result['text']))

@bot.message_handler(content_types=['photo'])
def handle_images(message):
    try:

        # First reply after image reception
        bot.reply_to(message, "Your image has been received and is being processed :D")

        # Get the chat ID and message ID
        chat_id = message.chat.id
        message_id = message.message_id

        # Get information about the largest available image
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Download the image
        image_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
        response = requests.get(image_url)

        # Save the image in the current directory
        with open(f"image_{chat_id}_{message_id}.jpg", 'wb') as f:
            f.write(response.content)

        # Process the image using your YOLO model
        results = model.predict(f"image_{chat_id}_{message_id}.jpg")
        result = results[0]
        image = Image.fromarray(result.plot()[:,:,::-1])
        image.save(f"image_{chat_id}_{message_id}_yolo.jpg")
        
        # Send the processed image back to the user
        with open(f"image_{chat_id}_{message_id}_yolo.jpg", 'rb') as photo:
            bot.send_photo(chat_id, photo)


    except Exception as e:
        print(f"Error processing the image: {e}")

model = YOLO("yolov8m.pt")
bot.infinity_polling()
