import asyncio
from datetime import datetime
import json
import logging

import discord
import pandas as pd

from src.bot import client
from src.sheet_operations.enums.article_status import ArticleStatus
from src.sheet_operations.get_cycle_report import get_cycle_report
from src.sheet_operations.utils.get_sheet import get_sheet

async def schedule_cycle_reminder(cycle: int, stage: ArticleStatus, due_date: datetime) -> None:
    """
    Sends reminders for a single edit stage in a cycle (e.g. Cycle 5 draft). 
    When edits are due, checks the sheet for incomplete articles and sends reminders.
    IMPORTANT: this method does not check if the due date has been updated
    NOTE: reminders are not sent for published articles or Shapiro edits
    
    :param cycle: The cycle number to send reminders for
    :type cycle: int
    :param stage: The edit stage to send reminders for
    :type stage: ArticleStatus
    :param due_date: The due date for the edits
    :type due_date: datetime
    """
    if stage in (ArticleStatus.PUBLISHED, ArticleStatus.SHAPIRO_EDIT):
        #these two stages don't need reminders sent
        return
    logger = logging.getLogger("discord")
    await asyncio.sleep(due_date.timestamp() - datetime.now().timestamp())

    logger.info("Sending reminders for Cycle %s %s due %s",
                cycle, stage.value, due_date.isoformat())
    sheet = get_sheet()
    cycle_data = get_cycle_report(sheet, cycle)
    with open("data/member_info.json", "r", encoding="utf-8") as f:
        author_data = json.load(f)

    #get discord IDs to send reminders to
    if stage == ArticleStatus.DRAFT:
        names = pd.concat([cycle_data["missing_articles"],
                            cycle_data["draft_incomplete"]["AUTHORS"]]).explode().unique()
        for name in names:
            discord_id = author_data[name]["discordID"]
            user = await client.fetch_user(discord_id)
            if user:
                try:
                    await user.send(
                        f"This is a reminder that your draft for **Cycle {cycle}** is due on "
                        f"{due_date.strftime('%m/%d')}, please make sure to "
                        f"complete it as soon as possible!"
                    )
                except discord.Forbidden:
                    logger.info("Could not send cycle reminder DM to" \
                        "user with Discord ID `%s`", discord_id)
    else:
        articles = cycle_data["unedited_articles"]
        articles = articles.loc[articles["status"] == stage.value]

        if stage == ArticleStatus.SECTION:
            editor_col = "SECTION EDITOR"
        elif stage == ArticleStatus.EIC:
            editor_col = "EIC"
        else:
            editor_col = None

        for _, article in articles.iterrows():
            if editor_col:
                editor = article[editor_col]
                if pd.isna(editor) or editor not in author_data:
                    logger.warning("No valid editor data found for article \"%s\" for stage %s." \
                                    "Got '%s'",
                                   article["ARTICLE TITLE"], stage.value, editor)
                discord_id = author_data[editor]["discordID"]
                user = await client.fetch_user(discord_id)
                if user:
                    try:
                        await user.send(
                            f"This is a reminder that your assigned **{stage.value}** for the "
                            f"**Cycle {cycle}** article \"{article['ARTICLE TITLE']}\" "
                            f"have not been completed! Due date: {due_date.strftime('%m/%d')}"
                        )
                    except discord.Forbidden:
                        logger.info("Could not send cycle reminder DM to user with ID %d",
                                    discord_id)
            else:
                #there may be multiple authors, notify each
                discord_ids = [author_data[author]["discordID"] for author in article["AUTHORS"]]
                for disc_id in discord_ids:
                    user = await client.fetch_user(disc_id)
                    if user:
                        try:
                            await user.send(
                                f"This is a reminder that your **{stage.value}** for the "
                                f"**Cycle {cycle}** article \"{article['ARTICLE TITLE']}\" "
                                f"have not been completed! Due date: {due_date.strftime('%m/%d')}"
                            )
                        except discord.Forbidden:
                            logger.info("Could not send cycle reminder DM to user with ID %d",
                                        disc_id)
