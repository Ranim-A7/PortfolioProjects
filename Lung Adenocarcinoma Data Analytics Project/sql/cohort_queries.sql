SELECT survival_5yr, COUNT(*)
FROM luad_analytics
GROUP BY survival_5yr;

-- Survival by Stage
SELECT
    stage,
    COUNT(*) AS patients,
    ROUND(AVG(survival_5yr)::numeric *100,2) AS survival_rate
FROM luad_analytics
GROUP BY stage
ORDER BY stage;

-- Age Cohort Analysis
SELECT
    CASE
        WHEN age < 50 THEN '<50'
        WHEN age BETWEEN 50 AND 65 THEN '50-65'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS patients,
    ROUND(AVG(survival_5yr)::numeric *100,2) AS survival_rate
FROM luad_analytics
GROUP BY age_group
ORDER BY age_group;

-- Gene Expression Survival Comparison
SELECT
    survival_5yr,
    AVG(EGFR) AS avg_EGFR_expression
FROM luad_analytics
GROUP BY survival_5yr;
