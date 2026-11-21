from pathlib import Path
import pandas as pd

# Find the folder containing this script.
PROJECT_DIR = Path(__file__).resolve().parent

# Build the path to our Excel file.
INPUT_FILE = PROJECT_DIR / "data" / "sample_-_superstore.xls"

# Read the Orders worksheet into a DataFrame.
orders = pd.read_excel(INPUT_FILE, sheet_name="Orders")

print("Dataset loaded successfully!")
print("Rows:", len(orders))
print("Columns:", len(orders.columns))
print("Distinct orders:", orders["Order ID"].nunique())
print(f"Total sales: {orders['Sales'].sum():,.2f}")
print(f"Total profit: {orders['Profit'].sum():,.2f}")

# Preview the first five rows.
print("\n--- First 5 rows ---")
print(orders.head())

# Inspect column types and non-missing counts.
print("\n--- Column information ---")
orders.info()

# Count missing values in each column.
print("\n--- Missing values per column ---")
print(orders.isna().sum())

# Count rows where every column matches another row.
print("\n--- Exact duplicate rows ---")
print(orders.duplicated().sum())

# Display the column names.
print("\n--- Column names ---")
print(orders.columns.tolist())

# Check text columns for empty strings or spaces.
print("\n--- Blank text values ---")
text_columns = orders.select_dtypes(
    include=["object", "string"]
).columns

for column in text_columns:
    blank_count = (
        orders[column]
        .astype("string")
        .str.strip()
        .eq("")
        .sum()
    )
    print(f"{column}: {blank_count}")

# Row ID should identify an individual product line.
print("\n--- Repeated Row IDs ---")
print(orders["Row ID"].duplicated().sum())

# Flag unusual values for investigation.
print("\n--- Business validation checks ---")
print(
    "Ship date before order date:",
    (orders["Ship Date"] < orders["Order Date"]).sum()
)
print("Sales zero or negative:", (orders["Sales"] <= 0).sum())
print("Quantity zero or negative:", (orders["Quantity"] <= 0).sum())
print(
    "Discount outside 0–1:",
    ((orders["Discount"] < 0) | (orders["Discount"] > 1)).sum()
)

# Understand the dataset's coverage.
print("\n--- Date range ---")
print("Earliest order:", orders["Order Date"].min())
print("Latest order:", orders["Order Date"].max())

print("\n--- Countries / Regions ---")
print(orders["Country/Region"].value_counts())

print("\n--- Postal Code examples ---")
print(orders["Postal Code"].head(10).tolist())

# Create a separate copy for analysis.
clean_orders = orders.copy()

# Stop preparation if the dataset violates our validation rules.
validation_checks = {
    "Dataset is empty": orders.empty,
    "Missing values": orders.isna().any().any(),
    "Duplicate Row IDs": orders["Row ID"].duplicated().any(),
    "Ship date before order date": (
        orders["Ship Date"] < orders["Order Date"]
    ).any(),
    "Sales zero or negative": (orders["Sales"] <= 0).any(),
    "Quantity zero or negative": (orders["Quantity"] <= 0).any(),
    "Fractional quantities": (orders["Quantity"] % 1 != 0).any(),
    "Discount outside 0–1": (
        (orders["Discount"] < 0) | (orders["Discount"] > 1)
    ).any(),
}

# Check for empty or whitespace-only text.
for column in orders.select_dtypes(
    include=["object", "string"]
).columns:
    validation_checks[f"Blank text in {column}"] = (
        orders[column]
        .astype("string")
        .str.strip()
        .eq("")
        .any()
    )

failed_checks = [
    name
    for name, failed in validation_checks.items()
    if failed
]

if failed_checks:
    raise ValueError(
        "Data validation failed:\n- "
        + "\n- ".join(failed_checks)
    )

print("\nData validation passed.")

# Remove spaces at the start and end of text values.
text_columns = clean_orders.select_dtypes(
    include=["object", "string"]
).columns

for column in text_columns:
    clean_orders[column] = (
        clean_orders[column].astype("string").str.strip()
    )

# Postal codes are identifiers, not numbers.
# US ZIP codes need five digits, including any leading zero.
us_rows = clean_orders["Country/Region"].eq("United States")

clean_orders.loc[us_rows, "Postal Code"] = (
    clean_orders.loc[us_rows, "Postal Code"]
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(5)
)

# Add date fields for yearly and monthly analysis.
clean_orders["Order Year"] = clean_orders["Order Date"].dt.year
clean_orders["Order Month"] = (
    clean_orders["Order Date"].dt.to_period("M").astype("string")
)

# Calculate days between ordering and shipping.
clean_orders["Shipping Days"] = (
    clean_orders["Ship Date"] - clean_orders["Order Date"]
).dt.days

# Calculate profit margin for each product line.
# Our checks confirmed that every Sales value is positive.
clean_orders["Profit Margin (%)"] = (
    clean_orders["Profit"] / clean_orders["Sales"] * 100
)

# Create the output folder and save the prepared dataset.
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "orders_cleaned.csv"
clean_orders.to_csv(OUTPUT_FILE, index=False)

print("\n--- Prepared dataset saved ---")
print("File:", OUTPUT_FILE)
print("Rows:", len(clean_orders))
print("Columns:", len(clean_orders.columns))

# Overall margin must use totals, not the average of row margins.
overall_margin = (
    clean_orders["Profit"].sum()
    / clean_orders["Sales"].sum()
    * 100
)
print(f"Overall profit margin: {overall_margin:.2f}%")

