import base64
import logging
import sys
import requests
import traceback
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
SPEECH_BACK = getenv("SPEECH_BACK")
WORDS_BACK = getenv("WORDS_BACK")
API_KEY = getenv("API_KEY")

# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = "::"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8350

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/bot/"
# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = "my-secret"
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
BASE_WEBHOOK_URL = "https://andriyip-04.alwaysdata.net/"

# All handlers should be attached to the Router (or Dispatcher)
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hi, {hbold(message.from_user.full_name)}!")


@router.message(Command("voice"))
async def command_find_handler(message: Message) -> None:
    if message.text:
        await message.chat.do("typing")
        text = process_query(message.text).strip()

        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": "en-US",
                "name": "en-US-News-L",
                "ssmlGender": "FEMALE"
            },
            "audioConfig": {"audioEncoding": "OGG_OPUS"}
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "joj-text-to-speech.p.rapidapi.com"
        }

        try:
            response = requests.post(SPEECH_BACK, json=payload, headers=headers)
            if 200 <= response.status_code <= 299:
                result = response.json()
                base64_voice_bytes = result["audioContent"].encode('utf-8')
                voice_data = base64.decodebytes(base64_voice_bytes)
                file = BufferedInputFile(voice_data, filename="voice.ogg")
                print(file)
                await message.bot.send_voice(voice=file, chat_id=message.chat.id)
            else:
                response_error = response.json()
                await message.answer(f"Request to backend was not successful: {response_error}")
        except TypeError as error:
            await message.answer("Error happened! " + traceback.format_exc())

    else:
        await message.answer("Something went wrong")


@router.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types (like text, photo, sticker etc.)
    """
    if message.text:
        await message.chat.do("typing")
        word = message.text.split(" ").pop(0)

        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
        }

        try:
            response = requests.get(WORDS_BACK + word + "/synonyms", headers=headers)
            if 200 <= response.status_code <= 299:
                result = response.json()
                print(result)
                synonyms = "\n".join(result["synonyms"]) if len(result["synonyms"]) else ("Seems like this word has no "
                                                                                          "synonyms.")
                await message.answer(f"Your word is: {word}. Here is a list of synonyms: \n {synonyms}")
            else:
                response_error = response.json()
                if "message" in response_error:
                    await message.answer(f"Request to backend was not successful: {response_error['message']}")
                else:
                    await message.answer(f"Request to backend was not successful: {response_error}")
        except TypeError as error:
            await message.answer("Error happened! " + traceback.format_exc())


def process_query(query_string: str):
    query = " ".join(query_string.split(" ")[1:])
    return query


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
