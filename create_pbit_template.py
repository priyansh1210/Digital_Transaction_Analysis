"""
create_pbit_template.py
=======================
Generates a Power BI Template (.pbit) file for the
Digital Payment Transaction Analysis dashboard.

When opened in Power BI Desktop:
  1. Enter the full path to your powerbi_data/ folder when prompted
  2. Click "Load" — all 6 tables import automatically
  3. All relationships and 40+ DAX measures are pre-built
  4. Add visuals on the 6 pre-named pages

Usage:
    python create_pbit_template.py
Output:
    Digital_Payment_Analysis.pbit
"""

import zipfile, json, os, struct, time

OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "Digital_Payment_Analysis.pbit")

# ══════════════════════════════════════════════════════════════
# HELPER — build M expression for a CSV table
# ══════════════════════════════════════════════════════════════
def build_m_expr(filename: str, col_types: list[tuple]) -> str:
    type_lines = ',\n            '.join(
        f'{{"{c}", {t}}}' for c, t in col_types
    )
    return (
        f'let\n'
        f'    Source = Csv.Document(\n'
        f'        File.Contents(FolderPath & "\\\\{filename}"),\n'
        f'        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),\n'
        f'    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        f'    Typed   = Table.TransformColumnTypes(Headers, {{\n'
        f'            {type_lines}\n'
        f'        }})\n'
        f'in\n'
        f'    Typed'
    )

T  = "type text"
I  = "Int64.Type"
D  = "type number"
DT = "type datetime"
B  = "type logical"

# ══════════════════════════════════════════════════════════════
# TABLE DEFINITIONS  (name, filename, column types)
# ══════════════════════════════════════════════════════════════
TABLES = {

"fact_transactions": {
    "file": "fact_transactions.csv",
    "cols": [
        ("transaction_id",    T), ("user_id",           T),
        ("date_key",          I), ("transaction_datetime", DT),
        ("hour",              I), ("time_bucket",        T),
        ("payment_method",    T), ("category",           T),
        ("merchant",          T), ("platform",           T),
        ("device_type",       T), ("city",               T),
        ("amount",            D), ("amount_bucket",      T),
        ("net_amount",        D), ("cashback_earned",    D),
        ("discount_applied",  D), ("total_savings",      D),
        ("savings_pct",       D), ("status",             T),
        ("is_success",        I), ("is_failed",          I),
        ("is_pending",        I), ("failure_reason",     T),
        ("processing_time_sec", D), ("processing_speed", T),
        ("is_flagged",        B), ("is_flagged_int",     I),
        ("fraud_reason",      T), ("is_refunded",        B),
        ("is_refunded_int",   I), ("refund_amount",      D),
    ],
},

"dim_date": {
    "file": "dim_date.csv",
    "cols": [
        ("date_key",          I), ("date",               DT),
        ("year",              I), ("month",              I),
        ("month_name",        T), ("month_year",         T),
        ("quarter",           I), ("quarter_label",      T),
        ("day",               I), ("day_of_week",        I),
        ("day_name",          T), ("week_number",        I),
        ("is_weekend",        I), ("is_month_start",     I),
        ("is_month_end",      I), ("is_festival_season", I),
    ],
},

"dim_users": {
    "file": "dim_users.csv",
    "cols": [
        ("user_id",              T), ("age_group",            T),
        ("gender",               T), ("account_tenure",       T),
        ("customer_tier",        T), ("spending_persona",     T),
        ("preferred_method",     T), ("user_home_city",       T),
        ("user_total_txns",      I), ("user_total_spend",     D),
        ("user_avg_txn_amount",  D), ("user_failure_rate_pct",D),
        ("user_spending_tier",   T),
    ],
},

"dim_payment_method": {
    "file": "dim_payment_method.csv",
    "cols": [
        ("payment_method",    T), ("payment_type",       T),
        ("base_failure_rate", D),
    ],
},

"dim_category": {
    "file": "dim_category.csv",
    "cols": [
        ("category",       T), ("category_group", T),
    ],
},

"dim_platform": {
    "file": "dim_platform.csv",
    "cols": [
        ("platform", T), ("channel", T),
    ],
},

}

# ══════════════════════════════════════════════════════════════
# DAX MEASURES  (all on fact_transactions)
# ══════════════════════════════════════════════════════════════
MEASURES = [
    # Volume
    ("Total Transactions",     "COUNTROWS(fact_transactions)"),
    ("Successful Transactions","CALCULATE(COUNTROWS(fact_transactions),fact_transactions[status]=\"Success\")"),
    ("Failed Transactions",    "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[status]=\"Failed\")"),
    ("Pending Transactions",   "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[status]=\"Pending\")"),
    # Rates
    ("Success Rate %",         "DIVIDE([Successful Transactions],[Total Transactions],0)*100"),
    ("Failure Rate %",         "DIVIDE([Failed Transactions],[Total Transactions],0)*100"),
    ("Pending Rate %",         "DIVIDE([Pending Transactions],[Total Transactions],0)*100"),
    # Revenue
    ("Total Revenue",          "CALCULATE(SUM(fact_transactions[amount]),fact_transactions[status]=\"Success\")"),
    ("Avg Transaction Amount", "CALCULATE(AVERAGE(fact_transactions[amount]),fact_transactions[status]=\"Success\")"),
    ("Total Net Revenue",      "CALCULATE(SUM(fact_transactions[net_amount]),fact_transactions[status]=\"Success\")"),
    ("Total Cashback",         "SUM(fact_transactions[cashback_earned])"),
    ("Total Discounts",        "SUM(fact_transactions[discount_applied])"),
    ("Total Savings",          "SUM(fact_transactions[total_savings])"),
    ("Lost Revenue (Failures)","CALCULATE(SUM(fact_transactions[amount]),fact_transactions[status]=\"Failed\")"),
    # Users
    ("Unique Users",           "DISTINCTCOUNT(fact_transactions[user_id])"),
    ("Avg Transactions Per User","DIVIDE([Total Transactions],[Unique Users],0)"),
    ("Avg Revenue Per User",   "DIVIDE([Total Revenue],[Unique Users],0)"),
    # Fraud
    ("Flagged Transactions",   "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[is_flagged]=TRUE())"),
    ("Fraud Rate %",           "DIVIDE([Flagged Transactions],[Total Transactions],0)*100"),
    ("Avg Flagged Amount",     "CALCULATE(AVERAGE(fact_transactions[amount]),fact_transactions[is_flagged]=TRUE())"),
    ("Total Flagged Volume",   "CALCULATE(SUM(fact_transactions[amount]),fact_transactions[is_flagged]=TRUE())"),
    # Refunds
    ("Total Refunds",          "CALCULATE(COUNTROWS(fact_transactions),fact_transactions[is_refunded]=TRUE())"),
    ("Refund Rate %",          "DIVIDE([Total Refunds],[Total Transactions],0)*100"),
    ("Total Refund Value",     "SUM(fact_transactions[refund_amount])"),
    ("Avg Refund Amount",      "CALCULATE(AVERAGE(fact_transactions[refund_amount]),fact_transactions[is_refunded]=TRUE())"),
    # Processing
    ("Avg Processing Time (sec)","CALCULATE(AVERAGE(fact_transactions[processing_time_sec]),fact_transactions[status]=\"Success\")"),
    # Time intelligence
    ("Revenue PM",             "CALCULATE([Total Revenue],DATEADD(dim_date[date],-1,MONTH))"),
    ("Revenue MoM Growth %",   "VAR _c=[Total Revenue] VAR _p=[Revenue PM] RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Transactions PM",        "CALCULATE([Total Transactions],DATEADD(dim_date[date],-1,MONTH))"),
    ("Transactions MoM Growth %","VAR _c=[Total Transactions] VAR _p=[Transactions PM] RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Revenue PY",             "CALCULATE([Total Revenue],DATEADD(dim_date[date],-1,YEAR))"),
    ("Revenue YoY Growth %",   "VAR _c=[Total Revenue] VAR _p=[Revenue PY] RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Transactions YoY Growth %","VAR _c=[Total Transactions] VAR _p=CALCULATE([Total Transactions],DATEADD(dim_date[date],-1,YEAR)) RETURN DIVIDE(_c-_p,_p,0)*100"),
    ("Revenue YTD",            "TOTALYTD([Total Revenue],dim_date[date])"),
    ("Transactions YTD",       "TOTALYTD([Total Transactions],dim_date[date])"),
    ("Revenue MTD",            "TOTALMTD([Total Revenue],dim_date[date])"),
    ("Cumulative Revenue",     "CALCULATE([Total Revenue],FILTER(ALL(dim_date[date]),dim_date[date]<=MAX(dim_date[date])))"),
    # Labels
    ("Revenue in Crores",      "FORMAT(DIVIDE([Total Revenue],10000000),\"\\u20B90.00\") & \" Cr\""),
    ("Revenue in Lakhs",       "FORMAT(DIVIDE([Total Revenue],100000),\"\\u20B90.00\") & \" L\""),
    ("Success Rate Color",     "SWITCH(TRUE(),[Success Rate %]>=95,\"#10b981\",[Success Rate %]>=90,\"#f59e0b\",\"#ef4444\")"),
]

# ══════════════════════════════════════════════════════════════
# RELATIONSHIPS
# ══════════════════════════════════════════════════════════════
RELATIONSHIPS = [
    # fromTable, fromCol, toTable, toCol
    ("fact_transactions", "date_key",       "dim_date",           "date_key"),
    ("fact_transactions", "user_id",        "dim_users",          "user_id"),
    ("fact_transactions", "payment_method", "dim_payment_method", "payment_method"),
    ("fact_transactions", "category",       "dim_category",       "category"),
    ("fact_transactions", "platform",       "dim_platform",       "platform"),
]

# ══════════════════════════════════════════════════════════════
# BUILD DataModelSchema JSON
# ══════════════════════════════════════════════════════════════
def build_table(name: str, info: dict) -> dict:
    cols_json = []
    for col_name, col_type in info["cols"]:
        pbi_type = {
            "type text":     "string",
            "Int64.Type":    "int64",
            "type number":   "double",
            "type datetime": "dateTime",
            "type logical":  "boolean",
        }[col_type]
        cols_json.append({
            "name":     col_name,
            "dataType": pbi_type,
            "sourceColumn": col_name,
            "annotations": [{"name": "SummarizationSetBy", "value": "Automatic"}],
        })

    measures_json = []
    if name == "fact_transactions":
        for m_name, m_expr in MEASURES:
            measures_json.append({
                "name":        m_name,
                "expression":  m_expr,
                "formatString": "0.00" if "%" in m_name else
                                "₹#,##0" if any(k in m_name for k in ["Revenue","Amount","Value","Cashback","Savings","Discounts"]) else
                                "#,##0",
                "annotations": [{"name": "PBI_FormatHint", "value": '{"isGeneralNumber":true}'}],
            })

    partition = {
        "name": name,
        "mode": "import",
        "source": {
            "type": "m",
            "expression": build_m_expr(info["file"], info["cols"]),
        },
    }

    tbl = {
        "name": name,
        "columns": cols_json,
        "partitions": [partition],
        "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
    }
    if measures_json:
        tbl["measures"] = measures_json
    return tbl


def build_relationship(i, from_tbl, from_col, to_tbl, to_col) -> dict:
    return {
        "name":          f"rel_{i}",
        "fromTable":     from_tbl,
        "fromColumn":    from_col,
        "toTable":       to_tbl,
        "toColumn":      to_col,
        "crossFilteringBehavior": "oneDirection",
    }


def build_data_model_schema() -> str:
    tables  = [build_table(name, info) for name, info in TABLES.items()]
    rels    = [build_relationship(i, *r) for i, r in enumerate(RELATIONSHIPS)]

    schema = {
        "name": "ReportSection",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-IN",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True,
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-IN",
            "tables": tables,
            "relationships": rels,
            "expressions": [
                {
                    "name": "FolderPath",
                    "kind": "m",
                    "expression": (
                        '"C:\\\\Users\\\\YourName\\\\path\\\\to\\\\powerbi_data"'
                        '\n// ⚠ Update this path to your powerbi_data\\ folder'
                    ),
                    "annotations": [
                        {"name": "PBI_NavigationStepName",  "value": "Navigation"},
                        {"name": "PBI_ParameterQueryName",  "value": "FolderPath"},
                    ],
                }
            ],
            "annotations": [
                {"name": "PBIDesktopVersion", "value": "2.136.1202.0"},
                {"name": "PBI_QueryOrder", "value": json.dumps(list(TABLES.keys()))},
            ],
        },
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════
# BUILD Report/Layout JSON  (6 blank pages)
# ══════════════════════════════════════════════════════════════
PAGE_NAMES = [
    "Executive Overview",
    "Transaction Analysis",
    "Failure Analysis",
    "User Analytics",
    "Fraud & Refunds",
    "Platform & Device",
]

def build_report_layout() -> str:
    sections = []
    for i, page_name in enumerate(PAGE_NAMES):
        cfg = json.dumps({
            "id": i,
            "type": "report",
            "objects": {},
            "layoutOptimization": 0,
        })
        sections.append({
            "id":              i,
            "name":            f"ReportSection{i}",
            "displayName":     page_name,
            "filters":         "[]",
            "ordinal":         i,
            "visualContainers": [],
            "config":          cfg,
            "layoutOptimization": 0,
        })

    layout = {
        "id": 0,
        "sections": sections,
        "config": json.dumps({
            "version": "5.47",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU07",
                    "version": "5.47",
                    "type": 2,
                }
            },
        }),
        "layoutOptimization": 0,
        "pods":    None,
        "resourcePackages": [],
    }
    return json.dumps(layout, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════
# BUILD CONTENT_TYPES, METADATA, SETTINGS
# ══════════════════════════════════════════════════════════════
CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json"          ContentType="application/json" />
  <Default Extension="xml"           ContentType="application/xml" />
  <Override PartName="/DataModelSchema" ContentType="application/json" />
  <Override PartName="/DiagramState"    ContentType="application/json" />
  <Override PartName="/Report/Layout"   ContentType="application/json" />
  <Override PartName="/Settings"        ContentType="application/json" />
  <Override PartName="/Metadata"        ContentType="application/json" />
  <Override PartName="/Version"         ContentType="application/octet-stream" />
</Types>"""

METADATA = json.dumps({
    "version": "4.0",
    "createdFrom": "PublishedVersion",
})

SETTINGS = json.dumps({
    "version": "1.0",
    "useStylableVisuals": True,
    "isPaidArtifact": False,
    "slowDataSourceSettings": {
        "isCrossHighlightingDisabled": False,
        "isSlicerSelectionsButtonEnabled": False,
        "isFilterPaneSearchEnabled": False,
        "isFieldWellRestricted": False,
        "maxIntermediateRowCountForSingleDatasource": 1000000,
        "maxIntermediateRowCount": 1000000,
        "maxResultRowCountForSingleDatasource": 30000,
        "maxResultRowCount": 30000,
    },
})

DIAGRAM_STATE = json.dumps({
    "version": "0",
    "positions": [],
})

VERSION = "2.0"

# ══════════════════════════════════════════════════════════════
# WRITE .pbit  (ZIP archive)
# ══════════════════════════════════════════════════════════════
def create_pbit():
    print("Building DataModelSchema ...")
    data_model_schema = build_data_model_schema()

    print("Building Report/Layout ...")
    report_layout = build_report_layout()

    print(f"Writing {OUT_FILE} ...")
    with zipfile.ZipFile(OUT_FILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        def add(arcname, content):
            zf.writestr(zipfile.ZipInfo(arcname), content.encode("utf-8") if isinstance(content, str) else content)

        add("[Content_Types].xml", CONTENT_TYPES)
        add("Version",            VERSION)
        add("Metadata",           METADATA)
        add("Settings",           SETTINGS)
        add("DiagramState",       DIAGRAM_STATE)
        add("DataModelSchema",    data_model_schema)
        add("SecurityBindings",   "")
        add("Report/Layout",      report_layout)

    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f"\n{'=' * 60}")
    print(f"  Digital_Payment_Analysis.pbit  ({size_kb:.0f} KB)")
    print(f"{'=' * 60}")
    lines = [
        "",
        "  HOW TO USE",
        "  1. Open Power BI Desktop (free: microsoft.com/powerbi)",
        "  2. File > Open > Digital_Payment_Analysis.pbit",
        "     Set FolderPath to your powerbi_data\\ folder path",
        "  3. Click Load - all 6 tables import automatically",
        "  4. Model view - verify 5 relationships exist",
        "  5. Right-click dim_date > Mark as Date Table > select 'date'",
        "  6. Add visuals using the 40+ measures in the Fields pane",
        "     See POWERBI_GUIDE.md for the full page-by-page layout",
        "  7. File > Save As > .pbix when done",
        "",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    create_pbit()
