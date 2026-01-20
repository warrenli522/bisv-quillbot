import os
import re

import pandas as pd

from pandas import DataFrame

def get_sheet() -> DataFrame:
    """
    Retrieves the sheet data and adds cycle information.
    
    :return: A DataFrame representing the sheet data with cycle information
    :rtype: DataFrame
    """
    sheet_id = os.getenv("SHEET_ID")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    #drop empty rows & header (only articles + cycle titles remain)
    df = pd.read_excel(url).dropna(subset=["ARTICLE TITLE"]).iloc[3:] # type: ignore

    #add another column for cycle number
    cycle_mask = df["ARTICLE TITLE"].str.match(r"^\s*cycle\s*\d+", flags=re.IGNORECASE)
    cycles = df["ARTICLE TITLE"].where(cycle_mask).str.extract(
                                                        r"cycle (\d+)", flags=re.IGNORECASE
                                                    )[0]
    df["CYCLE"] = cycles.reindex(df.index).ffill().astype(int)
    df = df[~cycle_mask]

    #fix types
    bool_cols = [
        "DRAFT1", "COLUMN EDIT", "REVISED", "EIC EDIT", "REVISED.1",
        "Shapiro Edits", "REVISE Shapiro Edits", "Published"
    ]

    for col in bool_cols:
        df[col] = df[col].astype(bool)

    return df.reset_index(drop=True)
