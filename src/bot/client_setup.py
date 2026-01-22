#type: ignore
import logging

import discord
from discord import Client, app_commands

logger = logging.getLogger("discord")

MY_GUILD = discord.Object(id=1463008420532715669) #TODO: make non guild specific

class MyClient(Client):
    """Client object for the Discord bot."""
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """Register all commands with Discord"""
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        logger.info("Commands synced.")
