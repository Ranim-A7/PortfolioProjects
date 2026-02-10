# Healthcare Readmission Analytics Pipeline

## Overview
This project implements a batch data pipeline that ingests raw hospital
encounter data and transforms it into analytics-ready fact and dimension
tables with data quality validation.

## Data Flow
Raw CSV → Raw Tables → Staging → Analytics Marts

## Technologies
- PostgreSQL
- Python
- SQL
- Apache Airflow

## Data Layers
- raw_diabetic_encounters (immutable)
- stg_diabetic_encounters (cleaned)
- fact_readmissions
- dim_patient
- dim_admission
- dim_diagnosis

## Quality Checks
- Row count validation
- Null thresholds
- Valid domain values
