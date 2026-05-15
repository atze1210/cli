import json
import sqlite3

import pandas as pd

# File paths
JSON_FILE_PATH = "data/SEC-CTEC-Data/company_tickers_exchange.json"
DB_FILE_PATH = "data/Issuers/Main_Database.db"

# Read JSON data
try:
    with open(JSON_FILE_PATH, "r") as json_file:
        sec_data = json.load(json_file)
except FileNotFoundError:
    raise SystemExit(
        f"JSON file not found: {JSON_FILE_PATH}. Run SEC_company_tickers_exchange.py first.",
    )
except json.JSONDecodeError as error:
    raise SystemExit(f"Failed to parse JSON file {JSON_FILE_PATH}: {error}")

fields = sec_data["fields"]
records = sec_data["data"]

# Convert JSON records to a DataFrame
df = pd.DataFrame(records, columns=fields)

# Replace NaN with empty strings
df = df.fillna("")

# Normalize key fields: strip whitespace and coerce to string
df["cik"] = df["cik"].astype(str).str.strip()
df["ticker"] = df["ticker"].astype(str).str.strip()
df["name"] = df["name"].astype(str).str.strip()

# Deduplicate case-insensitively on primary key columns to prevent duplicate ID
# issues when inserting into the database. Two rows that differ only in
# capitalization would violate the (CIK, Ticker, Company_Name_Issuer) PRIMARY KEY.
df["_cik_norm"] = df["cik"].str.lower()
df["_ticker_norm"] = df["ticker"].str.lower()
df["_name_norm"] = df["name"].str.lower()
df = df.drop_duplicates(subset=["_cik_norm", "_ticker_norm", "_name_norm"])
df = df.drop(columns=["_cik_norm", "_ticker_norm", "_name_norm"])

# Connect to the SQLite database
conn = sqlite3.connect(DB_FILE_PATH)
cursor = conn.cursor()

# Create table with the updated schema if it doesn't exist
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

# Remove duplicate rows in the database that share the same
# (CIK, Ticker, Company_Name_Issuer) when compared case-insensitively.
# Such duplicates can accumulate over time (e.g. from manual edits or older
# schema versions without the PRIMARY KEY constraint) and would cause
# UNIQUE constraint violations during the upsert loop below.
cursor.execute(
    """
    DELETE FROM Main_Database WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM Main_Database
        GROUP BY LOWER(CIK), LOWER(Ticker), LOWER(Company_Name_Issuer)
    )
""",
)

# Update existing rows or insert new rows from SEC data.
# The UPDATE targets a single row by rowid to prevent PRIMARY KEY constraint
# violations that would occur if multiple rows matched the case-insensitive
# WHERE clause and were updated to the same canonical Company_Name_Issuer value.
for _, row in df.iterrows():
    cik_value = row["cik"]
    ticker_value = row["ticker"]
    exchange_value = row["exchange"]
    company_name_issuer_value = row["name"]

    # Attempt to UPDATE an existing row using case-insensitive matching.
    # Using MIN(rowid) ensures at most one row is updated, avoiding duplicate
    # primary key errors when the same company was previously stored with
# inconsistent capitalization.
    cursor.execute(
        """
        UPDATE Main_Database
        SET CIK = ?, Ticker = ?, Exchange = ?, Company_Name_Issuer = ?
        WHERE rowid = (
            SELECT MIN(rowid) FROM Main_Database
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

    # If no rows were updated, INSERT a new one
    if cursor.rowcount == 0:
        cursor.execute(
            """
            INSERT INTO Main_Database (CIK, Ticker, Exchange, Company_Name_Issuer)
            VALUES (?, ?, ?, ?)
        """,
            (cik_value, ticker_value, exchange_value, company_name_issuer_value),
        )

# Clean up whitespace and NULL-like values in non-key columns only
cursor.execute(
    """
UPDATE Main_Database
SET
    Exchange = IFNULL(NULLIF(TRIM(Exchange), ''), ''),
    Transfer_Agent = IFNULL(NULLIF(TRIM(Transfer_Agent), ''), ''),
    Online_Purchase = IFNULL(NULLIF(TRIM(Online_Purchase), ''), ''),
    DTC_Member_Number = IFNULL(NULLIF(TRIM(DTC_Member_Number), ''), ''),
    TA_URL = IFNULL(NULLIF(TRIM(TA_URL), ''), ''),
    Transfer_Agent_Pct = IFNULL(NULLIF(TRIM(Transfer_Agent_Pct), ''), ''),
    IR_Emails = IFNULL(NULLIF(TRIM(IR_Emails), ''), ''),
    IR_Phone_Number = IFNULL(NULLIF(TRIM(IR_Phone_Number), ''), ''),
    IR_Company_Address = IFNULL(NULLIF(TRIM(IR_Company_Address), ''), ''),
    IR_URL = IFNULL(NULLIF(TRIM(IR_URL), ''), ''),
    IR_Contact_Info = IFNULL(NULLIF(TRIM(IR_Contact_Info), ''), ''),
    Shares_Outstanding = IFNULL(NULLIF(TRIM(Shares_Outstanding), ''), ''),
    CUSIP = IFNULL(NULLIF(TRIM(CUSIP), ''), ''),
    Company_Info_URL = IFNULL(NULLIF(TRIM(Company_Info_URL), ''), ''),
    Company_Info = IFNULL(NULLIF(TRIM(Company_Info), ''), ''),
    Full_Progress_Pct = IFNULL(NULLIF(TRIM(Full_Progress_Pct), ''), ''),
    DRS = IFNULL(NULLIF(TRIM(DRS), ''), ''),
    Percent_Shares_DRSd = IFNULL(NULLIF(TRIM(Percent_Shares_DRSd), ''), ''),
    Submission_Received = IFNULL(NULLIF(TRIM(Submission_Received), ''), ''),
    Timestamps_UTC = IFNULL(NULLIF(TRIM(Timestamps_UTC), ''), ''),
    Learn_More_About_DRS = IFNULL(NULLIF(TRIM(Learn_More_About_DRS), ''), ''),
    Certificates_Offered = IFNULL(NULLIF(TRIM(Certificates_Offered), ''), ''),
    S_And_P_500 = IFNULL(NULLIF(TRIM(S_And_P_500), ''), ''),
    Incorporated_In = IFNULL(NULLIF(TRIM(Incorporated_In), ''), '')
""",
)

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

print(f"Database updated from {JSON_FILE_PATH} successfully.")
