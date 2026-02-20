"""
create_pbit_template.py
=======================
Generates Digital_Payment_Analysis.pbit — a fully populated Power BI
Template with 6 pages, 40+ visuals, 38 DAX measures and a star-schema
data model that auto-loads from powerbi_data\ CSVs.

Usage:
    python create_pbit_template.py
Output:
    Digital_Payment_Analysis.pbit  (~50 KB)
"""

import zipfile, json, os

OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "Digital_Payment_Analysis.pbit")

# ── Table aliases ──────────────────────────────────────────────
F  = "f"    # fact_transactions
D  = "d"    # dim_date
U  = "u"    # dim_users
P  = "p"    # dim_payment_method
C  = "c"    # dim_category
PL = "pl"   # dim_platform

ENTITIES = {
    F:  "fact_transactions",
    D:  "dim_date",
    U:  "dim_users",
    P:  "dim_payment_method",
    C:  "dim_category",
    PL: "dim_platform",
}

# ══════════════════════════════════════════════════════════════
# M EXPRESSIONS (Power Query) — CSV loaders
# ══════════════════════════════════════════════════════════════
T  = "type text";    I  = "Int64.Type"
D_ = "type number";  DT = "type datetime";  B = "type logical"

TABLES = {
"fact_transactions": {
    "file": "fact_transactions.csv",
    "cols": [
        ("transaction_id",T),("user_id",T),("date_key",I),
        ("transaction_datetime",DT),("hour",I),("time_bucket",T),
        ("payment_method",T),("category",T),("merchant",T),
        ("platform",T),("device_type",T),("city",T),
        ("amount",D_),("amount_bucket",T),("net_amount",D_),
        ("cashback_earned",D_),("discount_applied",D_),
        ("total_savings",D_),("savings_pct",D_),
        ("status",T),("is_success",I),("is_failed",I),("is_pending",I),
        ("failure_reason",T),("processing_time_sec",D_),
        ("processing_speed",T),("is_flagged",B),("is_flagged_int",I),
        ("fraud_reason",T),("is_refunded",B),("is_refunded_int",I),
        ("refund_amount",D_),
    ],
},
"dim_date": {
    "file": "dim_date.csv",
    "cols": [
        ("date_key",I),("date",DT),("year",I),("month",I),
        ("month_name",T),("month_year",T),("quarter",I),
        ("quarter_label",T),("day",I),("day_of_week",I),
        ("day_name",T),("week_number",I),("is_weekend",I),
        ("is_month_start",I),("is_month_end",I),("is_festival_season",I),
    ],
},
"dim_users": {
    "file": "dim_users.csv",
    "cols": [
        ("user_id",T),("age_group",T),("gender",T),
        ("account_tenure",T),("customer_tier",T),
        ("spending_persona",T),("preferred_method",T),
        ("user_home_city",T),("user_total_txns",I),
        ("user_total_spend",D_),("user_avg_txn_amount",D_),
        ("user_failure_rate_pct",D_),("user_spending_tier",T),
    ],
},
"dim_payment_method": {
    "file": "dim_payment_method.csv",
    "cols": [("payment_method",T),("payment_type",T),("base_failure_rate",D_)],
},
"dim_category": {
    "file": "dim_category.csv",
    "cols": [("category",T),("category_group",T)],
},
"dim_platform": {
    "file": "dim_platform.csv",
    "cols": [("platform",T),("channel",T)],
},
}

MEASURES = [
    ("Total Transactions",      "COUNTROWS(fact_transactions)"),
    ("Successful Transactions", "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[status]=\"Success\")"),
    ("Failed Transactions",     "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[status]=\"Failed\")"),
    ("Pending Transactions",    "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[status]=\"Pending\")"),
    ("Success Rate %",          "DIVIDE([Successful Transactions],[Total Transactions],0)*100"),
    ("Failure Rate %",          "DIVIDE([Failed Transactions],[Total Transactions],0)*100"),
    ("Total Revenue",           "CALCULATE(SUM(fact_transactions[amount]),fact_transactions[status]=\"Success\")"),
    ("Avg Transaction Amount",  "CALCULATE(AVERAGE(fact_transactions[amount]),fact_transactions[status]=\"Success\")"),
    ("Total Net Revenue",       "CALCULATE(SUM(fact_transactions[net_amount]),fact_transactions[status]=\"Success\")"),
    ("Total Cashback",          "SUM(fact_transactions[cashback_earned])"),
    ("Total Discounts",         "SUM(fact_transactions[discount_applied])"),
    ("Total Savings",           "SUM(fact_transactions[total_savings])"),
    ("Lost Revenue (Failures)", "CALCULATE(SUM(fact_transactions[amount]),fact_transactions[status]=\"Failed\")"),
    ("Unique Users",            "DISTINCTCOUNT(fact_transactions[user_id])"),
    ("Avg Transactions Per User","DIVIDE([Total Transactions],[Unique Users],0)"),
    ("Avg Revenue Per User",    "DIVIDE([Total Revenue],[Unique Users],0)"),
    ("Flagged Transactions",    "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[is_flagged]=TRUE())"),
    ("Fraud Rate %",            "DIVIDE([Flagged Transactions],[Total Transactions],0)*100"),
    ("Avg Flagged Amount",      "CALCULATE(AVERAGE(fact_transactions[amount]),fact_transactions[is_flagged]=TRUE())"),
    ("Total Flagged Volume",    "CALCULATE(SUM(fact_transactions[amount]),fact_transactions[is_flagged]=TRUE())"),
    ("Total Refunds",           "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[is_refunded]=TRUE())"),
    ("Refund Rate %",           "DIVIDE([Total Refunds],[Total Transactions],0)*100"),
    ("Total Refund Value",      "SUM(fact_transactions[refund_amount])"),
    ("Avg Refund Amount",       "CALCULATE(AVERAGE(fact_transactions[refund_amount]),fact_transactions[is_refunded]=TRUE())"),
    ("Avg Processing Time (sec)","CALCULATE(AVERAGE(fact_transactions[processing_time_sec]),fact_transactions[status]=\"Success\")"),
    ("Revenue PM",              "CALCULATE([Total Revenue],DATEADD(dim_date[date],-1,MONTH))"),
    ("Revenue MoM Growth %",    "VAR _c=[Total Revenue] VAR _p=[Revenue PM] RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Transactions PM",         "CALCULATE([Total Transactions],DATEADD(dim_date[date],-1,MONTH))"),
    ("Transactions MoM Growth %","VAR _c=[Total Transactions] VAR _p=[Transactions PM] RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Revenue PY",              "CALCULATE([Total Revenue],DATEADD(dim_date[date],-1,YEAR))"),
    ("Revenue YoY Growth %",    "VAR _c=[Total Revenue] VAR _p=[Revenue PY] RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Revenue YTD",             "TOTALYTD([Total Revenue],dim_date[date])"),
    ("Transactions YTD",        "TOTALYTD([Total Transactions],dim_date[date])"),
    ("Revenue MTD",             "TOTALMTD([Total Revenue],dim_date[date])"),
    ("Cumulative Revenue",      "CALCULATE([Total Revenue],FILTER(ALL(dim_date[date]),dim_date[date]<=MAX(dim_date[date])))"),
    ("Revenue in Crores",       "FORMAT(DIVIDE([Total Revenue],10000000),\"0.00\") & \" Cr\""),
    ("Revenue in Lakhs",        "FORMAT(DIVIDE([Total Revenue],100000),\"0.00\") & \" L\""),
    ("Success Rate Color",      "SWITCH(TRUE(),[Success Rate %]>=95,\"#10b981\",[Success Rate %]>=90,\"#f59e0b\",\"#ef4444\")"),
]

RELATIONSHIPS = [
    ("fact_transactions","date_key",       "dim_date",           "date_key"),
    ("fact_transactions","user_id",        "dim_users",          "user_id"),
    ("fact_transactions","payment_method", "dim_payment_method", "payment_method"),
    ("fact_transactions","category",       "dim_category",       "category"),
    ("fact_transactions","platform",       "dim_platform",       "platform"),
]

# ══════════════════════════════════════════════════════════════
# DATA MODEL SCHEMA
# ══════════════════════════════════════════════════════════════
def build_m_expr(filename, col_types):
    lines = ",\n            ".join(f'{{"{c}", {t}}}' for c, t in col_types)
    return (
        f'let\n'
        f'    Source  = Csv.Document(File.Contents(FolderPath & "\\\\{filename}"),\n'
        f'                [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),\n'
        f'    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        f'    Typed   = Table.TransformColumnTypes(Headers, {{\n'
        f'            {lines}\n'
        f'        }})\n'
        f'in Typed'
    )

def _pbi_type(m_type):
    return {"type text":"string","Int64.Type":"int64","type number":"double",
            "type datetime":"dateTime","type logical":"boolean"}[m_type]

def build_data_model_schema():
    tables = []
    for tname, info in TABLES.items():
        cols = [{"name": c, "dataType": _pbi_type(t), "sourceColumn": c,
                 "annotations": [{"name":"SummarizationSetBy","value":"Automatic"}]}
                for c, t in info["cols"]]
        measures = []
        if tname == "fact_transactions":
            for m_name, m_dax in MEASURES:
                fmt = ("#,##0.00" if "%" in m_name else
                       "#,##0"   if any(k in m_name for k in ["Transaction","Users","Refunds","Flagged"]) else
                       "#,##0.00")
                measures.append({"name": m_name, "expression": m_dax, "formatString": fmt,
                                  "annotations": [{"name":"PBI_FormatHint","value":'{"isGeneralNumber":true}'}]})
        tbl = {"name": tname, "columns": cols,
               "partitions": [{"name": tname, "mode": "import",
                                "source": {"type":"m","expression": build_m_expr(info["file"], info["cols"])}}],
               "annotations": [{"name":"PBI_ResultType","value":"Table"}]}
        if measures:
            tbl["measures"] = measures
        tables.append(tbl)

    rels = [{"name": f"rel_{i}", "fromTable": ft, "fromColumn": fc,
             "toTable": tt, "toColumn": tc, "crossFilteringBehavior": "oneDirection"}
            for i, (ft, fc, tt, tc) in enumerate(RELATIONSHIPS)]

    schema = {
        "name": "ReportSection",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-IN",
            "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-IN",
            "tables": tables,
            "relationships": rels,
            "expressions": [{
                "name": "FolderPath",
                "kind": "m",
                "expression": [
                    '"C:\\\\Users\\\\YourName\\\\path\\\\to\\\\powerbi_data"',
                    "// Update this to your powerbi_data\\ folder path"
                ],
                "annotations": [
                    {"name":"PBI_NavigationStepName","value":"Navigation"},
                    {"name":"PBI_ParameterQueryName","value":"FolderPath"},
                ],
            }],
            "annotations": [
                {"name":"PBIDesktopVersion","value":"2.136.1202.0"},
                {"name":"PBI_QueryOrder","value": json.dumps(list(TABLES.keys()))},
            ],
        },
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════════════════════
# VISUAL BUILDER
# ══════════════════════════════════════════════════════════════
_VID = [0]

def _vid():
    _VID[0] += 1
    return f"v{_VID[0]:04d}"

def _from_clause(aliases):
    seen = {}
    result = []
    for a in aliases:
        if a not in seen:
            seen[a] = True
            result.append({"Name": a, "Entity": ENTITIES[a], "Type": 0})
    return result

def _ms(alias, prop):   # measure select
    return {"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop},
            "Name": f"{alias}.{prop}"}

def _cs(alias, prop):   # column select
    return {"Column":  {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop},
            "Name": f"{alias}.{prop}"}

def _qr(alias, prop):   # query ref string
    return f"{alias}.{prop}"

def _visual(vtype, x, y, w, h, projections, from_aliases, selects, title=""):
    name = _vid()
    vc_obj = {}
    if title:
        vc_obj["title"] = [{"properties": {
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
            "show": {"expr": {"Literal": {"Value": "true"}}}
        }}]

    proto_q = {"Version": 2, "From": _from_clause(from_aliases), "Select": selects}

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0,
                                            "width": w, "height": h, "tabOrder": _VID[0]}}],
        "singleVisual": {
            "visualType": vtype,
            "projections": projections,
            "prototypeQuery": proto_q,
            "vcObjects": vc_obj,
        },
    }

    sem_q = {"Commands": [{"SemanticQueryDataShapeCommand": {
        "Query": proto_q,
        "Binding": {
            "Primary": {"Groupings": [{"Projections": list(range(len(selects)))}]},
            "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 1000}}},
            "Version": 1,
        }
    }}]}

    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": json.dumps(config, ensure_ascii=False),
            "filters": "[]",
            "query":   json.dumps(sem_q, ensure_ascii=False),
            "dataTransforms": "{}",
            "howCreated": 1}

# ── Convenience wrappers ───────────────────────────────────────

def kpi_card(x, y, w, h, alias, measure, title=""):
    return _visual("card", x, y, w, h,
                   {"Values": [{"queryRef": _qr(alias, measure), "active": False}]},
                   [alias], [_ms(alias, measure)], title)

def bar(x, y, w, h, cat_a, cat_c, val_a, val_m, title="", horizontal=True):
    vtype = "clusteredBarChart" if horizontal else "clusteredColumnChart"
    return _visual(vtype, x, y, w, h,
                   {"Category": [{"queryRef": _qr(cat_a, cat_c), "active": False}],
                    "Y":        [{"queryRef": _qr(val_a, val_m), "active": False}]},
                   [cat_a, val_a], [_cs(cat_a, cat_c), _ms(val_a, val_m)], title)

def col(x, y, w, h, cat_a, cat_c, val_a, val_m, title=""):
    return bar(x, y, w, h, cat_a, cat_c, val_a, val_m, title, horizontal=False)

def multi_bar(x, y, w, h, cat_a, cat_c, measures, title="", horizontal=True):
    """Multiple grouped bars — measures = [(alias, measure_name), ...]"""
    vtype = "clusteredBarChart" if horizontal else "clusteredColumnChart"
    aliases = [cat_a] + [a for a, _ in measures]
    selects = [_cs(cat_a, cat_c)] + [_ms(a, m) for a, m in measures]
    proj = {"Category": [{"queryRef": _qr(cat_a, cat_c), "active": False}],
            "Y":        [{"queryRef": _qr(a, m), "active": False} for a, m in measures]}
    return _visual(vtype, x, y, w, h, proj, aliases, selects, title)

def donut(x, y, w, h, cat_a, cat_c, val_a, val_m, title=""):
    return _visual("donutChart", x, y, w, h,
                   {"Category": [{"queryRef": _qr(cat_a, cat_c), "active": False}],
                    "Y":        [{"queryRef": _qr(val_a, val_m), "active": False}]},
                   [cat_a, val_a], [_cs(cat_a, cat_c), _ms(val_a, val_m)], title)

def combo(x, y, w, h, cat_a, cat_c, bar_a, bar_m, line_a, line_m, title=""):
    aliases = [cat_a, bar_a, line_a]
    selects = [_cs(cat_a, cat_c), _ms(bar_a, bar_m), _ms(line_a, line_m)]
    proj = {"Category": [{"queryRef": _qr(cat_a, cat_c), "active": False}],
            "Y":        [{"queryRef": _qr(bar_a, bar_m),  "active": False}],
            "Y2":       [{"queryRef": _qr(line_a, line_m),"active": False}]}
    return _visual("lineClusteredColumnComboChart", x, y, w, h, proj, aliases, selects, title)

def matrix_vis(x, y, w, h, row_a, row_c, col_a, col_c, val_a, val_m, title=""):
    aliases = [row_a, col_a, val_a]
    selects = [_cs(row_a, row_c), _cs(col_a, col_c), _ms(val_a, val_m)]
    proj = {"Rows":    [{"queryRef": _qr(row_a, row_c), "active": False}],
            "Columns": [{"queryRef": _qr(col_a, col_c), "active": False}],
            "Values":  [{"queryRef": _qr(val_a, val_m), "active": False}]}
    return _visual("matrix", x, y, w, h, proj, aliases, selects, title)

def slicer_vis(x, y, w, h, alias, field, title=""):
    return _visual("slicer", x, y, w, h,
                   {"Values": [{"queryRef": _qr(alias, field), "active": False}]},
                   [alias], [_cs(alias, field)], title)

# ══════════════════════════════════════════════════════════════
# PAGE DEFINITIONS
# ══════════════════════════════════════════════════════════════

def page_overview():
    """Page 1 — Executive Overview"""
    vcs = []

    # ── KPI Row (6 cards) ──────────────────────────────────
    KPI_W, KPI_H, KPI_GAP, KPI_Y = 184, 95, 12, 15
    kpis = [
        (F, "Total Transactions",    "Total Transactions"),
        (F, "Total Revenue",         "Total Revenue"),
        (F, "Success Rate %",        "Success Rate %"),
        (F, "Unique Users",          "Active Users"),
        (F, "Fraud Rate %",          "Fraud Rate"),
        (F, "Total Cashback",        "Total Cashback"),
    ]
    for i, (a, m, t) in enumerate(kpis):
        vcs.append(kpi_card(15 + i * (KPI_W + KPI_GAP), KPI_Y, KPI_W, KPI_H, a, m, t))

    # ── Row 2: Monthly Trend + Payment Donut ──────────────
    vcs.append(combo(15, 128, 820, 265, D, "month_year",
                     F, "Total Transactions", F, "Success Rate %",
                     "Monthly Transaction Trend (2024-2025)"))
    vcs.append(donut(853, 128, 410, 265, F, "payment_method",
                     F, "Total Transactions", "Payment Method Split"))

    # ── Row 3: Category Revenue + City Distribution ───────
    vcs.append(bar(15, 410, 615, 285, F, "category",
                   F, "Total Revenue", "Revenue by Category (INR)", horizontal=True))
    vcs.append(bar(648, 410, 615, 285, F, "city",
                   F, "Total Transactions", "Transactions by City", horizontal=True))

    return vcs


def page_transactions():
    """Page 2 — Transaction Analysis"""
    vcs = []

    # ── Heatmap: Day x Hour (use matrix) ──────────────────
    vcs.append(matrix_vis(15, 15, 1248, 255,
                          F, "day_name", F, "hour", F, "Total Transactions",
                          "Transaction Heatmap: Day of Week vs Hour of Day"))

    # ── Time Bucket Combo ──────────────────────────────────
    vcs.append(combo(15, 288, 615, 230,
                     F, "time_bucket",
                     F, "Total Transactions", F, "Success Rate %",
                     "Transactions by Time of Day"))

    # ── Day of Week Column Chart ───────────────────────────
    vcs.append(combo(648, 288, 615, 230,
                     F, "day_name",
                     F, "Total Transactions", F, "Success Rate %",
                     "Transactions by Day of Week"))

    # ── Success Rate by Payment Method ───────────────────
    vcs.append(col(15, 535, 820, 165,
                   F, "payment_method", F, "Success Rate %",
                   "Success Rate % by Payment Method"))

    # ── Avg Transaction by Amount Bucket ─────────────────
    vcs.append(col(853, 535, 410, 165,
                   F, "amount_bucket", F, "Total Transactions",
                   "Transactions by Amount Tier"))

    return vcs


def page_failures():
    """Page 3 — Failure Analysis"""
    vcs = []

    # ── KPI Row (4 cards) ─────────────────────────────────
    kpis = [
        (F, "Failed Transactions",     "Failed Transactions"),
        (F, "Failure Rate %",          "Failure Rate %"),
        (F, "Lost Revenue (Failures)", "Lost Revenue"),
        (F, "Avg Transaction Amount",  "Avg Failed Amount"),
    ]
    for i, (a, m, t) in enumerate(kpis):
        vcs.append(kpi_card(15 + i * 315, 15, 303, 95, a, m, t))

    # ── Failure Reasons Horizontal Bar ────────────────────
    vcs.append(bar(15, 128, 615, 275,
                   F, "failure_reason", F, "Failed Transactions",
                   "Top Failure Reasons", horizontal=True))

    # ── Lost Revenue by Method ────────────────────────────
    vcs.append(bar(648, 128, 615, 275,
                   F, "payment_method", F, "Lost Revenue (Failures)",
                   "Lost Revenue by Payment Method", horizontal=True))

    # ── Hourly Failure Rate Combo ─────────────────────────
    vcs.append(combo(15, 420, 820, 270,
                     F, "hour",
                     F, "Total Transactions", F, "Failure Rate %",
                     "Failure Rate by Hour of Day"))

    # ── Method x Reason Matrix ────────────────────────────
    vcs.append(matrix_vis(853, 420, 410, 270,
                          F, "payment_method", F, "failure_reason",
                          F, "Failed Transactions",
                          "Failures: Method vs Reason"))

    return vcs


def page_users():
    """Page 4 — User Analytics"""
    vcs = []

    # ── Age Group Combo ───────────────────────────────────
    vcs.append(combo(15, 15, 615, 250,
                     U, "age_group",
                     F, "Total Transactions", F, "Avg Transaction Amount",
                     "Age Group: Transactions & Avg Amount"))

    # ── Customer Tier Column ──────────────────────────────
    vcs.append(col(648, 15, 615, 250,
                   U, "customer_tier", F, "Total Transactions",
                   "Customer Tier Distribution"))

    # ── Spending Persona Horizontal Bar ───────────────────
    vcs.append(bar(15, 283, 400, 205,
                   U, "spending_persona", F, "Avg Transaction Amount",
                   "Avg Amount by Spending Persona", horizontal=True))

    # ── Gender Donut ──────────────────────────────────────
    vcs.append(donut(433, 283, 400, 205,
                     U, "gender", F, "Total Transactions",
                     "Gender Distribution"))

    # ── Account Tenure Bar ───────────────────────────────
    vcs.append(bar(851, 283, 412, 205,
                   U, "account_tenure", F, "Total Transactions",
                   "Account Tenure Distribution", horizontal=True))

    # ── Monthly Active Users Combo ────────────────────────
    vcs.append(combo(15, 506, 1248, 190,
                     D, "month_year",
                     F, "Unique Users", F, "Avg Transactions Per User",
                     "Monthly Active Users & Engagement (2024-2025)"))

    return vcs


def page_fraud():
    """Page 5 — Fraud & Refunds"""
    vcs = []

    # ── Fraud KPI Row ─────────────────────────────────────
    fraud_kpis = [
        (F, "Flagged Transactions", "Flagged Transactions"),
        (F, "Fraud Rate %",         "Fraud Rate %"),
        (F, "Avg Flagged Amount",   "Avg Flagged Amount"),
        (F, "Total Flagged Volume", "Total Flagged Volume"),
    ]
    for i, (a, m, t) in enumerate(fraud_kpis):
        vcs.append(kpi_card(15 + i * 315, 15, 303, 95, a, m, t))

    # ── Fraud Reasons Bar ─────────────────────────────────
    vcs.append(bar(15, 128, 615, 240,
                   F, "fraud_reason", F, "Flagged Transactions",
                   "Fraud Flag Reasons", horizontal=True))

    # ── Flagged Amount by Category ────────────────────────
    vcs.append(bar(648, 128, 615, 240,
                   F, "category", F, "Total Flagged Volume",
                   "Flagged Transaction Volume by Category", horizontal=True))

    # ── Refund KPI Row ────────────────────────────────────
    refund_kpis = [
        (F, "Total Refunds",      "Total Refunds"),
        (F, "Refund Rate %",      "Refund Rate %"),
        (F, "Total Refund Value", "Total Refund Value"),
        (F, "Avg Refund Amount",  "Avg Refund Amount"),
    ]
    for i, (a, m, t) in enumerate(refund_kpis):
        vcs.append(kpi_card(15 + i * 315, 386, 303, 95, a, m, t))

    # ── Refund by Category Bar ────────────────────────────
    vcs.append(bar(15, 499, 615, 195,
                   F, "category", F, "Total Refund Value",
                   "Refund Value by Category", horizontal=True))

    # ── Refund by Payment Method Bar ─────────────────────
    vcs.append(bar(648, 499, 615, 195,
                   F, "payment_method", F, "Total Refund Value",
                   "Refund Value by Payment Method", horizontal=True))

    return vcs


def page_platform():
    """Page 6 — Platform & Device"""
    vcs = []

    # ── Platform Donut ────────────────────────────────────
    vcs.append(donut(15, 15, 390, 290,
                     F, "platform", F, "Total Transactions",
                     "Platform Distribution"))

    # ── Device Type Bar ───────────────────────────────────
    vcs.append(bar(423, 15, 430, 290,
                   F, "device_type", F, "Total Transactions",
                   "Transactions by Device Type", horizontal=True))

    # ── Platform Success Rate Column ──────────────────────
    vcs.append(col(871, 15, 392, 290,
                   F, "platform", F, "Success Rate %",
                   "Success Rate by Platform"))

    # ── Channel Column (from dim_platform) ────────────────
    vcs.append(col(15, 323, 390, 235,
                   PL, "channel", F, "Total Transactions",
                   "Transactions by Channel"))

    # ── Cashback by Payment Method ────────────────────────
    vcs.append(bar(423, 323, 430, 235,
                   F, "payment_method", F, "Total Cashback",
                   "Total Cashback by Payment Method", horizontal=True))

    # ── Discounts by Category ─────────────────────────────
    vcs.append(bar(871, 323, 392, 235,
                   F, "category", F, "Total Discounts",
                   "Total Discounts by Category", horizontal=True))

    # ── Processing Speed Distribution (full width) ────────
    vcs.append(col(15, 576, 820, 124,
                   F, "processing_speed", F, "Total Transactions",
                   "Transactions by Processing Speed"))

    # ── Avg Processing Time KPI ───────────────────────────
    vcs.append(kpi_card(853, 576, 410, 124,
                        F, "Avg Processing Time (sec)",
                        "Avg Processing Time (sec)"))

    return vcs


# ══════════════════════════════════════════════════════════════
# REPORT LAYOUT
# ══════════════════════════════════════════════════════════════
PAGES = [
    ("Executive Overview",   page_overview),
    ("Transaction Analysis", page_transactions),
    ("Failure Analysis",     page_failures),
    ("User Analytics",       page_users),
    ("Fraud & Refunds",      page_fraud),
    ("Platform & Device",    page_platform),
]

PAGE_CONFIG = json.dumps({
    "version": "5.47",
    "defaultDrillFilterOtherVisuals": True,
    "objects": {"section": [{"properties": {
        "height": {"value": {"type": "double", "value": 720}},
        "width":  {"value": {"type": "double", "value": 1280}},
    }}]},
})

def build_report_layout():
    sections = []
    for i, (page_name, page_fn) in enumerate(PAGES):
        sections.append({
            "id":               i,
            "name":             f"ReportSection{i}",
            "displayName":      page_name,
            "filters":          "[]",
            "ordinal":          i,
            "visualContainers": page_fn(),
            "config":           PAGE_CONFIG,
            "layoutOptimization": 0,
        })

    layout = {
        "id":      0,
        "sections": sections,
        "config":  json.dumps({
            "version": "5.47",
            "themeCollection": {
                "baseTheme": {"name": "CY24SU07", "version": "5.47", "type": 2}
            },
        }),
        "layoutOptimization": 0,
        "pods":              None,
        "resourcePackages":  [],
    }
    return json.dumps(layout, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════
# STATIC COMPONENTS
# ══════════════════════════════════════════════════════════════
CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Override PartName="/DataModelSchema" ContentType="application/json"/>
  <Override PartName="/DiagramState"    ContentType="application/json"/>
  <Override PartName="/Report/Layout"   ContentType="application/json"/>
  <Override PartName="/Settings"        ContentType="application/json"/>
  <Override PartName="/Metadata"        ContentType="application/json"/>
  <Override PartName="/Version"         ContentType="application/octet-stream"/>
</Types>"""

METADATA     = json.dumps({"version": "4.0", "createdFrom": "PublishedVersion"})
SETTINGS     = json.dumps({"version": "1.0", "useStylableVisuals": True,
                            "isPaidArtifact": False})
DIAGRAM_STATE = json.dumps({"version": "0", "positions": []})
VERSION      = "2.0"


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════
def create_pbit():
    print("Building DataModelSchema ...")
    dms = build_data_model_schema()

    print("Building Report/Layout (6 pages, 40+ visuals) ...")
    layout = build_report_layout()

    total_visuals = sum(len(page_fn()) for _, page_fn in PAGES)
    _VID[0] = 0  # reset so rebuild is idempotent

    print(f"Writing {OUT_FILE} ...")
    with zipfile.ZipFile(OUT_FILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        def add(name, content):
            zf.writestr(zipfile.ZipInfo(name),
                        content.encode("utf-8") if isinstance(content, str) else content)
        add("[Content_Types].xml", CONTENT_TYPES)
        add("Version",             VERSION)
        add("Metadata",            METADATA)
        add("Settings",            SETTINGS)
        add("DiagramState",        DIAGRAM_STATE)
        add("DataModelSchema",     dms)
        add("SecurityBindings",    "")
        add("Report/Layout",       layout)

    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f"\nDone!  {OUT_FILE}  ({size_kb:.0f} KB)")
    print(f"Pages: {len(PAGES)}   |   Visuals: counted in layout")
    print("\nNext steps:")
    print("  1. Install Power BI Desktop (microsoft.com/powerbi - free)")
    print("  2. File > Open > Digital_Payment_Analysis.pbit")
    print("  3. Set FolderPath = full path to your powerbi_data\\ folder")
    print("  4. Click Load  -  all tables, measures and visuals load")
    print("  5. File > Save As .pbix when done")


if __name__ == "__main__":
    create_pbit()
