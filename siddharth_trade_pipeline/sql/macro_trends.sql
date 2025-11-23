-- Query for Year-over-Year Growth (SQLite Compatible)

WITH YearlyStats AS (
    SELECT 
        YEAR,
        SUM(TOTAL_VALUE_INR) as total_value,
        SUM(DUTY_PAID_INR) as total_duty,
        SUM(GRAND_TOTAL_INR) as total_grand
    FROM shipments
    GROUP BY YEAR
)
SELECT 
    YEAR,
    total_value,
    
    -- Lag function to get previous year's value
    LAG(total_value) OVER (ORDER BY YEAR) as prev_year_value,
    
    -- Growth Calculation
    ROUND(
        (total_value - LAG(total_value) OVER (ORDER BY YEAR)) / 
        NULLIF(LAG(total_value) OVER (ORDER BY YEAR), 0) * 100
    , 2) as yoy_growth_pct
FROM YearlyStats
ORDER BY YEAR;