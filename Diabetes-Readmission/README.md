# Hospital Readmission Risk Prediction

## Problem Statement
Hospital readmissions within 30 days are costly and often preventable.
This project builds a predictive model to identify patients at high risk
of readmission using historical electronic health record (EHR) data.

## Dataset
- Source: UCI Machine Learning Repository
- Size: ~130,000 hospital encounters
- Domain: Diabetes-related admissions across U.S. hospitals

## Objective
Predict whether a patient will be readmitted within 30 days of discharge.

## Target Variable
Binary indicator:
- 1 = Readmitted within 30 days
- 0 = No readmission or readmitted after 30 days

## Evaluation Metrics
- ROC-AUC
- Precision-Recall (class imbalance)

## Tools & Technologies
- SQL (PostgreSQL / MySQL)
- Python (pandas, scikit-learn, XGBoost)
- SHAP for model interpretability
- Streamlit/Dash for visualization
