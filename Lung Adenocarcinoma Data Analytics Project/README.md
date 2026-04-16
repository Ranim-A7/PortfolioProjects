# Lung Adenocarcinoma Survival Analytics

This project analyzes clinical and gene expression data from The Cancer Genome Atlas (TCGA) to identify factors associated with 5-year survival in lung adenocarcinoma (LUAD) patients.

## 📊 Dashboard Preview

![Dashboard](dashboard/dashboard_screenshot.png)

## 🎯 Objective

To evaluate how clinical factors (age, stage) and gene expression biomarkers influence survival outcomes in LUAD patients.

## 📁 Project Structure

- `data/` — cleaned dataset  
- `notebooks/` — exploratory data analysis and visualization  
- `sql/` — cohort analysis queries  
- `dashboard/` — Tableau dashboard  

## ⚙️ Tools Used

- Python (pandas, matplotlib)
- SQL (PostgreSQL)
- Tableau (dashboard visualization)

## 📈 Key Insights

- Advanced tumor stage (Stage III/IV) is strongly associated with decreased survival  
- Older patients (65+) show lower survival rates  
- High MKI67 expression is linked to poorer outcomes  
- Gene expression patterns suggest pathway-level interactions  

## 🧠 Project Relevance

This project simulates real-world clinical analytics workflows used in precision medicine, demonstrating how data-driven insights can support patient risk stratification and treatment decision-making.
