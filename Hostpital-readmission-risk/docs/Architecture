# Architecture Overview

## Data Source
- UCI Diabetes 130-US Hospitals dataset
- Batch CSV ingestion

## Pipeline Layers
1. Raw layer: immutable ingestion
2. Staging layer: type casting & normalization
3. Analytics layer: star schema (fact + dimensions)

## Consumers
- BI dashboards
- ML feature pipelines

## Orchestration
- Apache Airflow (batch, daily)

## Data Quality Guarantees
- Row count consistency
- Valid categorical values
- Non-null business keys
