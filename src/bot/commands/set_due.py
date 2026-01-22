import json
import logging
import asyncio
from typing import Optional, Dict
from datetime import timedelta, datetime

import discord
from discord import app_commands

from src.sheet_operations.enums.article_status import ArticleStatus
from src.bot import client, cycle_reminders
from src.bot.utils.parse_dates import parse_date
from src.bot.utils.schedule_reminder import schedule_cycle_reminder
from src.bot.utils.clear_cycle_reminders import clear_cycle_reminders


#TODO: simplify UI using a view & refactor method
@client.tree.command(name="set_cycle_due",
                     description="Sets the due dates for a given article cycle.")
@app_commands.checks.has_any_role("EIC", "quillbot-manager")
@app_commands.describe(cycle="The cycle number ",
                       send_reminders="Whether to send DM reminders for this cycle's due dates",
                      due_date="The cycle's first draft due date (MM-DD-YY; " \
                        "other dates are inferred by default)",
                      section_edit="When section edits are due.",
                      section_revise="When section edit revisions are due.",
                      eic_edit="When EIC edits are due.",
                      eic_revise="When EIC edit revisions are due.",
                      shapiro_edit="When Shapiro edits are due.",
                      shapiro_revise="When Shapiro edit revisions are due.")
async def set_cycle_due(interaction: discord.Interaction,
                       cycle: int,
                       due_date: str,
                       section_edit: Optional[str],
                       section_revise: Optional[str],
                       eic_edit: Optional[str],
                       eic_revise: Optional[str],
                       shapiro_edit: Optional[str],
                       shapiro_revise: Optional[str],
                       send_reminders: bool = True):
    """Sets the due dates for a given article cycle."""
    logger = logging.getLogger("discord")
    due_dates: Dict[str, str | None] = {
        "draftDue": due_date,
        "sectionEditsDue": section_edit,
        "sectionRevisedDue": section_revise,
        "eicEditsDue": eic_edit,
        "eicRevisedDue": eic_revise,
        "shapiroEditsDue": shapiro_edit,
        "shapiroRevisedDue": shapiro_revise,
    }
    #default offset in days from the previous due date
    due_date_offsets = {
        "draftDue": 0,
        "sectionEditsDue": 3,
        "sectionRevisedDue": 5,
        "eicEditsDue": 7,
        "eicRevisedDue": 9,
        "shapiroEditsDue": 11,
        "shapiroRevisedDue": 13,
    }
    try:
        curr_due_date = parse_date(due_date)
    except ValueError:
        await interaction.response.send_message(
            "Invalid date format for draft due date. Please use MM-DD-YY format.",
            ephemeral=True
        )
        return
    try:
        clear_cycle_reminders(cycle)
    except RuntimeError:
        #previous cycle reminders currently being fired
        logger.warning("Could not clear previous reminders for Cycle %s" \
            "as they are currently being fired.", cycle)
    for date, offset in due_date_offsets.items():
        if due_dates[date]:
            try:
                curr_due_date = parse_date(due_dates[date]) #type: ignore
            except ValueError:
                await interaction.response.send_message(
                    f"Invalid date format for {date}. Please use MM-DD-YY format.",
                    ephemeral=True
                )
                return
        else:
            curr_due_date += timedelta(days=offset)
        due_dates[date] = curr_due_date.isoformat()
    with open("data/cycle_info.json", "r", encoding="utf-8") as f:
        cycle_info = json.load(f)
    cycle_info[str(cycle)] = due_dates
    with open("data/cycle_info.json", "w", encoding="utf-8") as f:
        json.dump(cycle_info, f, indent=4)
    if send_reminders:
        possible_statuses = [ArticleStatus.DRAFT,
                             ArticleStatus.SECTION,
                             ArticleStatus.SECTION_REVISE,
                             ArticleStatus.EIC,
                             ArticleStatus.EIC_REVISE,
                             ArticleStatus.SHAPIRO_EDIT,
                             ArticleStatus.SHAPIRO_REVISE]
        for (_, due), status in zip(due_dates.items(), possible_statuses):
            due = datetime.fromisoformat(due) #type: ignore
            task = asyncio.create_task(
                schedule_cycle_reminder(cycle, status, due)
            )
            cycle_reminders.append(task)
            task.add_done_callback(cycle_reminders.remove) #prevent stale tasks
    await interaction.response.send_message(
        f"Successfully set due dates for **Cycle {cycle}**.", ephemeral=True
    )
