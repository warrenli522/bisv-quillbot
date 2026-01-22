import os
import re

import pandas as pd
from pandas import DataFrame

from src.sheet_operations.utils.extract_names import extract_names

def get_sheet() -> DataFrame:
    """
    Retrieves the sheet data and adds cycle information.
    
    :return: A DataFrame with the sheet data. 'CYCLE' contains cycle number,
    'AUTHORS' contains a tuple of extracted author names.

    :rtype: DataFrame
    """
    sheet_id = os.getenv("SHEET_ID")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    #clean empty rows/header
    df = pd.read_excel(url).dropna(subset=["ARTICLE TITLE"]).iloc[3:] # type: ignore

    #add another column for cycle number & remove cycle headers
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

    #extract & format author/editor names
    df["AUTHORS"] = df["AUTHORS"].apply(extract_names) #type: ignore
    df["SECTION EDITOR"] = df["SECTION EDITOR"].str.lower().str.strip()
    df["EIC"] = df["EIC"].str.lower().str.strip()
    return df.reset_index(drop=True)
