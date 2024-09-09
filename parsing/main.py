import asyncio
from telethon import TelegramClient
import telegram_parser.config as config
from telegram_parser.parser import fetch_messages

client = TelegramClient('session_name', config.api_id, config.api_hash)

async def main():
    await client.start(config.phone)
    await fetch_messages(client, config.channel_username, config.since_date)

with client:
    client.loop.run_until_complete(main())
