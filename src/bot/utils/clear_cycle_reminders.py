from src.bot import cycle_reminders

def clear_cycle_reminders(cycle: int) -> None:
    """Clears old scheduled reminders from the bot's tasks."""
    #check if task group with name "cycle_reminders_{cycle}" exists
    for task in cycle_reminders:
        if not task.done() and task.get_name() == f"cycle_reminders_{cycle}":
            task.cancel()
            break
