import json
from typing import TypedDict, List

from pandas import DataFrame

class CycleReport(TypedDict):
    """report of incomplete articles for a given cycle"""
    cycle: int
    missing_articles: List[str] #list of people who don't have their article on the sheet
    draft_incomplete: DataFrame #articles with draft not marked complete

def get_cycle_report(sheet: DataFrame, cycle: int) -> CycleReport:
    """
    Gets the following for a given cycle:
    1. missing articles, 
    2. articles with wrong/missing perms on Google Doc, and 
    3. articles not marked complete
    
    :param sheet: The DataFrame with the sheet data
    :type sheet: DataFrame
    :param cycle: The cycle number to check
    :type cycle: int
    :return: A report of incomplete articles for the given cycle. It is a dict with keys:

        - cycle: int

             The cycle number for which the report is generated
        - missing_articles: List[str]

             A list of author names who do not have their articles listed for the given cycle
        - bad_perms: DataFrame

             A DataFrame of articles that are not marked as complete in the draft stage
    :rtype: CycleReport
    """
    cycle_articles = sheet[sheet["CYCLE"] == cycle]
    author_names: List[str] = []
    with open("data/member_info.json", "r", encoding="utf-8") as f:
        author_data = json.load(f)
    for author in author_data:
        author_names.append(author["name"])

    missing_articles = [name for name in author_names
                        if not cycle_articles["AUTHORS"].str.contains(name).any()]
    incomplete_articles = cycle_articles[~cycle_articles["DRAFT1"]]

    return {
        "cycle": cycle,
        "missing_articles": missing_articles,
        "draft_incomplete": incomplete_articles
    }
