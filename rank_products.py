from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DB_FILE = PROJECT_DIR / "data" / "retail_sales.db"
QUERY_FILE = PROJECT_DIR / "sql" / "top_products_by_category.sql"
REPORT_DIR = PROJECT_DIR / "reports"

if not DB_FILE.exists():
    raise FileNotFoundError("Run load_database.py first.")

query = QUERY_FILE.read_text(encoding="utf-8")
connection = sqlite3.connect(DB_FILE)

try:
    result = pd.read_sql_query(
        query,
        connection,
        params=(2026,)
    )

    print("--- Top 3 Products per Category by Profit: 2026 ---")
    print(result.to_string(index=False))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = REPORT_DIR / "top_products_by_category_2026.csv"
    result.to_csv(output_file, index=False)

    print(f"\nReport saved: {output_file}")

finally:
    connection.close()