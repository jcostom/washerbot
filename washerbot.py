#!/usr/bin/env python3

import asyncio
import logging
import os
import telegram
from time import sleep, strftime
from kasa import SmartPlug

# --- To be passed in to container ---
# Mandatory vars
PLUG_IP = os.getenv('PLUG_IP')
TZ = os.getenv('TZ', 'America/New_York')
OFFPOWER = float(os.getenv('OFFPOWER', 1.2))
ONPOWER = float(os.getenv('ONPOWER', 3.0))
INTERVAL = os.getenv('INTERVAL', 300)
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')

# Optional Vars
DEBUG = int(os.getenv('DEBUG', 0))

# Other Globals
VER = "0.7.6"
USER_AGENT = f"washerbot.py/{VER}"

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()


async def send_notification(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=msg)
    logger.info('Telegram Group Message Sent')


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
                asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))  # noqa: E501
                is_running = 0
            else:
                DEBUG and logger.debug(f"Washer remains running: {watts}")

        sleep(INTERVAL)


if __name__ == "__main__":
    main()
