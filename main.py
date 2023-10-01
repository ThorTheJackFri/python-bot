import os
import json
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Define your bot token here
TOKEN = '6452800763:AAEYIdvIo8byckVTymq01ntVC37kKqSUF-M'

# Define states for conversation
START, UPLOAD = range(2)

# Function to start the bot
def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    update.message.reply_text("Welcome to the Streamtape Uploader bot! Send me a file to upload to Streamtape.")
    return UPLOAD

# Function to handle file upload
def upload_file(update: Update, context: CallbackContext) -> int:
    user_id = context.user_data['user_id']

    if update.message.document:
        file_id = update.message.document.file_id
        file = context.bot.get_file(file_id)
        file.download(f"{user_id}_{file.file_name}")
        upload_url = "https://api.streamtape.com/upload"
        response = requests.post(upload_url, files={'file': open(f"{user_id}_{file.file_name}", 'rb')})
        if response.status_code == 200:
            update.message.reply_text(f"File successfully uploaded to Streamtape. Here is the link:\n{response.json()['result']['url']}")
        else:
            update.message.reply_text("Failed to upload the file to Streamtape.")
        os.remove(f"{user_id}_{file.file_name}")
    else:
        update.message.reply_text("Please send a valid file to upload.")

    return ConversationHandler.END

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            UPLOAD: [MessageHandler(Filters.document, upload_file)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
