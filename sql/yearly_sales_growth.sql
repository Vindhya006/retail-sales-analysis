WITH yearly_totals AS (
    SELECT
        order_year,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit
    FROM orders
    GROUP BY order_year
),
previous_year_values AS (
    SELECT
        *,
        LAG(order_year) OVER (
            ORDER BY order_year
        ) AS previous_year,
        LAG(total_sales) OVER (
            ORDER BY order_year
        ) AS previous_sales
    FROM yearly_totals
)
SELECT
    order_year,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(total_profit, 2) AS total_profit,
    CASE
        WHEN previous_year = order_year - 1
        THEN ROUND(
            100.0 * (total_sales - previous_sales)
            / NULLIF(previous_sales, 0),
            2
        )
        ELSE NULL
    END AS sales_growth_pct
FROM previous_year_values
ORDER BY order_year;