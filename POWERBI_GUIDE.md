# Power BI Dashboard — Setup Guide
## Digital Payment Transaction Analysis

---

## Step 1 — Generate the data tables

Run this script once to create the star-schema CSVs:

```bash
python prepare_powerbi_data.py
```

This produces a `powerbi_data/` folder with 6 files:

| File | Rows | Purpose |
|------|------|---------|
| `fact_transactions.csv` | 60,000 | Main fact table |
| `dim_date.csv` | 731 | Date dimension |
| `dim_users.csv` | 500 | User demographics |
| `dim_payment_method.csv` | 5 | Payment method lookup |
| `dim_category.csv` | 10 | Category lookup |
| `dim_platform.csv` | 4 | Platform/channel lookup |

---

## Step 2 — Import into Power BI Desktop

1. Open **Power BI Desktop**
2. **Home → Get Data → Text/CSV**
3. Import all 6 files from `powerbi_data/`
4. For each file click **Load** (no transformations needed)

---

## Step 3 — Build the Data Model (Relationships)

Go to **Model view** and create these relationships (all Many-to-One):

| From (fact) | → | To (dimension) | Type |
|---|---|---|---|
| `fact_transactions[date_key]` | → | `dim_date[date_key]` | Many → One |
| `fact_transactions[user_id]` | → | `dim_users[user_id]` | Many → One |
| `fact_transactions[payment_method]` | → | `dim_payment_method[payment_method]` | Many → One |
| `fact_transactions[category]` | → | `dim_category[category]` | Many → One |
| `fact_transactions[platform]` | → | `dim_platform[platform]` | Many → One |

**Mark dim_date as a Date Table:**
- Right-click `dim_date` → **Mark as Date Table** → select `date` column

---

## Step 4 — Add DAX Measures

1. Select the `fact_transactions` table in the Fields pane
2. **Modeling → New Measure**
3. Copy-paste each measure from `powerbi_measures.dax`

Key measures to add first:
- `Total Transactions`
- `Total Revenue`
- `Success Rate %`
- `Failure Rate %`
- `Unique Users`
- `Fraud Rate %`
- `Refund Rate %`

---

## Step 5 — Build the Dashboard Pages

### Page 1 · Executive Overview
| Visual | Fields | Notes |
|--------|--------|-------|
| Card | `Total Transactions` | KPI |
| Card | `Total Revenue` | use "Revenue in Crores" measure |
| Card | `Success Rate %` | conditional format with `Success Rate Color` |
| Card | `Unique Users` | KPI |
| Card | `Fraud Rate %` | KPI |
| Card | `Total Cashback` | KPI |
| Line + Clustered Column | X: `dim_date[month_year]`, Bar: `Total Transactions`, Line: `Success Rate %` | Monthly trend |
| Donut Chart | Legend: `payment_method`, Values: `Total Transactions` | Payment mix |
| Bar Chart | Y: `category`, X: `Total Revenue` | Revenue by category |
| Bar Chart | Y: `city`, X: `Total Transactions` | City distribution |
| Date Slicer | `dim_date[date]` | Set to "Between" range |

---

### Page 2 · Transaction Analysis
| Visual | Fields | Notes |
|--------|--------|-------|
| Matrix / Heatmap | Rows: `day_name`, Cols: `hour`, Values: `Total Transactions` | Use conditional formatting on values |
| Clustered Bar | X: `time_bucket`, Y: `Total Transactions` + `Success Rate %` | Time of day |
| Clustered Column | X: `payment_method`, Y: `Success Rate %` | Colour by success level |
| Pie Chart | Legend: `is_weekend`, Values: `Total Transactions` | Weekday vs Weekend |
| Line Chart | X: `dim_date[month_year]`, Y: `Avg Transaction Amount` | Avg trend |
| Slicer | `dim_payment_method[payment_type]` | Card/Digital/Banking |

---

### Page 3 · Failure Analysis
| Visual | Fields | Notes |
|--------|--------|-------|
| Card | `Failed Transactions` | KPI |
| Card | `Failure Rate %` | KPI |
| Card | `Lost Revenue (Failures)` | KPI |
| Bar Chart (H) | Y: `failure_reason`, X: `Failed Transactions` | Top reasons |
| Bar Chart (H) | Y: `payment_method`, X: `Lost Revenue (Failures)` | By method |
| Line + Column | X: `hour`, Bar: `Total Transactions`, Line: `Failure Rate %` | Hourly pattern |
| Matrix | Rows: `payment_method`, Cols: `failure_reason`, Values: `Failed Transactions` | Cross-tab |
| Slicer | `dim_date[date]` | Date range |

---

### Page 4 · User Analytics
| Visual | Fields | Notes |
|--------|--------|-------|
| Clustered Column | X: `age_group`, Y: `Total Transactions` + `Avg Transaction Amount` | Age analysis |
| Bar Chart | X: `customer_tier`, Y: `Total Transactions` | Order: New → VIP |
| Donut Chart | Legend: `gender`, Values: `Total Transactions` | Gender split |
| Bar Chart (H) | Y: `spending_persona`, X: `Avg Transaction Amount` | Persona |
| Line + Column | X: `dim_date[month_year]`, Bar: `Unique Users`, Line: `Avg Transactions Per User` | MAU |
| Slicer | `dim_users[customer_tier]` | Tier filter |
| Slicer | `dim_users[age_group]` | Age filter |

---

### Page 5 · Fraud & Refunds
| Visual | Fields | Notes |
|--------|--------|-------|
| Card | `Flagged Transactions` | KPI |
| Card | `Fraud Rate %` | KPI |
| Card | `Total Flagged Volume` | KPI |
| Card | `Total Refunds` | KPI |
| Card | `Total Refund Value` | KPI |
| Bar Chart (H) | Y: `fraud_reason`, X: `Flagged Transactions` | Filter `is_flagged = TRUE` |
| Box Plot / Violin | `amount` split by `is_flagged` | Normal vs Flagged amounts |
| Bar Chart (H) | Y: `category`, X: `Total Refunds` | Refund by category |
| Bar Chart (H) | Y: `payment_method`, X: `Total Refund Value` | Refund by method |
| Line Chart | X: `dim_date[month_year]`, Y: `Fraud Rate %` | Fraud trend |

---

### Page 6 · Platform & Device
| Visual | Fields | Notes |
|--------|--------|-------|
| Donut Chart | Legend: `platform`, Values: `Total Transactions` | Platform split |
| Bar Chart | Y: `device_type`, X: `Total Transactions` | Device breakdown |
| Clustered Bar | X: `device_type` (Android/iOS), Y: `Success Rate %` + `Avg Transaction Amount` | Mobile compare |
| Bar Chart (H) | Y: `payment_method`, X: `Total Cashback` | Cashback by method |
| Bar Chart (H) | Y: `category`, X: `Total Discounts` | Discounts by category |
| Card | `Avg Processing Time (sec)` | KPI |
| Slicer | `dim_platform[channel]` | Mobile / Web / Physical |

---

## Recommended Theme & Colours

Set a **dark theme** in Power BI:
- **View → Themes → Browse for themes** or paste this JSON:

```json
{
  "name": "Payment Analytics Dark",
  "dataColors": ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899","#14b8a6","#06b6d4","#f97316","#a855f7"],
  "background": "#0f172a",
  "foreground": "#f1f5f9",
  "tableAccent": "#3b82f6"
}
```

---

## Tips

- Use **dim_date[date]** as the slicer field (not fact_transactions dates) so all visuals sync
- Enable **drill-through** on `payment_method` and `category` pages for detail views
- Add **tooltips** with `Avg Transaction Amount`, `Success Rate %` on all bar charts
- Use **conditional formatting** on matrices with colour scales (white → blue for volume, white → red for failures)
- Set `dim_date` as the **Mark as Date Table** to enable DATEADD / TOTALYTD measures
