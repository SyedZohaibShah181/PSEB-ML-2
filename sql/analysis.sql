-- Top 10 countries by total revenue
SELECT Country,
       COUNT(*)                     AS n_transactions,
       SUM(Quantity * UnitPrice)    AS total_revenue
FROM sales
GROUP BY Country
ORDER BY total_revenue DESC
LIMIT 10;

-- Monthly revenue + number of active countries (join-style derived table)
SELECT strftime('%Y-%m', InvoiceDate) AS month,
       SUM(Quantity * UnitPrice)      AS revenue,
       COUNT(DISTINCT Country)        AS n_countries
FROM sales
GROUP BY month
ORDER BY month;

-- Query plan analysis (Index experiment baseline)
EXPLAIN QUERY PLAN
SELECT Country, SUM(Quantity * UnitPrice) AS total_revenue
FROM sales GROUP BY Country ORDER BY total_revenue DESC LIMIT 10;
