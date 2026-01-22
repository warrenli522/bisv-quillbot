from datetime import datetime, timezone
from typing import Optional
from pandas import DataFrame

from src.sheet_operations.enums.article_status import ArticleStatus
from src.sheet_operations.utils.annotate_status import annotate_status

def get_edits(sheet: DataFrame, author: Optional[str] = None,
              editor: Optional[str] = None, late: bool = False) -> DataFrame:
    """
    Retrieves all articles with unrevised edits

    :param sheet: The DataFrame with the article data
    :type sheet: DataFrame
    :param author: If provided, only checks articles authored by this author;
        if None, checks all articles on the sheet. Cannot be used with editor.
    :type author: Optional[str]
    :param editor: If provided, only checks articles assigned to this editor;
        if None, checks all articles on the sheet. Cannot be used with author.
    :type editor: Optional[str]
    :param late: If True, only returns articles that are late.
    :type late: bool
    :return: A DataFrame of articles that have their status tagged in a "status"
        column and a "late" bool indicating whether the article is late.
    :rtype: DataFrame
    """
    if author and editor:
        raise ValueError("Cannot filter by both author and editor simultaneously.")

    if author:
        sheet = sheet[sheet["AUTHORS"].apply(lambda authors: author in authors)] #type: ignore
    if editor:
        editor_cols = ["SECTION EDITOR", "EIC"]
        mask = sheet[editor_cols].stack().str.contains(editor, regex=False)
        sheet = sheet[mask.groupby( #type: ignore
            level=0).any().reindex(sheet.index, fill_value=False)]

    cur_time = datetime.now(timezone.utc)
    sheet = annotate_status(sheet, cur_time=cur_time)
    if late:
        sheet = sheet[sheet["late"].fillna(False)] #type: ignore
    if author:
        author_statuses = [ArticleStatus.SECTION_REVISE.value, ArticleStatus.EIC_REVISE.value,
                           ArticleStatus.SHAPIRO_REVISE.value]
        return sheet[sheet["status"].isin(author_statuses)] #type: ignore
    if editor:
        editor_statuses = [ArticleStatus.SECTION.value, ArticleStatus.EIC.value,
                           ArticleStatus.SHAPIRO_EDIT.value]
        return sheet[sheet["status"].isin(editor_statuses)] #type: ignore
    return sheet[sheet["status"] != ArticleStatus.PUBLISHED.value]
