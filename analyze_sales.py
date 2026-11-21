from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "data" / "processed" / "orders_cleaned.csv"

# Restore dates and preserve leading zeros in postal codes.
orders = pd.read_csv(
    INPUT_FILE,
    dtype={"Postal Code": "string"},
    parse_dates=["Order Date", "Ship Date"]
)

# 1. Calculate overall business metrics.
total_sales = orders["Sales"].sum()
total_profit = orders["Profit"].sum()
total_orders = orders["Order ID"].nunique()
total_customers = orders["Customer ID"].nunique()
total_quantity = orders["Quantity"].sum()

average_order_value = total_sales / total_orders
profit_margin = total_profit / total_sales * 100

print("--- Business Summary ---")
print(f"Total sales: {total_sales:,.2f}")
print(f"Total profit: {total_profit:,.2f}")
print(f"Distinct orders: {total_orders:,}")
print(f"Distinct customers: {total_customers:,}")
print(f"Units sold: {total_quantity:,}")
print(f"Average order value: {average_order_value:,.2f}")
print(f"Profit margin: {profit_margin:.2f}%")

# 2. Compare product categories.
category_summary = (
    orders.groupby("Category")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("Order ID", "nunique")
    )
    .reset_index()
)

# Calculate each category's margin using its totals.
category_summary["Profit Margin (%)"] = (
    category_summary["Profit"] / category_summary["Sales"] * 100
)

category_summary = category_summary.sort_values(
    "Sales", ascending=False
)

print("\n--- Category Performance ---")
print(category_summary.round(2).to_string(index=False))

# 3. Save the summary for later reporting.
OUTPUT_DIR = PROJECT_DIR / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "category_summary.csv"
category_summary.to_csv(OUTPUT_FILE, index=False)

print(f"\nCategory report saved: {OUTPUT_FILE}")

# 4. Investigate Furniture performance.
furniture = orders.loc[orders["Category"].eq("Furniture")].copy()

furniture_summary = (
    furniture.groupby("Sub-Category")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"),
        Average_Discount=("Discount", "mean")
    )
    .reset_index()
)

furniture_summary["Profit Margin (%)"] = (
    furniture_summary["Profit"] / furniture_summary["Sales"] * 100
)

furniture_summary["Average Discount (%)"] = (
    furniture_summary.pop("Average_Discount") * 100
)

# Show the least profitable sub-categories first.
furniture_summary = furniture_summary.sort_values("Profit")

print("\n--- Furniture Sub-Category Performance ---")
print(furniture_summary.round(2).to_string(index=False))

FURNITURE_FILE = OUTPUT_DIR / "furniture_subcategory_summary.csv"
furniture_summary.to_csv(FURNITURE_FILE, index=False)

print(f"\nFurniture report saved: {FURNITURE_FILE}")

# 5. Investigate discounts for Tables and Bookcases.
target_rows = furniture.loc[
    furniture["Sub-Category"].isin(["Tables", "Bookcases"])
].copy()

discount_summary = (
    target_rows.groupby(["Sub-Category", "Discount"])
    .agg(
        Line_Items=("Row ID", "count"),
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
)

discount_summary["Profit Margin (%)"] = (
    discount_summary["Profit"] / discount_summary["Sales"] * 100
)

discount_summary["Discount (%)"] = (
    discount_summary["Discount"] * 100
)

discount_summary = discount_summary[
    [
        "Sub-Category",
        "Discount (%)",
        "Line_Items",
        "Sales",
        "Profit",
        "Profit Margin (%)"
    ]
]

print("\n--- Discount and Profitability ---")
print(discount_summary.round(2).to_string(index=False))

DISCOUNT_FILE = OUTPUT_DIR / "discount_profitability.csv"
discount_summary.to_csv(DISCOUNT_FILE, index=False)

print(f"\nDiscount report saved: {DISCOUNT_FILE}")

# 6. Analyze monthly sales and profitability.
monthly_summary = (
    orders.groupby("Order Month")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    )
    .reset_index()
    .sort_values("Order Month")
)

monthly_summary["Profit Margin (%)"] = (
    monthly_summary["Profit"] / monthly_summary["Sales"] * 100
)

monthly_summary["Average Order Value"] = (
    monthly_summary["Sales"] / monthly_summary["Orders"]
)

print("\n--- Monthly Performance ---")
print(monthly_summary.round(2).to_string(index=False))

MONTHLY_FILE = OUTPUT_DIR / "monthly_performance.csv"
monthly_summary.to_csv(MONTHLY_FILE, index=False)

print(f"\nMonthly report saved: {MONTHLY_FILE}")

# 7. Compare yearly performance.
yearly_summary = (
    orders.groupby(orders["Order Date"].dt.year)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    )
    .rename_axis("Year")
    .reset_index()
    .sort_values("Year")
)

yearly_summary["Profit Margin (%)"] = (
    yearly_summary["Profit"] / yearly_summary["Sales"] * 100
)

yearly_summary["Sales Growth (%)"] = (
    yearly_summary["Sales"].pct_change(fill_method=None) * 100
)

yearly_summary["Profit Growth (%)"] = (
    yearly_summary["Profit"].pct_change(fill_method=None) * 100
)

print("\n--- Yearly Performance ---")
print(
    yearly_summary.round(2).to_string(
        index=False,
        na_rep="N/A"
    )
)

YEARLY_FILE = OUTPUT_DIR / "yearly_performance.csv"
yearly_summary.to_csv(YEARLY_FILE, index=False)

print(f"\nYearly report saved: {YEARLY_FILE}")


# 8. Compare category profitability across years.
year_category_summary = (
    orders.groupby(["Order Year", "Category"])
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
    .sort_values(["Order Year", "Category"])
)

year_category_summary["Profit Margin (%)"] = (
    year_category_summary["Profit"]
    / year_category_summary["Sales"]
    * 100
)

# Calculate each category's share of its year's total sales.
annual_sales = year_category_summary.groupby(
    "Order Year"
)["Sales"].transform("sum")

year_category_summary["Sales Share (%)"] = (
    year_category_summary["Sales"] / annual_sales * 100
)

# Display the two years we want to compare.
recent_years = year_category_summary.loc[
    year_category_summary["Order Year"].isin([2025, 2026])
]

print("\n--- Category Comparison: 2025 vs 2026 ---")
print(recent_years.round(2).to_string(index=False))

CATEGORY_YEAR_FILE = OUTPUT_DIR / "year_category_performance.csv"
year_category_summary.to_csv(CATEGORY_YEAR_FILE, index=False)

print(f"\nYear-category report saved: {CATEGORY_YEAR_FILE}")

# 9. Compare sub-category margins between 2025 and 2026.
comparison_rows = orders.loc[
    orders["Order Year"].isin([2025, 2026])
]

subcategory_year = (
    comparison_rows.groupby(
        ["Category", "Sub-Category", "Order Year"]
    )
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
)

subcategory_year["Margin"] = (
    subcategory_year["Profit"] / subcategory_year["Sales"] * 100
)

# Place the two years side by side.
margin_comparison = subcategory_year.pivot(
    index=["Category", "Sub-Category"],
    columns="Order Year",
    values="Margin"
)

margin_comparison = margin_comparison.rename(
    columns={
        2025: "2025 Margin (%)",
        2026: "2026 Margin (%)"
    }
)

margin_comparison["Change (percentage points)"] = (
    margin_comparison["2026 Margin (%)"]
    - margin_comparison["2025 Margin (%)"]
)

margin_comparison = (
    margin_comparison
    .sort_values("Change (percentage points)")
    .reset_index()
)

margin_comparison.columns.name = None

print("\n--- Sub-Category Margin Changes ---")
print(margin_comparison.round(2).to_string(index=False))

COMPARISON_FILE = OUTPUT_DIR / "subcategory_margin_changes.csv"
margin_comparison.to_csv(COMPARISON_FILE, index=False)

print(f"\nSub-category comparison saved: {COMPARISON_FILE}")

# 10. Compare actual profit amounts between the two years.
profit_comparison = subcategory_year.pivot(
    index=["Category", "Sub-Category"],
    columns="Order Year",
    values=["Sales", "Profit"]
)

# Flatten column names, for example ("Sales", 2025) -> "Sales 2025".
profit_comparison.columns = [
    f"{metric} {year}"
    for metric, year in profit_comparison.columns
]

profit_comparison["Profit Change"] = (
    profit_comparison["Profit 2026"]
    - profit_comparison["Profit 2025"]
)

profit_comparison = (
    profit_comparison
    .sort_values("Profit Change")
    .reset_index()
)

print("\n--- Sub-Category Profit Changes ---")
print(profit_comparison.round(2).to_string(index=False))

PROFIT_CHANGE_FILE = OUTPUT_DIR / "subcategory_profit_changes.csv"
profit_comparison.to_csv(PROFIT_CHANGE_FILE, index=False)

print(f"\nProfit comparison saved: {PROFIT_CHANGE_FILE}")

# Export overall metrics for the Excel dashboard.
kpi_summary = pd.DataFrame([{
    "Total Sales": total_sales,
    "Total Profit": total_profit,
    "Profit Margin": total_profit / total_sales,
    "Distinct Orders": total_orders,
    "Distinct Customers": total_customers,
    "Average Order Value": average_order_value
}])

KPI_FILE = OUTPUT_DIR / "kpi_summary.csv"
kpi_summary.to_csv(KPI_FILE, index=False)

print(f"\nKPI summary saved: {KPI_FILE}")