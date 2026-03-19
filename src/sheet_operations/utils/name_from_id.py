import os
from typing import Dict, Any
import json

def get_name_by_id(discord_id: int) -> str | None:
    """Returns the author name associated with a given discord ID"""
    member_data_path = os.getenv("MEMBER_DATA_FILEPATH")
    if member_data_path is None:
        raise ValueError("MEMBER_DATA_FILEPATH environment variable not set.")
    with open(member_data_path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
    for entry in data:
        if int(data[entry]["discordID"]) == discord_id:
            return entry
    return None
