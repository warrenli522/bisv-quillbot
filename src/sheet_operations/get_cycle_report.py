import json
from typing import TypedDict

from pandas import DataFrame, Series

from src.sheet_operations.utils.annotate_status import annotate_status

class CycleReport(TypedDict):
    """report of incomplete articles for a given cycle"""
    cycle: int
    missing_articles: Series #list of people who don't have their article on the sheet
    draft_incomplete: DataFrame #articles with draft not marked complete
    unedited_articles: DataFrame #not published articles

def get_cycle_report(sheet: DataFrame, cycle: int) -> CycleReport:
    """
    Gets the following for a given cycle:
    1. missing articles
    2. drafts not marked complete
    3. unedited articles (not published)
    
    :param sheet: The DataFrame with the sheet data
    :type sheet: DataFrame
    :param cycle: The cycle number to check
    :type cycle: int
    :return: A report of incomplete articles for the given cycle. It is a dict with keys:

        - cycle: int

             The cycle number for which the report is generated
        - missing_articles: Series

             A list of author names who do not have their articles listed for the given cycle
        - draft_incomplete: DataFrame

             A DataFrame of annotated articles that are not marked as complete in the draft stage
        - unedited_articles: DataFrame
                A DataFrame of annotated articles currently being edited
    :rtype: CycleReport
    """
    cycle_articles = annotate_status(sheet[sheet["CYCLE"] == cycle])
    with open("data/member_info.json", "r", encoding="utf-8") as f:
        author_names = json.load(f).keys()


    missing_articles = [name for name in author_names
                        if not cycle_articles["AUTHORS"].str.contains(name).any()]
    missing_articles = Series(missing_articles)
    incomplete_articles = cycle_articles[~cycle_articles["DRAFT1"]]
    unedited_articles = cycle_articles[cycle_articles["status"] != "Published"]

    return {
        "cycle": cycle,
        "missing_articles": missing_articles,
        "draft_incomplete": incomplete_articles,
        "unedited_articles": unedited_articles
    }
