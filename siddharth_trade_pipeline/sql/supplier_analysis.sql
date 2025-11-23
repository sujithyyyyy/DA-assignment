-- Active vs Churned Supplier Logic (SQLite Compatible)

SELECT 
    "SUPPLIER_NAME",
    -- Max Year Check
    MAX(YEAR) as last_active_year,
    
    -- Status Determination
    CASE 
        WHEN MAX(YEAR) = 2025 THEN 'Active'
        WHEN MAX(YEAR) < 2025 THEN 'Churned'
        ELSE 'Unknown'
    END as status,
    
    -- Aggregated Metrics
    COUNT(*) as shipment_count,
    SUM(GRAND_TOTAL_INR) as total_spend
FROM shipments
GROUP BY "SUPPLIER_NAME"
ORDER BY total_spend DESC;