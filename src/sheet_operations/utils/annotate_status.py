from typing import Any, Dict, Optional
from datetime import datetime, timezone
import json

import pandas as pd
from pandas import DataFrame
from src.sheet_operations.enums.article_status import ArticleStatus

def get_article_status_helper(article: pd.Series, due_dates: Dict[str, Any],
                       cur_time: Optional[datetime] = None) -> pd.Series:
    """
    Get a single article's status (editing stage + lateness)
    
    :param due_dates: The cycle info with due dates
    :type due_dates: Dict[str, Any]
    :param article: An entry from the articles DataFrame
    :type article: pd.Series
    :param cur_time: The time to check lateness against; if None, uses the current time.
    :type cur_time: Optional[datetime]
    :return: A tuple with the article status and whether it is late
    :rtype: Tuple[ArticleStatus, bool]
    """
    if article["Published"]:
        status = ArticleStatus.PUBLISHED.value
    elif not article["DRAFT1"]:
        status = ArticleStatus.DRAFT.value
    elif not article["COLUMN EDIT"]:
        status = ArticleStatus.SECTION.value
    elif not article["REVISED"]:
        status = ArticleStatus.SECTION_REVISE.value
    elif not article["EIC EDIT"]:
        status = ArticleStatus.EIC.value
    elif not article["REVISED.1"]:
        status = ArticleStatus.EIC_REVISE.value
    elif not article["Shapiro Edits"]:
        status = ArticleStatus.SHAPIRO_EDIT.value
    elif not article["REVISE Shapiro Edits"]:
        status = ArticleStatus.SHAPIRO_REVISE.value
    else:
        status = ArticleStatus.PUBLISHED.value

    cycle = due_dates.get(str(article["CYCLE"]))
    if not cycle:
        return pd.Series([status, False], index=["status", "late"])

    due_key_map: Dict[str, str] = {
        ArticleStatus.DRAFT.value: "draftDue",
        ArticleStatus.SECTION.value: "sectionEditsDue",
        ArticleStatus.SECTION_REVISE.value: "sectionRevisedDue",
        ArticleStatus.EIC.value: "eicEditsDue",
        ArticleStatus.EIC_REVISE.value: "eicRevisedDue",
        ArticleStatus.SHAPIRO_EDIT.value: "shapiroEditsDue",
        ArticleStatus.SHAPIRO_REVISE.value: "shapiroRevisedDue",
    }
    due_key = due_key_map.get(status)
    if not due_key:
        #article was published, no need for lateness check
        return pd.Series([status, False], index=["status", "late"])

    cur_time = cur_time or datetime.now(timezone.utc)
    return pd.Series([status, cur_time > datetime.fromisoformat(cycle[due_key])],
                     index=["status", "late"])

def annotate_status(sheet: DataFrame, cur_time: Optional[datetime] = None) -> DataFrame:
    """
    Returns an annotated article sheet with "status" and "late" columns. 
    Late is a bool (is late/not late) and status is an ArticleStatus enum.
    
    :param sheet: The article sheet
    :type sheet: DataFrame
    :param cur_time: The time to check lateness against; if None, uses the current time.
    :type cur_time: Optional[datetime]
    :return: The annotated article sheet with "status" and "late" columns
    :rtype: DataFrame
    """
    with open("data/cycle_info.json", "r", encoding="utf-8") as f:
        due_dates = json.load(f)
    sheet.loc[:, ["status", "late"]] = sheet.apply(get_article_status_helper, axis=1,
                                              due_dates=due_dates,
                                              cur_time=cur_time, result_type="expand")
    return sheet
