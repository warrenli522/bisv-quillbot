from typing import Optional
import logging

import discord
from discord import app_commands

from src.bot import client

from src.sheet_operations.utils.get_sheet import get_sheet
from src.sheet_operations.utils.name_from_id import get_name_by_id
from src.sheet_operations.get_edits import get_edits

logger = logging.getLogger("discord")

#TODO: make this work for editors
@client.tree.command(name="incomplete_edits",
                     description="Sends a message with all edits that need revising.")
@app_commands.describe(author="Who to check for edits (defaults to yourself). " \
                       "Format: <First Name> <Last Initial>")
async def get_edits_command(interaction: discord.Interaction, author: Optional[str]):
    """Sends a message with all of a user's incomplete edits."""
    logger.debug("incomplete_edits command invoked by %s for author=%s", interaction.user, author)
    if author is None:
        author = get_name_by_id(interaction.user.id)
        if not author:
            await interaction.response.send_message(
                "Your Discord ID is not linked to any author name. " \
                "Please contact <@722584036068818945> to resolve this!",
                ephemeral=True,
            )
            return

    await interaction.response.defer()
    sheet = get_sheet()
    incomplete_edits = get_edits(sheet, author=author, late=False)
    if not incomplete_edits.empty:
        message = f"Below are the articles with incomplete edits for **{author}**:\n"
        for _, article in incomplete_edits.iterrows():
            message += (f"- **Cycle {article['CYCLE']}**: "
                    f"'{article['ARTICLE TITLE']}' (waiting on {article['status']})")
            if article["late"]:
                message += " ⏰ **LATE**"
            message += "\n"
        await interaction.followup.send(message)
    else:
        await interaction.followup.send('You have no incomplete edits :)', ephemeral=True)
