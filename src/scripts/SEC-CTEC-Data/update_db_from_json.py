import json
import sqlite3
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
JSON_FILE_PATH = REPO_ROOT / "data" / "SEC-CTEC-Data" / "company_tickers_exchange.json"
DB_FILE_PATH = REPO_ROOT / "data" / "Issuers" / "Main_Database.db"


def load_sec_data() -> dict:
    try:
        with JSON_FILE_PATH.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError as error:
        raise SystemExit(
            f"JSON file not found: {JSON_FILE_PATH}. Run SEC_company_tickers_exchange.py first.",
        ) from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"Failed to parse JSON file {JSON_FILE_PATH}: {error}") from error


def build_dataframe(sec_data: dict) -> pd.DataFrame:
    df = pd.DataFrame(sec_data["data"], columns=sec_data["fields"]).fillna("")

    df["cik"] = df["cik"].astype(str).str.strip()
    df["ticker"] = df["ticker"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()

    df["_cik_norm"] = df["cik"].str.lower()
    df["_ticker_norm"] = df["ticker"].str.lower()
    df["_name_norm"] = df["name"].str.lower()
    df = df.drop_duplicates(subset=["_cik_norm", "_ticker_norm", "_name_norm"])
    return df.drop(columns=["_cik_norm", "_ticker_norm", "_name_norm"])


def main() -> None:
    sec_data = load_sec_data()
    df = build_dataframe(sec_data)

    DB_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Main_Database (
                Ticker TEXT,
                Exchange TEXT,
                Company_Name_Issuer TEXT,
                Transfer_Agent TEXT,
                Online_Purchase TEXT,
                DTC_Member_Number TEXT,
                TA_URL TEXT,
                Transfer_Agent_Pct TEXT,
                IR_Emails TEXT,
                IR_Phone_Number TEXT,
                IR_Company_Address TEXT,
                IR_URL TEXT,
                IR_Contact_Info TEXT,
                Shares_Outstanding TEXT,
                CUSIP TEXT,
                Company_Info_URL TEXT,
                Company_Info TEXT,
                Full_Progress_Pct TEXT,
                CIK TEXT,
                DRS TEXT,
                Percent_Shares_DRSd TEXT,
                Submission_Received TEXT,
                Timestamps_UTC TEXT,
                Learn_More_About_DRS TEXT,
                Certificates_Offered TEXT,
                S_And_P_500 TEXT,
                Incorporated_In TEXT,
                PRIMARY KEY (CIK, Ticker, Company_Name_Issuer)
            )
            """,
        )

        cursor.execute(
            """
            DELETE FROM Main_Database
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM Main_Database
                GROUP BY LOWER(CIK), LOWER(Ticker), LOWER(Company_Name_Issuer)
            )
            """,
        )

        for row in df.itertuples(index=False):
            cik_value = row.cik
            ticker_value = row.ticker
            exchange_value = row.exchange
            company_name_issuer_value = row.name

            cursor.execute(
                """
                UPDATE Main_Database
                SET CIK = ?, Ticker = ?, Exchange = ?, Company_Name_Issuer = ?
                WHERE rowid = (
                    SELECT MIN(rowid)
                    FROM Main_Database
                    WHERE LOWER(CIK) = LOWER(?)
                      AND LOWER(Ticker) = LOWER(?)
                      AND LOWER(Company_Name_Issuer) = LOWER(?)
                )
                """,
                (
                    cik_value,
                    ticker_value,
                    exchange_value,
                    company_name_issuer_value,
                    cik_value,
                    ticker_value,
                    company_name_issuer_value,
                ),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO Main_Database (CIK, Ticker, Exchange, Company_Name_Issuer)
                    VALUES (?, ?, ?, ?)
                    """,
                    (cik_value, ticker_value, exchange_value, company_name_issuer_value),
                )

        cursor.execute(
            """
            UPDATE Main_Database
            SET
                Exchange = IFNULL(TRIM(Exchange), ''),
                Transfer_Agent = IFNULL(TRIM(Transfer_Agent), ''),
                Online_Purchase = IFNULL(TRIM(Online_Purchase), ''),
                DTC_Member_Number = IFNULL(TRIM(DTC_Member_Number), ''),
                TA_URL = IFNULL(TRIM(TA_URL), ''),
                Transfer_Agent_Pct = IFNULL(TRIM(Transfer_Agent_Pct), ''),
                IR_Emails = IFNULL(TRIM(IR_Emails), ''),
                IR_Phone_Number = IFNULL(TRIM(IR_Phone_Number), ''),
                IR_Company_Address = IFNULL(TRIM(IR_Company_Address), ''),
                IR_URL = IFNULL(TRIM(IR_URL), ''),
                IR_Contact_Info = IFNULL(TRIM(IR_Contact_Info), ''),
                Shares_Outstanding = IFNULL(TRIM(Shares_Outstanding), ''),
                CUSIP = IFNULL(TRIM(CUSIP), ''),
                Company_Info_URL = IFNULL(TRIM(Company_Info_URL), ''),
                Company_Info = IFNULL(TRIM(Company_Info), ''),
                Full_Progress_Pct = IFNULL(TRIM(Full_Progress_Pct), ''),
                DRS = IFNULL(TRIM(DRS), ''),
                Percent_Shares_DRSd = IFNULL(TRIM(Percent_Shares_DRSd), ''),
                Submission_Received = IFNULL(TRIM(Submission_Received), ''),
                Timestamps_UTC = IFNULL(TRIM(Timestamps_UTC), ''),
                Learn_More_About_DRS = IFNULL(TRIM(Learn_More_About_DRS), ''),
                Certificates_Offered = IFNULL(TRIM(Certificates_Offered), ''),
                S_And_P_500 = IFNULL(TRIM(S_And_P_500), ''),
                Incorporated_In = IFNULL(TRIM(Incorporated_In), '')
            """,
        )

        cursor.close()

    print(f"Database updated from {JSON_FILE_PATH} successfully.")


if __name__ == "__main__":
    main()
