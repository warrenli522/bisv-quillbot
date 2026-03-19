import os
import logging
import dotenv

from src.bot import client

dotenv.load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

if not token:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

if os.getenv("DEBUG_MODE") == "True":
    os.environ["MEMBER_DATA_FILEPATH"] = "data/test_member_info.json"
    print("Running in debug mode! Using test member data.")
    client.run(token, log_handler=handler, log_level=logging.DEBUG)
else:
    client.run(token, log_handler=handler, log_level=logging.INFO)
