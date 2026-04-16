-- COHORT DISTRIBUTION ANALYSIS
-- Patient Count
SELECT COUNT(*) AS total_patients
FROM luad_analytics;

-- Survival Distribution: The survival balance in the cohort
SELECT
    survival_5yr,
    COUNT(*) AS patient_count
FROM luad_analytics
GROUP BY survival_5yr;

-- Stage Distributiuon: Where most LUAD diagnoses occur
SELECT
    stage,
    COUNT(*) AS patients
FROM luad_analytics
GROUP BY stage
ORDER BY patients DESC;

-- Gender Distribution
SELECT
    gender,
    COUNT(*) AS patients
FROM luad_analytics
GROUP BY gender;

-- Average Age by Survival: Those who survive more than 5 years were slightly younger on average
SELECT
    survival_5yr,
    ROUND(AVG(age)::numeric,2) AS avg_age
FROM luad_analytics
GROUP BY survival_5yr;

--SURVIVAL COHORT ANALYSIS
-- Survival Rate by Stage
SELECT
    stage,
    COUNT(*) AS patients,
    ROUND(AVG(survival_5yr)::numeric * 100,2) AS survival_rate
FROM luad_analytics
GROUP BY stage
ORDER BY stage;

-- Age Group Risk
SELECT
    CASE
        WHEN age < 50 THEN '<50'
        WHEN age BETWEEN 50 AND 65 THEN '50-65'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS patients,
    ROUND(AVG(survival_5yr)::numeric * 100,2) AS survival_rate
FROM luad_analytics
GROUP BY age_group
ORDER BY age_group;

-- Cross tab for Stage and Survival: shows how mortality is distribiuted across stages
SELECT
    stage,
    survival_5yr,
    COUNT(*) AS patients
FROM luad_analytics
GROUP BY stage, survival_5yr
ORDER BY stage;

--BIOMARKER ANALYSIS: evaluate whether gene expression relates to outcomes
--EGFR Expression By survival
SELECT
    survival_5yr,
    ROUND(AVG(EGFR)::numeric,3) AS avg_EGFR_expression
FROM luad_analytics
GROUP BY survival_5yr;

-- KRAS Expression by Survival
SELECT
    survival_5yr,
    ROUND(AVG(KRAS)::numeric,3) AS avg_KRAS_expression
FROM luad_analytics
GROUP BY survival_5yr;

-- Average Expression for Top Biomarkers: Help to identify highly expressed pathways   
SELECT
    ROUND(AVG(EGFR)::numeric,3) AS EGFR,
    ROUND(AVG(KRAS)::numeric,3) AS KRAS,
    ROUND(AVG(TP53)::numeric,3) AS TP53,
    ROUND(AVG(MKI67)::numeric,3) AS MKI67
FROM luad_analytics;

-- HIGH VS LOW BIOMARKER RISK: Simulating biomarker stratification
-- High vs Low EGFR Groups
SELECT
    CASE
        WHEN EGFR > (SELECT AVG(EGFR) FROM luad_analytics)
        THEN 'High EGFR'
        ELSE 'Low EGFR'
    END AS EGFR_group,
    COUNT(*) AS patients,
    ROUND(AVG(survival_5yr)::numeric * 100,2) AS survival_rate
FROM luad_analytics
GROUP BY EGFR_group;

--High vs Low MKI67 (proliferation marker)
SELECT
    CASE
        WHEN MKI67 > (SELECT AVG(MKI67) FROM luad_analytics)
        THEN 'High proliferation'
        ELSE 'Low proliferation'
    END AS proliferation_group,
    COUNT(*) AS patients,
    ROUND(AVG(survival_5yr)::numeric * 100,2) AS survival_rate
FROM luad_analytics
GROUP BY proliferation_group;

-- Combined Risk Profile
SELECT
    stage,
    CASE
        WHEN age > 65 THEN 'Older'
        ELSE 'Younger'
    END AS age_group,
    ROUND(AVG(survival_5yr)::numeric * 100,2) AS survival_rate
FROM luad_analytics
GROUP BY stage, age_group
ORDER BY stage;

-- Top 10 Youngest patients
SELECT
    patient_id,
    age,
    stage,
    survival_5yr
FROM luad_analytics
ORDER BY age ASC
LIMIT 10;

