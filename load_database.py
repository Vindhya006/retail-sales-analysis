from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent

CSV_FILE = PROJECT_DIR / "data" / "processed" / "orders_cleaned.csv"
DB_FILE = PROJECT_DIR / "data" / "retail_sales.db"

# Read the prepared data.
orders = pd.read_csv(
    CSV_FILE,
    dtype={"Postal Code": "string"}
)

# Convert column names to SQL-friendly names.
# Example: "Order ID" becomes "order_id".
orders.columns = (
    orders.columns
    .str.lower()
    .str.replace(r"[^a-z0-9]+", "_", regex=True)
    .str.strip("_")
)

# Connect to the database, creating the file if necessary.
connection = sqlite3.connect(DB_FILE)

try:
    # Replace the orders table with the current prepared dataset.
    orders.to_sql(
        "orders",
        connection,
        if_exists="replace",
        index=False
    )

    # Run our first SQL query.
    query = """
    SELECT
        COUNT(*) AS line_items,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit
    FROM orders;
    """

    result = pd.read_sql_query(query, connection)

    print("--- SQL Business Summary ---")
    print(result.to_string(index=False))
    print(f"\nDatabase saved: {DB_FILE}")

finally:
    connection.close()