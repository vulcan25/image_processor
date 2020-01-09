from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from functools import wraps
from io import BytesIO
from telegram import Update, ChatAction

import os
import random
import requests

TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY', 0)

if TELEGRAM_API_KEY == 0:
    raise Exception('Please set TELEGRAM_API_KEY in .telegram-env')

LIST_OF_ADMINS = [i for i in os.environ.get("LIST_OF_ADMINS", '').split(",")]
LIST_OF_ADMINS = [int(x) for x in LIST_OF_ADMINS if x != '']

updater = Updater(token=TELEGRAM_API_KEY, use_context=True)

dispatcher = updater.dispatcher

def beginning():
    CONVO_STARTS = ["Here's what I found: ", "In that image I got: ", "Here's what that image contains: "]
    return random.choice(CONVO_STARTS)

#
# This decorator lets you limit a response to only admins:
def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

#
# Chat action, makes teh bot look like it's typing, etc.
def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            update, context = args
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, **kwargs)
        return command_func
    return decorator

""" Bots should implement a `/start` command """
@restricted
def start (update: Update, context: CallbackContext):
    response = "I'm an image recognition telegram bot powered by YOLOv3.  Share a photo and I'll tell you what I see."
    context.bot.send_message(chat_id=update.message.chat_id, text=response)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

""" This echo handler tells you your `chat_id` """
def echo(update: Update, context: CallbackContext):
    response = update.effective_user.id
    context.bot.send_message(chat_id=update.message.chat_id, text=response)
    

""" A function to utilise the image_processor API """
def upload(file_obj):
    headers={'ContentType': 'multipart/form-data'}
    files = {'file': ('tg-upload.jpg', file_obj, 'image/jpeg')}

    # TODO: Set this URL via env var
    url='http://processor:5000/upload'

    req = requests.post(url, files=files)
    
    #print (req.content)
    
    return req.json()

""" This one handles the photo transfer from telegram. """
@send_action(ChatAction.TYPING)
@restricted
def photo(update: Update, context: CallbackContext):

    print ('Recognising:', update.message.caption)
    
    file = context.bot.get_file(update.message.photo[-1].file_id)

    response = 'I was unable to process that for some reason.' # default

    f =  BytesIO(file.download_as_bytearray())
    
    print ('about to query image_processor API')
        
    result = upload(f)
    print ('RESULT: ', result)

    if 'info' in result:
        if len(result['info']['objects']) > 0:
            response = '%s%s' % (beginning(), result['info']['object_string'])
        else:
            response = "I couldn't see anything in that image."

    context.bot.send_message(chat_id=update.message.chat_id, text=response)


""" This makes an echo endpoint available to find your own `chat_id`. 
    If the LIST_OF_ADMINS contains < 1 chat_id, the photo handler is not served, instead
    the echo handler is served.  Once you've got the chat ID, add it to `.telegram-env`
    and restart the compose service.
    """

print ('Admin list: ', LIST_OF_ADMINS)

if len(LIST_OF_ADMINS) < 1:
    print ('Serving echo handler')
    echo_handler = CommandHandler('echo', echo)
    dispatcher.add_handler(echo_handler)
else:
    print ('Serving photo handler')
    photo_handler = MessageHandler(Filters.photo, photo)
    dispatcher.add_handler(photo_handler)

print ('About to poll...')
updater.start_polling()
