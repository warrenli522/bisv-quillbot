import os
import logging
import dotenv

from src.bot import client

dotenv.load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setLevel(logging.DEBUG)
client.run(token, log_handler=handler)
