#pyright: reportUnusedImport=false
from asyncio import Task
from typing import List
from src.bot.bot_client import client

__all__ = ["client"]
#store strong references to prevent garbage collection
cycle_reminders: List[Task[None]] = []
from src.bot.commands import *
from src.bot.on_error import on_error
