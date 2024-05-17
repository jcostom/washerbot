#!/usr/bin/env python3

import asyncio
import logging
import os
import telegram
import json
import requests
from time import sleep, strftime
from kasa import SmartPlug

# --- To be passed in to container ---
# Mandatory vars
PLUG_IP = os.getenv('PLUG_IP')
TZ = os.getenv('TZ', 'America/New_York')
OFFPOWER = float(os.getenv('OFFPOWER', 1.2))
ONPOWER = float(os.getenv('ONPOWER', 3.0))
INTERVAL = os.getenv('INTERVAL', 300)

# Optional Vars
DEBUG = int(os.getenv('DEBUG', 0))

# Optional Vars for Notification Types
# --- Optional Vars ---
# Telegram
USE_TELEGRAM = int(os.getenv('USE_TELEGRAM', 0) or os.getenv('USETELEGRAM', 0))  # noqa E501
TELEGRAM_CHATID = int(os.getenv('TELEGRAM_CHATID', 0) or os.getenv('CHATID', 0))  # noqa E501
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'none') or os.getenv('MYTOKEN', 'none')  # noqa E501

# Pushover
USE_PUSHOVER = int(os.getenv('USE_PUSHOVER', 0) or os.getenv('USEPUSHOVER', 0))  # noqa E501
PUSHOVER_APP_TOKEN = os.getenv('PUSHOVER_APP_TOKEN')
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')

# Pushbullet
USE_PUSHBULLET = int(os.getenv('USE_PUSHBULLET', 0) or os.getenv('USEPUSHBULLET', 0))  # noqa E501
PUSHBULLET_APIKEY = os.getenv('PUSHBULLET_APIKEY')

# Alexa "Notify Me" - Add this Skill to your Alexa Account before you use this!
USE_ALEXA = int(os.getenv('USE_ALEXA', 0) or os.getenv('USEALEXA', 0))  # noqa E501
ALEXA_ACCESSCODE = os.getenv('ALEXA_ACCESSCODE')

# Other Globals
VER = "1.0.4"
USER_AGENT = f"washerbot.py/{VER}"

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()


async def send_telegram(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=msg)
    logger.info('Telegram Group Message Sent')


def send_pushover(msg: str, token: str, user: str) -> requests.Response:
    url = "https://api.pushover.net/1/messages.json"
    data = {"token": token, "user": user, "message": msg}
    r = requests.post(url, data)
    logger.info('Pushover Message Sent')
    return r


def send_pushbullet(msg: str, apikey: str) -> requests.Response:
    url = "https://api.pushbullet.com/v2/pushes"
    data = {"type": "note", "body": msg}
    headers = {"Authorization": f"Bearer {apikey}", "Content-Type": "application/json"}  # noqa E501
    r = requests.post(url, data=json.dumps(data), headers=headers)
    logger.info('Pushbullet Message Sent')
    return r


def send_alexa(msg: str, access_code: str) -> requests.Response:
    url = "https://api.notifymyecho.com/v1/NotifyMe"
    data = {"notification": msg, "accessCode": access_code}
    r = requests.post(url, data=json.dumps(data))
    logger.info('Alexa Notification Sent')
    return r


def send_notifications(msg: str) -> None:
    if USE_TELEGRAM:
        asyncio.run(send_telegram(msg, TELEGRAM_CHATID, TELEGRAM_TOKEN))  # noqa E501
    if USE_PUSHOVER:
        send_pushover(msg, PUSHOVER_APP_TOKEN, PUSHOVER_USER_KEY)  # noqa E501
    if USE_PUSHBULLET:
        send_pushbullet(msg, PUSHBULLET_APIKEY)
    if USE_ALEXA:
        send_alexa(msg, ALEXA_ACCESSCODE)


async def plug_off(ip: str) -> None:
    p = SmartPlug(ip)
    await p.update()
    await p.turn_off()


async def plug_on(ip: str) -> None:
    p = SmartPlug(ip)
    await p.update()
    await p.turn_on()


async def read_consumption(ip: str) -> float:
    p = SmartPlug(ip)
    await p.update()
    watts = await p.current_consumption()
    return watts


def main() -> None:
    logger.info(f"Initiated: {USER_AGENT}")

    # Make sure plug is switched on
    logger.info(f"Ensuring plug {PLUG_IP} is switched on.")
    asyncio.run(plug_on(PLUG_IP))

    is_running = 0

    while True:
        watts = asyncio.run(read_consumption(PLUG_IP))
        if is_running == 0:
            if watts > ONPOWER:
                logger.info(f"Transition from stopped to running: {watts}")
                is_running = 1
            else:
                DEBUG and logger.debug(f"Washer remains stopped: {watts}")
        else:
            if watts < OFFPOWER:
                logger.info(f"Transition from running to stopped: {watts}")
                now = strftime("%B %d, %Y at %H:%M")
                notification_text = f"Washer finished on {now}. Go switch out the laundry!"  # noqa: E501
                # asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))  # noqa: E501
                send_notifications(notification_text)
                is_running = 0
            else:
                DEBUG and logger.debug(f"Washer remains running: {watts}")

        sleep(INTERVAL)


if __name__ == "__main__":
    main()
