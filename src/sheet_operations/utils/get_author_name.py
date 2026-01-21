import json

def get_name_by_id(discord_id: int) -> str | None:
    """Returns the author name associated with a given discord ID"""
    with open("data/member_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        if int(entry["discordID"]) == discord_id:
            return entry["name"]
    return None
