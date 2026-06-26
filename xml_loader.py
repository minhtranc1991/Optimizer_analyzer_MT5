# ============================================================
# XML LOADER
# ============================================================

import pandas as pd
import xml.etree.ElementTree as ET

class XMLLoader:

    @staticmethod
    def load(xml_file):

        print(f"Loading {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        worksheet = root.find(
            ".//{urn:schemas-microsoft-com:office:spreadsheet}Worksheet"
        )

        rows = worksheet.findall(
            ".//{urn:schemas-microsoft-com:office:spreadsheet}Row"
        )

        raw = []

        for row in rows:

            values = []

            for cell in row.findall(
                "{urn:schemas-microsoft-com:office:spreadsheet}Cell"
            ):

                data = cell.find(
                    "{urn:schemas-microsoft-com:office:spreadsheet}Data"
                )

                values.append(
                    data.text if data is not None else None
                )

            raw.append(values)

        header = raw[0]

        records = []

        for r in raw[1:]:

            if len(r) < len(header):
                r += [None] * (len(header) - len(r))

            records.append(r[:len(header)])

        df = pd.DataFrame(
            records,
            columns=header
        )

        for col in df.columns:

            try:
                df[col] = pd.to_numeric(df[col])

            except Exception:
                pass

        print(f"Rows: {len(df):,}")

        return df