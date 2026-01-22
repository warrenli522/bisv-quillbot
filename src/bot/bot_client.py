import discord

from src.bot.client_setup import MyClient

intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)

@client.event
async def on_ready():
    """log message for bot ready"""
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
