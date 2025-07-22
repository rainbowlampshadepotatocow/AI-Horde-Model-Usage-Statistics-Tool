# SPDX-License-Identifier: Apache-2.0
"""Utility script for fetching AI Horde model usage statistics.

This script downloads usage statistics from the AI Horde API and exports them as
CSV and Excel workbooks. Optionally, model names can be normalised using a
``models.csv`` whitelist placed inside the ``user-files`` directory.

The generated files are written back to ``user-files``.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict

import pandas as pd
import requests
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


API_URL = "https://aihorde.net/api/v2/stats/text/models"

# Directory where input and output files are stored
USER_FILES_DIR = os.path.join(os.path.dirname(__file__), "user-files")
USAGE_JSON = os.path.join(USER_FILES_DIR, "RawModelUsageData.json")
MODELS_CSV = os.path.join(USER_FILES_DIR, "models.csv")
USAGE_CSV = os.path.join(USER_FILES_DIR, "usage_data.csv")
USAGE_XLSX = os.path.join(USER_FILES_DIR, "usage_data.xlsx")


def fetch_usage_data() -> Dict[str, Dict[str, int]]:
    """Fetch the raw usage information from the AI Horde API."""

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def save_json(data: dict, path: str) -> None:
    """Save *data* as nicely formatted JSON to *path*."""

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_usage_df(data: Dict[str, Dict[str, int]]) -> pd.DataFrame:
    """Convert the raw API response into a tidy :class:`pandas.DataFrame`."""

    records = []
    for period, models in data.items():
        for model_name, count in models.items():
            records.append({"period": period, "model": model_name, "usage_count": count})
    return pd.DataFrame(records)


def export_usage_excel(df: pd.DataFrame, path: str) -> None:
    """Write the usage dataframe to ``path`` with one sheet per period."""

    with pd.ExcelWriter(path) as writer:
        for period, group in df.groupby("period"):
            sheet = period.capitalize()
            group.drop(columns="period").to_excel(writer, index=False, sheet_name=sheet)

    _format_excel_tables(path)


def _format_excel_tables(path: str) -> None:
    """Apply table formatting and auto-fit column widths in-place."""

    wb = load_workbook(path)
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        max_row = ws.max_row
        max_col = ws.max_column
        end_col = get_column_letter(max_col)
        table_ref = f"A1:{end_col}{max_row}"
        table = Table(displayName=f"{sheet}Table", ref=table_ref)
        style = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        table.tableStyleInfo = style
        ws.add_table(table)

        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    wb.save(path)


def clean_and_merge(path: str) -> None:
    """Clean model names using a whitelist and merge duplicate entries."""

    official_quant_regex = re.compile(
        r"[.,-][a-zA-Z0-9]+?-?Q(-[Ii]nt)?[2-9]{1,2}([_.-][0-9a-zA-Z]+)*$",
        re.IGNORECASE,
    )
    extra_suffix_regex = re.compile(r"(?i)([._-](?:iMat|iMatrix|i\d+|b\d+|c\d+|ch\d+|bpw|h\d+|exl\d+).*)$")

    def strip_quant(name: str) -> str:
        name = official_quant_regex.sub("", name)
        return extra_suffix_regex.sub("", name)

    model_short_map: Dict[str, str] = {}
    if os.path.exists(MODELS_CSV):
        models_df = pd.read_csv(MODELS_CSV)
        models_df["model_short"] = models_df["name"].astype(str).str.split("/").str[-1]
        model_short_map = {ms.lower(): ms for ms in models_df["model_short"]}

    def map_to_whitelist(raw_short: str) -> str | None:
        raw_lower = raw_short.lower()
        for short_lower, short_orig in model_short_map.items():
            if raw_lower.endswith(short_lower):
                return short_orig
        return None

    wb = load_workbook(path)
    cleaned_dfs = {}
    for sheet in wb.sheetnames:
        df = pd.read_excel(path, sheet_name=sheet)
        df["raw_short"] = df["model"].astype(str).str.split("/").str[-1]
        df["mapped"] = df["raw_short"].apply(map_to_whitelist)
        df["whitelisted"] = df["mapped"].notnull()
        df["cleaned"] = df["raw_short"].apply(strip_quant)
        df["model"] = df.apply(
            lambda r: r["mapped"] if pd.notnull(r["mapped"]) else r["cleaned"],
            axis=1,
        )
        df_merged = df.groupby("model", as_index=False).agg({"usage_count": "sum", "whitelisted": "max"})
        df_merged["whitelisted"] = df_merged["whitelisted"].apply(lambda x: "T" if x else "F")
        cleaned_dfs[sheet] = df_merged

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, cdf in cleaned_dfs.items():
            cdf.to_excel(writer, index=False, sheet_name=sheet)

    _format_excel_tables(path)


def main() -> None:
    os.makedirs(USER_FILES_DIR, exist_ok=True)

    print(f"Fetching usage data from {API_URL}...")
    usage_data = fetch_usage_data()
    save_json(usage_data, USAGE_JSON)

    df_usage = build_usage_df(usage_data)
    df_usage.to_csv(USAGE_CSV, index=False)

    export_usage_excel(df_usage, USAGE_XLSX)

    print("Cleaning model names and merging duplicates...")
    clean_and_merge(USAGE_XLSX)
    print(f"Done. Files written to {USER_FILES_DIR}")


if __name__ == "__main__":
    main()

# # Step 3: Determine top N models per period
# top_models = {}
# for period, group in df_usage.groupby('period'):
#     # Sort by usage and take top N
#     top_list = group.sort_values('usage_count', ascending=False)
#     top_models[period] = set(top_list.head(TOP_N)['model'].tolist())
#     print(f"Top {TOP_N} for {period}: {len(top_models[period])} models")


# # Step 4: Load existing models whitelist
# df_models = pd.read_csv(MODELS_CSV)
# # Ensure tags column exists
# if 'tags' not in df_models.columns:
#     df_models['tags'] = ''

# # Step 5: Update tags based on membership in top lists
# new_tags = []
# for _, row in df_models.iterrows():
#     model = row['name']
#     tags = []
#     for period, tag in PERIOD_TAGS.items():
#         if model in top_models.get(period, set()):
#             tags.append(tag)
#     # Join with commas, preserve any existing tags if desired
#     new_tags.append(','.join(tags))

# df_models['tags'] = new_tags

# # Step 6: Save updated CSV
# df_models.to_csv(OUTPUT_CSV, index=False)
# print(f"Updated CSV written to {OUTPUT_CSV}")
