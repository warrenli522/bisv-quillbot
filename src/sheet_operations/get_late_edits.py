import json
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
from pandas import DataFrame

import sys
sys.path.append("/Users/warrenli/GitHub/bisv-quillbot")  # to allow importing from src when running this file directly
from src.sheet_operations.utils.get_sheet import get_sheet

def get_late_edits(sheet: DataFrame,
                   author: Optional[str] = None, editor: Optional[str] = None) -> DataFrame:
    """
    Retrieves all articles with late edits (either not revised or not edited).

    :param sheet: The DataFrame with the article data
    :type sheet: DataFrame
    :param author: If provided, only checks articles authored by this author;
        if None, checks all articles on the sheet. Cannot be used with editor.
    :type author: Optional[str]
    :param editor: If provided, only checks articles assigned to this editor;
        if None, checks all articles on the sheet. Cannot be used with author.
    :type editor: Optional[str]
    :return: A DataFrame of articles that have late edits. Contains an extra
        column "reason_late", which indicates what was late. Possible values
        are: "section_edit", "section_revise", "eic_edit", "eic_revise".
    :rtype: DataFrame
    """
    if author and editor:
        raise ValueError("Cannot filter by both author and editor simultaneously.")

    late_articles = sheet.head(0)
    with open("data/cycle_info.json", "r", encoding="utf-8") as f:
        due_dates = json.load(f)
    if author:
        sheet = sheet[sheet["AUTHORS"].str.contains(author, regex=False)]
    if editor:
        editor_cols = ["SECTION EDITOR", "EIC"]
        mask = sheet[editor_cols].stack().str.contains(editor, regex=False)
        sheet = sheet[mask.groupby( #type: ignore
            level=0).any().reindex(sheet.index, fill_value=False)]


    cur_time = datetime.now(timezone.utc)
    for article in sheet.iterrows():
        cycle = due_dates[str(article[1]["CYCLE"])]

        if article[1]["DRAFT1"]:
            if (not article[1]["COLUMN EDIT"] and
                    cur_time > datetime.fromisoformat(cycle["sectionEditsDue"])):
                late_articles = pd.concat([late_articles, pd.DataFrame([article[1]])])
                late_articles.at[late_articles.index[-1], "reason_late"] = "section_edit"
            elif (not article[1]["REVISED"] and
                    cur_time > datetime.fromisoformat(cycle["sectionRevisedDue"])):
                late_articles = pd.concat([late_articles, pd.DataFrame([article[1]])])
                late_articles.at[late_articles.index[-1], "reason_late"] = "section_revise"
            elif (not article[1]["EIC EDIT"] and
                    cur_time > datetime.fromisoformat(cycle["eicEditsDue"])):
                late_articles = pd.concat([late_articles, pd.DataFrame([article[1]])])
                late_articles.at[late_articles.index[-1], "reason_late"] = "eic_edit"
            elif (not article[1]["REVISED.1"] and
                    cur_time > datetime.fromisoformat(cycle["eicRevisedDue"])):
                late_articles = pd.concat([late_articles, pd.DataFrame([article[1]])])
                late_articles.at[late_articles.index[-1], "reason_late"] = "eic_revise"
            elif (not article[1]["Shapiro Edits"] and
                    cur_time > datetime.fromisoformat(cycle["shapiroReviseDue"]) and
                    article[1]["Shapiro Edits"]):
                late_articles = pd.concat([late_articles, pd.DataFrame([article[1]])])
                late_articles.at[late_articles.index[-1], "reason_late"] = "shapiro_revise"

    if editor and not late_articles.empty:
        late_articles = late_articles[late_articles["reason_late"].isin( #type: ignore
            ["section_edit", "eic_edit"])]
    if author and not late_articles.empty:
        late_articles = late_articles[late_articles["reason_late"].isin( #type: ignore
            ["section_revise", "eic_revise", "shapiro_revise"])]
    return late_articles

df = get_sheet()

print(get_late_edits(df, editor="Nishka"))