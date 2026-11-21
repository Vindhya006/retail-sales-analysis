SELECT
        order_id,
        order_date,
        product_name,
        quantity,
        ROUND(discount * 100, 2) AS discount_pct,
        ROUND(sales, 2) AS sales,
        ROUND(profit, 2) AS profit
    FROM orders
    WHERE order_year = ?
      AND product_id IN (?, ?)
    ORDER BY profit ASC, order_id;