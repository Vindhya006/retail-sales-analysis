from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DB_FILE = PROJECT_DIR / "data" / "retail_sales.db"

if not DB_FILE.exists():
    raise FileNotFoundError("Run load_database.py first.")

connection = sqlite3.connect(DB_FILE)

try:
    QUERY_FILE = (
        PROJECT_DIR / "sql" / "high_loss_product_transactions.sql"
    )
    query = QUERY_FILE.read_text(encoding="utf-8")

    parameters = (
        2026,
        "TEC-MA-10004125",
        "TEC-MA-10000822"
    )

    result = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    print("--- Transactions for Two High-Loss Products: 2026 ---")
    print(result.to_string(index=False))

     # Save the query results for reporting.
    REPORT_DIR = PROJECT_DIR / "reports"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE = REPORT_DIR / "high_loss_product_transactions.csv"
    result.to_csv(OUTPUT_FILE, index=False)

    print(f"\nReport saved: {OUTPUT_FILE}")

finally:
    connection.close()