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

stateMachine = dict()


def start(bot, update):
  stateMachine[update.message.chat_id] = {}
  stateMachine[update.message.chat_id]['style'] = 'oil'
  stateMachine[update.message.chat_id]['processing'] = False
  bot.sendMessage(chat_id=update.message.chat_id,
      text='Hi! \nI\'m Draw Me Bot!\nSend me a picture and I\'ll draw you.\nMy current style is oil.\nCurrently I can draw in the styles oil and sketch, but I will hopefully learn more :D\nJust use /oil or /sketch to change my style.')

def oil(bot, update): 
  stateMachine[update.message.chat_id]['style'] = 'oil'
  bot.sendMessage(chat_id=update.message.chat_id,
	text='Okay, now using the oil style.')

def sketch(bot, update):
  stateMachine[update.message.chat_id]['style'] = 'sketch'
  bot.sendMessage(chat_id=update.message.chat_id,
	text='Okay, now using the sketch style.')

def processPhoto(bot, update):
  # Get Photo, write it to image folder with chat id as filename
  with urllib.request.urlopen('http://api.telegram.org/bot'+token+'/getFile?file_id='+update.message.photo[1].file_id) as response:
    remoteFilePath = json.loads(response.read().decode('utf-8'))['result']['file_path']
    localFilePath = 'images/'+str(update.message.chat_id)
    urllib.request.urlretrieve('http://api.telegram.org/file/bot'+token+'/'+remoteFilePath, localFilePath+'.jpg')

    # Check whether we're already processing something
    if stateMachine[update.message.chat_id]['processing']:
      bot.sendMessage(chat_id=update.message.chat_id, text='Not so fast! I\'m still working on the last image! :(')
      return False

    stateMachine[update.message.chat_id]['processing'] = True
    # Magic happens here, process photo via neural net, wait for result
    if (stateMachine[update.message.chat_id]['style'] == 'oil'):
      command = 'scripts/oil.sh '+str(update.message.chat_id)
    elif (stateMachine[update.message.chat_id]['style'] == 'sketch'):
      command = 'scripts/sketch.sh '+str(update.message.chat_id)

    print(command)
    process = subprocess.Popen(command, shell=True, cwd=os.path.dirname(os.path.realpath('__file__')))
    process.wait()
    stateMachine[update.message.chat_id]['processing'] = False
    with open(localFilePath+'_out.jpg', 'rb') as file:
      bot.send_photo(chat_id=update.message.chat_id, photo=file)
      bot.sendMessage(chat_id=update.message.chat_id, text='Done! I hope you like it! :D')


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('oil', oil))
dispatcher.add_handler(CommandHandler('sketch', sketch))
dispatcher.add_handler(MessageHandler([Filters.photo], processPhoto))

updater.start_polling()

