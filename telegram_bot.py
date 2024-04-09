import logging
import urllib
from typing import Union
import requests
from telegram import __version__ as TG_VER
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)
from models import ApiResponse, ApiError
from dotenv import load_dotenv
from agents import OFCAgent


import os


load_dotenv(
    "ops/.env"
)

"""
Commands to use in the bot
start - Start the bot
set_language - To choose language of your choice
"""


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_KEY")
uuid_number = os.getenv("UUID_NUMBER")
bot = Bot(token=BOT_TOKEN)
CUSTOM_NAME = os.getenv("CUSTOM_NAME")

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """When the command /start is issued ask the user to choose a language"""
    await relay_handler(update, context)


async def relay_handler(update: Update, context: CallbackContext):
    await language_handler(update, context)


async def language_handler(update: Update, context: CallbackContext):
    english_button = InlineKeyboardButton('English', callback_data='lang_English')
    hindi_button = InlineKeyboardButton('हिंदी', callback_data='lang_Hindi')
    kannada_button = InlineKeyboardButton('ಕನ್ನಡ', callback_data='lang_Kannada')

    inline_keyboard_buttons = [[english_button], [hindi_button], [kannada_button]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

    await bot.send_message(chat_id=update.effective_chat.id, text="Choose a Language:", reply_markup=reply_markup)

async def action_handler(update: Update, context: CallbackContext):

    language = context.user_data.get('language')

    if language == "English":
        button_1 = InlineKeyboardButton('⁠I want information on legal rights', callback_data='action_1')
        button_2 = InlineKeyboardButton('I want to file a complaint', callback_data='action_2')
        button_3 = InlineKeyboardButton('I am not sure', callback_data='action_3')
    elif language == "Hindi":
        button_1 = InlineKeyboardButton('मैं कानूनी अधिकारों पर जानकारी चाहता हूँ', callback_data='action_1')
        button_2 = InlineKeyboardButton('मैं शिकायत दर्ज करना चाहता हूँ', callback_data='action_2')
        button_3 = InlineKeyboardButton('मुझे यकीन नहीं है', callback_data='action_3')
    elif language == "Kannada":
        button_1 = InlineKeyboardButton('ನೀತಿಯ ಹಕ್ಕುಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕಾಗಿದೆ', callback_data='action_1')
        button_2 = InlineKeyboardButton('ನಾನು ತಪ್ಪಿನದನ್ನು ದಾಖಲಿಸಲು ಬಯಸುತ್ತೇನೆ', callback_data='action_2')
        button_3 = InlineKeyboardButton('ನನಗೆ ಖಚಿತವಿಲ್ಲ', callback_data='action_3')
    inline_keyboard_buttons = [[button_1], [button_2], [button_3]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

    if language == "English":
        text = "Choose an option"
    elif language == "Hindi":
        text = "एक विकल्प चुनें"
    elif language == "Kannada":
        text = "ಒಂದು ಆಯ್ಕೆ ಮಾಡಿಕೊಂಡು ನೋಡಿ"

    await bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)


async def preferred_language_callback(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    preferred_language = callback_query.data.lstrip('lang_')
    context.user_data['language'] = preferred_language

    text_message = ""
    if preferred_language == "English":
        text_message = "You have chosen English."
    elif preferred_language == "Hindi":
        text_message = "आपने हिंदी चुना है।"
    elif preferred_language == "Kannada":
        text_message = "ಕನ್ನಡ ಆಯ್ಕೆ ಮಾಡಿಕೊಂಡಿದ್ದೀರಿ."

    await bot.send_message(chat_id=update.effective_chat.id, text=text_message)

    username = update.effective_user.username
    if not username:
        username = update.effective_user.first_name
    if not username:
        username = "User"

    agent = OFCAgent(
        username=username,
        language=context.user_data.get('language'),
        uuid=uuid_number
    )

    text_responses, voice_response, history = agent.execute("Start", None)
    for text_response in text_responses:
        await bot.send_message(chat_id=update.effective_chat.id, text=text_response)
    if voice_response:
        await bot.send_voice(chat_id=update.effective_chat.id, voice=voice_response)
    
    context.user_data['agent_state'] = agent.get_agent_state()

    await action_handler(update, context)



async def preferred_action_callback(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    preferred_action = callback_query.data.lstrip('action_')
    print(preferred_action)
    context.user_data['action'] = preferred_action
    if preferred_action == "1":
        text = "I want information on legal rights"
    elif preferred_action == "2":
        text = "I want to file a complaint"
    elif preferred_action == "3":
        text = "I am not sure"

    agent = OFCAgent(       
        username=update.effective_user.username,
        language=context.user_data.get('language'),
        uuid=uuid_number,
        history=context.user_data.get('agent_state', {}).get('history', [])
    )

    text_responses, voice_response, history = agent.execute(text, False)
    
    for text_response in text_responses:
        if text_response:
            await bot.send_message(chat_id=update.effective_chat.id, text=text_response)

    if voice_response:
        await bot.send_voice(chat_id=update.effective_chat.id, voice=voice_response)

    context.user_data['agent_state'] = agent.get_agent_state()


async def response_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await query_handler(update, context)


async def query_handler(update: Update, context: CallbackContext):
    voice_message_language = context.user_data.get('language')

    if not voice_message_language:
        await language_handler(update, context)
        return
    voice_message = None
    query = None

    if update.message.text:
        query = update.message.text
    elif update.message.voice:
        voice_message = update.message.voice

    if voice_message is not None:
        voice_file = await voice_message.get_file()
        voice_message = voice_file.file_path
        voice = True
    else:
        voice = False

    query = query or voice_message
    
    text_message = ""
    if voice_message_language == "English":
        text_message = "Thank you, allow me to search for the best information to respond to your query."
    elif voice_message_language == "Hindi":
        text_message = "शुक्रीया। मैं आपके प्रश्न के लिए सही जानकरी ढूंढ रही हूं।"
    elif voice_message_language == "Kannada":
        text_message = "ಧನ್ಯವಾದ. ನಾನು ಉತ್ತಮ ಮಾಹಿತಿಯನ್ನು ಕಂಡುಕೊಳ್ಳುವವರೆಗೆ ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ"

    await bot.send_message(chat_id=update.effective_chat.id, text=text_message)

    agent = OFCAgent(
        username=update.effective_user.username,
        language=context.user_data.get('language'),
        uuid=uuid_number,
        history=context.user_data.get('agent_state', {}).get('history', [])
    )

    text_responses, voice_response, history = agent.execute(query, voice)

    for text_response in text_responses:
        if text_response:
            await bot.send_message(chat_id=update.effective_chat.id, text=text_response)
    
    if voice_response:
        await bot.send_voice(chat_id=update.effective_chat.id, voice=voice_response)

    context.user_data['agent_state'] = agent.get_agent_state()




def main() -> None:
    application = ApplicationBuilder().bot(bot).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler('set_language', language_handler))

    application.add_handler(CallbackQueryHandler(preferred_language_callback, pattern=r'lang_\w*'))

    application.add_handler(CallbackQueryHandler(preferred_action_callback, pattern=r'action_\w*'))

    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, response_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
