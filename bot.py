import json
import sys
import logging
import urllib
import telegram
import subprocess
import os
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

token = open('token.txt', 'r').read().replace('\n', '')
updater = Updater(token=token)
dispatcher = updater.dispatcher


def start(bot, update):
  bot.sendMessage(chat_id=update.message.chat_id,
      text='Hi! \nI\'m Draw Me Bot!\nSend me a picture and I\'ll draw you.\nMy current style is sketch.\nThis is the only style I can currently draw in, but I will hopefully learn more :D')

def processPhoto(bot, update):
  # Get Photo, write it to image folder with chat id as filename
  with urllib.request.urlopen("http://api.telegram.org/bot"+token+"/getFile?file_id="+update.message.photo[1].file_id) as response:
    remoteFilePath = json.loads(response.read().decode("utf-8"))["result"]["file_path"]
    localFilePath = "images/"+str(update.message.chat_id)
    urllib.request.urlretrieve("http://api.telegram.org/file/bot"+token+"/"+remoteFilePath, localFilePath+".jpg")

    # Magic happens here, process photo via neural net, wait for result
    # command = "convert "+localFilePath+".jpg -charcoal 2 "+localFilePath+"_out.jpg"
    command = "imgmagick_scripts/sketch.sh "+str(update.message.chat_id)
    print(command)
    process = subprocess.Popen(command, shell=True, cwd=os.path.dirname(os.path.realpath("__file__")))
    process.wait()
    with open(localFilePath+"_out.jpg", "rb") as file:
      bot.send_photo(chat_id=update.message.chat_id, photo=file)
      bot.sendMessage(chat_id=update.message.chat_id, text="Done! I hope you like it <3")

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler([Filters.photo], processPhoto))

updater.start_polling()

