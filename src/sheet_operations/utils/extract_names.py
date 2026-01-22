import json
from typing import List, Tuple

#NOTE: this method is quite inefficient (but foolproof)
def extract_names(author_str: str) -> Tuple[str, ...]:
    """
    Extracts individual author names from a string of authors separated by commas.
    
    :param author_str: The author string from the sheet
    :type author_str: str
    :return: A list of individual author names
    :rtype: Tuple[str]
    """
    author_str = author_str.lower().strip()
    with open("data/member_info.json", "r", encoding="utf-8") as f:
        author_names = json.load(f).keys()

    extracted_names: List[str] = []
    for name in author_names:
        if name in author_str:
            extracted_names.append(name)
    return tuple(extracted_names)
