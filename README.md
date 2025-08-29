# 🛒 A/B Testing with Olist E‑commerce Data

An end‑to‑end data project using the **Olist Brazilian E‑commerce dataset** to simulate an **A/B marketing experiment**.  
It demonstrates skills in **ETL (Extract‑Transform‑Load)**, **experiment design**, **statistical testing**, and **BI dashboarding** (Power BI, Tableau, Excel).

---

## 🚀 What This Project Does  
- 📥 **Ingests Olist data** (orders, payments, customers) → builds tidy revenue table  
- 🧪 **Simulates an A/B test** (assigns customers, defines test window, measures conversions + revenue)  
- 📊 **Computes KPIs**: Conversion Rate (CR), Revenue per Visitor (RPV), Confidence Intervals, z‑tests  
- 📈 **Exports CSVs** for **Power BI, Tableau, or Excel** dashboards  
- 📝 **Generates plots** and (optional) Markdown reports for stakeholders  

---

## 🧰 Tech Stack  
- **Python**: `pandas`, `numpy`  
- **Visualisation**: `matplotlib`, `seaborn`  
- **Statistics**: `statsmodels` (z‑test, Wilson CIs)  
- **BI**: Power BI Desktop / Tableau Public / Excel  
- **Version Control**: Git + GitHub for portfolio  

---

## 📁 Repository Structure  

```
ab-testing-olist/
├── README.md                    # Project overview (this file)
├── requirements.txt             # Python dependencies
├── data/
│   ├── raw/olist/               # Olist CSV datasets
│   └── processed/               # Enriched intermediate files
├── outputs/
│   ├── plots/                   # Visualisations (PNG)
│   └── bi_exports/              # CSVs for BI dashboards
└── scripts/
    ├── ingest_olist.py          # ETL: build tidy orders + revenue
    ├── build_experiment.py      # Simulate A/B campaign + outcomes
    ├── run_ab_test.py           # Stats, plots, BI exports
    └── make_report.py           # Optional Markdown summary
```

---

## ▶️ How to Run  

### 1. Create a virtual environment  

**Windows PowerShell**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
python -m venv venv
source venv/bin/activate
```

---

### 2. Install dependencies  
```bash
pip install -r requirements.txt
```

---

### 3. Ingest Olist data (build tidy orders table)  
```bash
python scripts/ingest_olist.py
```
✅ Produces `data/processed/orders_enriched.csv`  

---

### 4. Build simulated A/B experiment  
```bash
python scripts/build_experiment.py
```
✅ Produces `data/ab_data.csv` (one row per customer with group, conversion, revenue, segment)  

---

### 5. Run A/B analysis + exports  
```bash
python scripts/run_ab_test.py
```
✅ Produces:  
- `outputs/bi_exports/groups.csv` (KPI summary per group)  
- `outputs/bi_exports/daily.csv` (daily trend data)  
- `outputs/bi_exports/segments.csv` (geo breakdown)  
- `outputs/plots/cr_by_group.png` (bar + CI)  

---

### 6. Hook into BI tools  

**Power BI Desktop**  
- Import `outputs/bi_exports/*.csv`  
- Build visuals:  
  - KPI cards → Visitors, Conversions, CR, RPV  
  - Bar chart → CR by Group  
  - Line chart → Daily conversions/revenue  
  - Matrix → Segment × Group breakdown  
  - Slicers → Group, Segment, Date  

**Tableau Public**  
- Connect to CSVs (`groups.csv`, `daily.csv`, `segments.csv`)  
- Build similar sheets + dashboard  

**Excel**  
- Open CSVs directly → insert PivotTables & charts  

---

## 📊 Example Visuals  

**Conversion Rate by Group (95% CI)**  
![CR by Group](outputs/plots/cr_by_group.png)  

---

## 🎯 Why This Project Matters  

This project demonstrates:  
- **ETL** with messy e‑commerce data  
- **Experiment design**: customer‑level randomisation, conversion window  
- **Statistics**: CR, revenue lift, confidence intervals, hypothesis testing  
- **Business relevance**: conversion, ROAS, geo segmentation → common e‑commerce KPIs  
- **Communication**: outputs are BI‑ready for stakeholders  

📌 *This mirrors real workflows in marketing analytics, growth, and product data science — perfect for an internship/entry‑level portfolio.*  

---

## 🔒 Notes  
- Place Olist CSVs in `data/raw/olist/` before running scripts  
- Adjust test window in `scripts/build_experiment.py` (`TEST_START`, `TEST_END`)  
- Set random seed (`SEED`) for reproducibility  
- Use `.gitignore` for large data files  

---

## 📄 Licence  
MIT Licence – free to use and adapt.  
