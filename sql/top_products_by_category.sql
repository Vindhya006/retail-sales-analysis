WITH product_totals AS (
    SELECT
        category,
        product_id,
        product_name,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit
    FROM orders
    WHERE order_year = ?
    GROUP BY category, product_id, product_name
),
ranked_products AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY total_profit DESC, product_id, product_name
        ) AS profit_rank
    FROM product_totals
)
SELECT
    category,
    profit_rank,
    product_id,
    product_name,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(total_profit, 2) AS total_profit
FROM ranked_products
WHERE profit_rank <= 3
ORDER BY category, profit_rank;