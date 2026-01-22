from typing import Dict, Any
import json

def get_name_by_id(discord_id: int) -> str | None:
    """Returns the author name associated with a given discord ID"""
    with open("data/member_info.json", "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
    for entry in data:
        if int(data[entry]["discordID"]) == discord_id:
            return entry
    return None
