-- Pareto Analysis for Top 25 HSN Codes (SQLite Compatible)

WITH HSN_Stats AS (
    SELECT 
        "HS_CODE",  -- Ensure column name matches your CSV header (Pandas standardizes to HS_CODE usually)
        SUM(TOTAL_VALUE_INR) as hsn_total_value
    FROM shipments
    GROUP BY "HS_CODE"
),
Ranked_HSN AS (
    SELECT 
        "HS_CODE",
        hsn_total_value,
        -- Calculate Rank
        RANK() OVER (ORDER BY hsn_total_value DESC) as rnk,
        -- Calculate Share
        hsn_total_value * 100.0 / (SELECT SUM(TOTAL_VALUE_INR) FROM shipments) as pct_share
    FROM HSN_Stats
)
SELECT 
    CASE WHEN rnk <= 25 THEN "HS_CODE" ELSE 'OTHERS' END as hsn_group,
    COUNT(DISTINCT "HS_CODE") as count_codes,
    SUM(hsn_total_value) as total_value,
    SUM(pct_share) as total_share_pct
FROM Ranked_HSN
GROUP BY 1
ORDER BY total_value DESC;