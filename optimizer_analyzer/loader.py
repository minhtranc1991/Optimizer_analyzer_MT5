"""Load an MT5 optimization report exported as Excel-XML (SpreadsheetML)."""
import xml.etree.ElementTree as ET

import pandas as pd

NS = "{urn:schemas-microsoft-com:office:spreadsheet}"
BOOLS = {"true": 1, "false": 0, "True": 1, "False": 0}


def _row_values(row):
    values = []
    for cell in row.findall(f"{NS}Cell"):
        index = cell.get(f"{NS}Index")  # 1-based; present when cells are skipped
        if index:
            values += [None] * (int(index) - 1 - len(values))
        data = cell.find(f"{NS}Data")
        values.append(data.text if data is not None else None)
    return values


def load_report(xml_file):
    worksheet = ET.parse(xml_file).getroot().find(f".//{NS}Worksheet")
    if worksheet is None:
        raise ValueError(f"{xml_file}: no Worksheet found")

    raw = [_row_values(r) for r in worksheet.iter(f"{NS}Row")]
    if len(raw) < 2:
        raise ValueError(f"{xml_file}: no data rows")

    header = raw[0]
    n = len(header)
    records = [(r + [None] * (n - len(r)))[:n] for r in raw[1:]]
    df = pd.DataFrame(records, columns=header)

    for c in df.columns:
        numeric = pd.to_numeric(df[c].replace(BOOLS), errors="coerce")
        if numeric.notna().sum() == df[c].notna().sum():
            df[c] = numeric
    return df
