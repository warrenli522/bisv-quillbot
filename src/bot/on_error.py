import logging

import discord

from src.bot import client

@client.tree.error
async def on_error(interaction: discord.Interaction, error: Exception, /) -> None:
    """Global error handler for app commands."""
    logger = logging.getLogger("discord")
    logger.error("An error occurred: %s. Context: %s", error, interaction.context, exc_info=True)
    if not interaction.response.is_done():
        await interaction.followup.send(
            "An unexpected error occurred!" \
            " If the error persists, please contact <@722584036068818945>.",
            ephemeral=True,
        )
