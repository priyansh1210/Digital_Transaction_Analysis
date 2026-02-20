"""
Digital Payment Transaction Analysis — Streamlit Dashboard
===========================================================
Phase 4: Interactive Dashboard

Run: streamlit run app.py
Requirements: streamlit, plotly, pandas, numpy
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Digital Payment Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #1e293b;
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: #cbd5e1;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        margin: 4px 0;
        letter-spacing: -0.5px;
    }
    .kpi-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .kpi-delta {
        font-size: 12px;
        margin-top: 4px;
    }
    
    /* Section headers */
    .section-header {
        color: #f1f5f9;
        font-size: 22px;
        font-weight: 700;
        margin: 30px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #3b82f6;
        display: inline-block;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #94a3b8;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #f1f5f9;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
    }
    
    /* Plotly chart containers */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(script_dir, 'transactions_cleaned.csv'))
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# ============================================================
# PLOTLY THEME
# ============================================================
COLORS = {
    'bg': '#0f172a',
    'card_bg': '#1e293b',
    'text': '#f1f5f9',
    'muted': '#94a3b8',
    'border': '#334155',
    'blue': '#3b82f6',
    'green': '#10b981',
    'red': '#ef4444',
    'amber': '#f59e0b',
    'purple': '#8b5cf6',
    'pink': '#ec4899',
    'teal': '#14b8a6',
    'cyan': '#06b6d4',
}

CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                '#ec4899', '#14b8a6', '#06b6d4', '#f97316', '#a855f7']

def chart_layout(title="", height=400, showlegend=True):
    return dict(
        title=dict(text=title, font=dict(color=COLORS['text'], size=16), x=0.01),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['muted'], size=12),
        height=height,
        showlegend=showlegend,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['muted'])),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor='#1e293b', zerolinecolor='#334155'),
        yaxis=dict(gridcolor='#1e293b', zerolinecolor='#334155'),
    )

# ============================================================
# SIDEBAR — FILTERS
# ============================================================
with st.sidebar:
    st.markdown("## 💳 Payment Analytics")
    st.markdown("---")
    
    # Date range
    st.markdown("### 📅 Date Range")
    date_min = df['date'].min().date()
    date_max = df['date'].max().date()
    date_range = st.date_input("Select range", [date_min, date_max], 
                                min_value=date_min, max_value=date_max)
    
    st.markdown("### 🏦 Payment Method")
    methods = st.multiselect("", df['payment_method'].unique().tolist(),
                              default=df['payment_method'].unique().tolist())
    
    st.markdown("### 📊 Status")
    statuses = st.multiselect("", df['status'].unique().tolist(),
                               default=df['status'].unique().tolist(), key="status_filter")
    
    st.markdown("### 🏙️ City")
    cities = st.multiselect("", sorted(df['city'].unique().tolist()),
                             default=sorted(df['city'].unique().tolist()), key="city_filter")
    
    st.markdown("### 📂 Category")
    categories = st.multiselect("", sorted(df['category'].unique().tolist()),
                                 default=sorted(df['category'].unique().tolist()), key="cat_filter")
    
    st.markdown("---")
    st.markdown(f"**Filtered:** `{len(df)}` → ", unsafe_allow_html=True)

# Apply filters
if len(date_range) == 2:
    mask = (
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1]) &
        (df['payment_method'].isin(methods)) &
        (df['status'].isin(statuses)) &
        (df['city'].isin(cities)) &
        (df['category'].isin(categories))
    )
else:
    mask = (
        (df['payment_method'].isin(methods)) &
        (df['status'].isin(statuses)) &
        (df['city'].isin(cities)) &
        (df['category'].isin(categories))
    )

fdf = df[mask].copy()

# Update sidebar count
with st.sidebar:
    st.markdown(f"**`{len(fdf):,}` transactions shown**")

# ============================================================
# NAVIGATION TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", "💰 Transactions", "❌ Failures", 
    "👥 Users", "🛡️ Fraud & Refunds", "📱 Platform & Device"
])

# ============================================================
# TAB 1: OVERVIEW DASHBOARD
# ============================================================
with tab1:
    st.markdown('<p class="section-header">Executive Overview</p>', unsafe_allow_html=True)
    
    # KPI Row
    total_txn = len(fdf)
    success_txn = (fdf['status'] == 'Success').sum()
    success_rate = success_txn / total_txn * 100 if total_txn > 0 else 0
    total_volume = fdf[fdf['status'] == 'Success']['amount'].sum()
    avg_txn = fdf[fdf['status'] == 'Success']['amount'].mean() if success_txn > 0 else 0
    unique_users = fdf['user_id'].nunique()
    total_cashback = fdf['cashback_earned'].sum()
    fraud_count = fdf['is_flagged'].sum()
    refund_count = fdf['is_refunded'].sum()
    
    k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
    
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Txns</div>
            <div class="kpi-value" style="color:{COLORS['blue']}">{total_txn:,}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        sr_color = COLORS['green'] if success_rate > 90 else COLORS['amber'] if success_rate > 85 else COLORS['red']
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Success Rate</div>
            <div class="kpi-value" style="color:{sr_color}">{success_rate:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Volume</div>
            <div class="kpi-value" style="color:{COLORS['purple']}">₹{total_volume/1e7:.2f}Cr</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Avg Txn</div>
            <div class="kpi-value" style="color:{COLORS['amber']}">₹{avg_txn:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Users</div>
            <div class="kpi-value" style="color:{COLORS['teal']}">{unique_users}</div>
        </div>""", unsafe_allow_html=True)
    with k6:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Cashback</div>
            <div class="kpi-value" style="color:{COLORS['green']}">₹{total_cashback/1e3:.1f}K</div>
        </div>""", unsafe_allow_html=True)
    with k7:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Fraud Flags</div>
            <div class="kpi-value" style="color:{COLORS['red']}">{fraud_count}</div>
        </div>""", unsafe_allow_html=True)
    with k8:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Refunds</div>
            <div class="kpi-value" style="color:{COLORS['pink']}">{refund_count}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Monthly Trend + Payment Method Pie
    col1, col2 = st.columns([2, 1])
    
    with col1:
        monthly = fdf.groupby('month').agg(
            txn_count=('transaction_id', 'count'),
            success=('status', lambda x: (x == 'Success').sum()),
            volume=('amount', 'sum')
        ).reset_index()
        monthly['success_rate'] = (monthly['success'] / monthly['txn_count'] * 100).round(1)
        month_labels = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                       7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        monthly['month_name'] = monthly['month'].map(month_labels)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=monthly['month_name'], y=monthly['txn_count'],
            name='Transactions', marker_color=COLORS['blue'], opacity=0.7
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=monthly['month_name'], y=monthly['success_rate'],
            name='Success Rate %', line=dict(color=COLORS['green'], width=3),
            mode='lines+markers'
        ), secondary_y=True)
        fig.update_layout(**chart_layout("Monthly Transaction Trend", height=380))
        fig.update_yaxes(title_text="Count", secondary_y=False, gridcolor='#1e293b')
        fig.update_yaxes(title_text="Success %", secondary_y=True, range=[80, 100], gridcolor='#1e293b')
        
        # Festival season highlight
        fig.add_vrect(x0="Oct", x1="Nov", fillcolor=COLORS['amber'], opacity=0.08,
                      annotation_text="Festival Season", annotation_position="top left",
                      annotation_font_color=COLORS['amber'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        method_dist = fdf['payment_method'].value_counts().reset_index()
        method_dist.columns = ['method', 'count']
        fig = go.Figure(go.Pie(
            labels=method_dist['method'], values=method_dist['count'],
            hole=0.55, marker=dict(colors=CHART_COLORS),
            textinfo='label+percent', textfont=dict(size=11, color='white')
        ))
        fig.update_layout(**chart_layout("Payment Method Split", height=380, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Category Volume + City Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        cat_stats = fdf[fdf['status']=='Success'].groupby('category')['amount'].sum().sort_values(ascending=True).reset_index()
        fig = go.Figure(go.Bar(
            y=cat_stats['category'], x=cat_stats['amount']/1e5,
            orientation='h', marker_color=CHART_COLORS[:len(cat_stats)],
            text=[f"₹{v:.1f}L" for v in cat_stats['amount']/1e5],
            textposition='outside', textfont=dict(color=COLORS['text'])
        ))
        fig.update_layout(**chart_layout("Revenue by Category (₹ Lakhs)", height=380, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        city_stats = fdf.groupby('city').size().sort_values(ascending=True).reset_index(name='count')
        fig = go.Figure(go.Bar(
            y=city_stats['city'], x=city_stats['count'],
            orientation='h', marker_color=COLORS['teal'],
            text=city_stats['count'], textposition='outside',
            textfont=dict(color=COLORS['text'])
        ))
        fig.update_layout(**chart_layout("Transactions by City", height=380, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2: TRANSACTION ANALYSIS
# ============================================================
with tab2:
    st.markdown('<p class="section-header">Transaction Deep Dive</p>', unsafe_allow_html=True)
    
    # Hourly Heatmap
    hourly_day = fdf.groupby(['day_name', 'hour']).size().reset_index(name='count')
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    pivot = hourly_day.pivot_table(index='day_name', columns='hour', values='count', fill_value=0)
    pivot = pivot.reindex(day_order)
    
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=[f"{h}:00" for h in pivot.columns], y=pivot.index,
        colorscale='YlOrRd', hoverongaps=False,
        colorbar=dict(title="Txns", titlefont=dict(color=COLORS['muted']),
                      tickfont=dict(color=COLORS['muted']))
    ))
    fig.update_layout(**chart_layout("Transaction Heatmap: Day × Hour", height=350, showlegend=False))
    st.plotly_chart(fig, use_container_width=True)
    
    # Row: Time bucket + Weekend comparison
    col1, col2 = st.columns(2)
    
    with col1:
        tb = fdf.groupby('time_bucket').agg(
            count=('transaction_id', 'count'),
            avg_amt=('amount', 'mean'),
            sr=('status', lambda x: (x=='Success').mean()*100)
        ).reindex(['Morning','Afternoon','Evening','Night']).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=tb['time_bucket'], y=tb['count'],
            name='Count', marker_color=[COLORS['amber'], COLORS['blue'], COLORS['purple'], COLORS['teal']]
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=tb['time_bucket'], y=tb['sr'],
            name='Success %', line=dict(color=COLORS['green'], width=3),
            mode='lines+markers'
        ), secondary_y=True)
        fig.update_layout(**chart_layout("Time of Day Analysis", height=350))
        fig.update_yaxes(secondary_y=True, range=[80, 100], gridcolor='#1e293b')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        wk = fdf.groupby('is_weekend').agg(
            count=('transaction_id', 'count'),
            avg_amt=('amount', 'mean'),
            volume=('amount', 'sum'),
            sr=('status', lambda x: (x=='Success').mean()*100)
        ).reset_index()
        wk['label'] = wk['is_weekend'].map({0: 'Weekday', 1: 'Weekend'})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Transactions', 'Avg Amount (₹)', 'Success Rate (%)'],
            y=[wk.loc[wk['is_weekend']==0, 'count'].values[0],
               wk.loc[wk['is_weekend']==0, 'avg_amt'].values[0],
               wk.loc[wk['is_weekend']==0, 'sr'].values[0]],
            name='Weekday', marker_color=COLORS['blue']
        ))
        fig.add_trace(go.Bar(
            x=['Transactions', 'Avg Amount (₹)', 'Success Rate (%)'],
            y=[wk.loc[wk['is_weekend']==1, 'count'].values[0],
               wk.loc[wk['is_weekend']==1, 'avg_amt'].values[0],
               wk.loc[wk['is_weekend']==1, 'sr'].values[0]],
            name='Weekend', marker_color=COLORS['amber']
        ))
        fig.update_layout(**chart_layout("Weekday vs Weekend", height=350), barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    # Payment Method Success Rate Comparison
    method_stats = fdf.groupby('payment_method').agg(
        count=('transaction_id', 'count'),
        success_rate=('status', lambda x: (x=='Success').mean()*100),
        avg_amount=('amount', 'mean'),
        avg_proc=('processing_time_sec', 'mean')
    ).sort_values('count', ascending=False).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=method_stats['payment_method'], y=method_stats['success_rate'],
        marker_color=[COLORS['green'] if r > 90 else COLORS['amber'] if r > 85 else COLORS['red']
                      for r in method_stats['success_rate']],
        text=[f"{v:.1f}%" for v in method_stats['success_rate']],
        textposition='outside', textfont=dict(color=COLORS['text'])
    ))
    fig.update_layout(**chart_layout("Success Rate by Payment Method", height=350, showlegend=False))
    fig.update_yaxes(range=[75, 100])
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 3: FAILURE ANALYSIS
# ============================================================
with tab3:
    st.markdown('<p class="section-header">Failed Transaction Analysis</p>', unsafe_allow_html=True)
    
    failed = fdf[fdf['status'] == 'Failed']
    
    if len(failed) > 0:
        # KPI Row
        fk1, fk2, fk3, fk4 = st.columns(4)
        with fk1:
            st.metric("Failed Transactions", f"{len(failed):,}")
        with fk2:
            st.metric("Failure Rate", f"{len(failed)/len(fdf)*100:.1f}%")
        with fk3:
            st.metric("Lost Revenue", f"₹{failed['amount'].sum()/1e5:.1f}L")
        with fk4:
            st.metric("Avg Failed Amount", f"₹{failed['amount'].mean():,.0f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Failure reasons
            reasons = failed['failure_reason'].value_counts().head(10).reset_index()
            reasons.columns = ['reason', 'count']
            fig = go.Figure(go.Bar(
                y=reasons['reason'][::-1], x=reasons['count'][::-1],
                orientation='h', marker_color=COLORS['red'],
                text=reasons['count'][::-1], textposition='outside',
                textfont=dict(color=COLORS['text'])
            ))
            fig.update_layout(**chart_layout("Top Failure Reasons", height=400, showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Failure by method
            method_fail = failed.groupby('payment_method').agg(
                count=('transaction_id', 'count'),
                lost=('amount', 'sum')
            ).sort_values('lost', ascending=True).reset_index()
            
            fig = go.Figure(go.Bar(
                y=method_fail['payment_method'], x=method_fail['lost']/1e5,
                orientation='h', marker_color=COLORS['red'], opacity=0.8,
                text=[f"₹{v:.1f}L ({c} txns)" for v, c in zip(method_fail['lost'], method_fail['count'])],
                textposition='outside', textfont=dict(color=COLORS['text'])
            ))
            fig.update_layout(**chart_layout("Lost Revenue by Method (₹ Lakhs)", height=400, showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
        
        # Failure rate by hour
        hourly_fail = fdf.groupby('hour').apply(
            lambda x: pd.Series({
                'total': len(x),
                'failed': (x['status']=='Failed').sum(),
                'rate': (x['status']=='Failed').mean()*100
            })
        ).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hourly_fail['hour'], y=hourly_fail['total'],
            name='Total Txns', marker_color=COLORS['blue'], opacity=0.4
        ))
        fig.add_trace(go.Scatter(
            x=hourly_fail['hour'], y=hourly_fail['rate'],
            name='Failure Rate %', yaxis='y2',
            line=dict(color=COLORS['red'], width=3), mode='lines+markers'
        ))
        fig.update_layout(
            **chart_layout("Failure Rate by Hour", height=350),
            yaxis2=dict(title='Failure %', overlaying='y', side='right',
                       gridcolor='#1e293b', range=[0, 20])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Method × Reason heatmap
        cross = pd.crosstab(failed['payment_method'], failed['failure_reason'])
        fig = go.Figure(go.Heatmap(
            z=cross.values, x=cross.columns.tolist(), y=cross.index.tolist(),
            colorscale='Reds', text=cross.values, texttemplate='%{text}',
            colorbar=dict(title="Count", titlefont=dict(color=COLORS['muted']),
                         tickfont=dict(color=COLORS['muted']))
        ))
        fig.update_layout(**chart_layout("Failure Reason × Payment Method", height=350, showlegend=False))
        fig.update_xaxes(tickangle=35)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No failed transactions in the current filter selection.")


# ============================================================
# TAB 4: USER ANALYSIS
# ============================================================
with tab4:
    st.markdown('<p class="section-header">User Behavior & Demographics</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age group analysis
        age_stats = fdf.groupby('age_group').agg(
            count=('transaction_id', 'count'),
            avg_amt=('amount', 'mean'),
            users=('user_id', 'nunique')
        ).reset_index()
        age_order = ['18-24', '25-34', '35-44', '45-54', '55+']
        age_stats['age_group'] = pd.Categorical(age_stats['age_group'], categories=age_order, ordered=True)
        age_stats = age_stats.sort_values('age_group')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=age_stats['age_group'], y=age_stats['count'],
            name='Transactions', marker_color=COLORS['blue']
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=age_stats['age_group'], y=age_stats['avg_amt'],
            name='Avg Amount (₹)', line=dict(color=COLORS['amber'], width=3),
            mode='lines+markers'
        ), secondary_y=True)
        fig.update_layout(**chart_layout("Age Group Analysis", height=370))
        fig.update_yaxes(secondary_y=True, gridcolor='#1e293b')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer tier
        tier_stats = fdf.groupby('customer_tier').agg(
            count=('transaction_id', 'count'),
            volume=('amount', lambda x: x[fdf.loc[x.index, 'status']=='Success'].sum()),
            users=('user_id', 'nunique')
        ).reset_index()
        tier_order = ['New', 'Regular', 'Premium', 'VIP']
        tier_stats['customer_tier'] = pd.Categorical(tier_stats['customer_tier'], categories=tier_order, ordered=True)
        tier_stats = tier_stats.sort_values('customer_tier')
        
        fig = go.Figure(go.Bar(
            x=tier_stats['customer_tier'], y=tier_stats['count'],
            marker_color=[COLORS['muted'], COLORS['blue'], COLORS['purple'], COLORS['amber']],
            text=[f"{c:,} txns<br>{u} users" for c, u in zip(tier_stats['count'], tier_stats['users'])],
            textposition='outside', textfont=dict(color=COLORS['text'], size=11)
        ))
        fig.update_layout(**chart_layout("Customer Tier Distribution", height=370, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    # Spending persona
    col1, col2 = st.columns(2)
    
    with col1:
        persona = fdf[fdf['status']=='Success'].groupby('spending_persona').agg(
            avg_amt=('amount', 'mean'),
            total=('amount', 'sum'),
            users=('user_id', 'nunique')
        ).reset_index()
        persona['per_user'] = persona['total'] / persona['users']
        persona = persona.sort_values('avg_amt', ascending=True)
        
        fig = go.Figure(go.Bar(
            y=persona['spending_persona'], x=persona['avg_amt'],
            orientation='h',
            marker_color=[COLORS['green'], COLORS['blue'], COLORS['amber'], COLORS['red']],
            text=[f"₹{v:,.0f}" for v in persona['avg_amt']],
            textposition='outside', textfont=dict(color=COLORS['text'])
        ))
        fig.update_layout(**chart_layout("Avg Transaction by Spending Persona", height=320, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gender split
        gender_stats = fdf.groupby('gender').agg(
            count=('transaction_id', 'count'),
            avg_amt=('amount', 'mean')
        ).reset_index()
        
        fig = go.Figure(go.Pie(
            labels=gender_stats['gender'], values=gender_stats['count'],
            hole=0.5, marker=dict(colors=[COLORS['blue'], COLORS['pink'], COLORS['teal']]),
            textinfo='label+percent', textfont=dict(color='white', size=12)
        ))
        fig.update_layout(**chart_layout("Gender Distribution", height=320, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly Active Users
    mau = fdf.groupby('month').agg(
        mau=('user_id', 'nunique'),
        txn_per_user=('transaction_id', lambda x: len(x) / fdf.loc[x.index, 'user_id'].nunique())
    ).reset_index()
    mau['month_name'] = mau['month'].map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                                           7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=mau['month_name'], y=mau['mau'],
        name='MAU', marker_color=COLORS['teal'], opacity=0.7
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=mau['month_name'], y=mau['txn_per_user'],
        name='Txn per User', line=dict(color=COLORS['amber'], width=3),
        mode='lines+markers'
    ), secondary_y=True)
    fig.update_layout(**chart_layout("Monthly Active Users & Engagement", height=350))
    fig.update_yaxes(secondary_y=True, gridcolor='#1e293b')
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 5: FRAUD & REFUNDS
# ============================================================
with tab5:
    st.markdown('<p class="section-header">Fraud Detection & Refund Analysis</p>', unsafe_allow_html=True)
    
    # Fraud section
    st.markdown("#### 🛡️ Fraud Flags")
    flagged = fdf[fdf['is_flagged'] == True]
    
    fk1, fk2, fk3, fk4 = st.columns(4)
    with fk1:
        st.metric("Flagged Transactions", f"{len(flagged)}")
    with fk2:
        st.metric("Flag Rate", f"{len(flagged)/len(fdf)*100:.1f}%" if len(fdf) > 0 else "0%")
    with fk3:
        st.metric("Avg Flagged Amount", f"₹{flagged['amount'].mean():,.0f}" if len(flagged) > 0 else "₹0")
    with fk4:
        st.metric("Total Flagged Volume", f"₹{flagged['amount'].sum()/1e5:.1f}L" if len(flagged) > 0 else "₹0")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(flagged) > 0:
            fraud_reasons = flagged['fraud_reason'].value_counts().reset_index()
            fraud_reasons.columns = ['reason', 'count']
            fig = go.Figure(go.Bar(
                y=fraud_reasons['reason'][::-1], x=fraud_reasons['count'][::-1],
                orientation='h', marker_color=COLORS['red'],
                text=fraud_reasons['count'][::-1], textposition='outside',
                textfont=dict(color=COLORS['text'])
            ))
            fig.update_layout(**chart_layout("Fraud Flag Reasons", height=320, showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if len(flagged) > 0:
            # Amount distribution: flagged vs normal
            fig = go.Figure()
            fig.add_trace(go.Box(
                y=fdf[fdf['is_flagged']==False]['amount'].clip(upper=50000),
                name='Normal', marker_color=COLORS['blue'], boxmean=True
            ))
            fig.add_trace(go.Box(
                y=fdf[fdf['is_flagged']==True]['amount'].clip(upper=50000),
                name='Flagged', marker_color=COLORS['red'], boxmean=True
            ))
            fig.update_layout(**chart_layout("Amount Distribution: Normal vs Flagged", height=320))
            st.plotly_chart(fig, use_container_width=True)
    
    # Refund section
    st.markdown("---")
    st.markdown("#### 💸 Refund Analysis")
    refunded = fdf[fdf['is_refunded'] == True]
    
    rk1, rk2, rk3, rk4 = st.columns(4)
    with rk1:
        st.metric("Total Refunds", f"{len(refunded)}")
    with rk2:
        st.metric("Refund Rate", f"{len(refunded)/len(fdf)*100:.1f}%" if len(fdf) > 0 else "0%")
    with rk3:
        st.metric("Total Refund Value", f"₹{refunded['refund_amount'].sum()/1e3:.1f}K")
    with rk4:
        full_refunds = len(refunded[refunded['refund_amount'] >= refunded['amount'] * 0.99]) if len(refunded) > 0 else 0
        st.metric("Full Refunds", f"{full_refunds} ({full_refunds/len(refunded)*100:.0f}%)" if len(refunded) > 0 else "0")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(refunded) > 0:
            ref_cat = refunded.groupby('category')['refund_amount'].agg(['count','sum']).sort_values('count', ascending=True).reset_index()
            ref_cat.columns = ['category', 'count', 'total']
            fig = go.Figure(go.Bar(
                y=ref_cat['category'], x=ref_cat['count'],
                orientation='h', marker_color=COLORS['pink'],
                text=[f"{c} (₹{t/1e3:.1f}K)" for c, t in zip(ref_cat['count'], ref_cat['total'])],
                textposition='outside', textfont=dict(color=COLORS['text'])
            ))
            fig.update_layout(**chart_layout("Refunds by Category", height=320, showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if len(refunded) > 0:
            ref_method = refunded.groupby('payment_method')['refund_amount'].agg(['count','sum']).sort_values('sum', ascending=True).reset_index()
            ref_method.columns = ['method', 'count', 'total']
            fig = go.Figure(go.Bar(
                y=ref_method['method'], x=ref_method['total']/1e3,
                orientation='h', marker_color=COLORS['pink'], opacity=0.8,
                text=[f"₹{v:.1f}K" for v in ref_method['total']/1e3],
                textposition='outside', textfont=dict(color=COLORS['text'])
            ))
            fig.update_layout(**chart_layout("Refund Value by Method (₹K)", height=320, showlegend=False))
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 6: PLATFORM & DEVICE
# ============================================================
with tab6:
    st.markdown('<p class="section-header">Platform & Device Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        plat = fdf.groupby('platform').agg(
            count=('transaction_id', 'count'),
            sr=('status', lambda x: (x=='Success').mean()*100),
            avg_proc=('processing_time_sec', 'mean')
        ).sort_values('count', ascending=False).reset_index()
        
        fig = go.Figure(go.Pie(
            labels=plat['platform'], values=plat['count'],
            hole=0.55, marker=dict(colors=CHART_COLORS[:4]),
            textinfo='label+percent', textfont=dict(color='white', size=11)
        ))
        fig.update_layout(**chart_layout("Platform Distribution", height=370, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        device = fdf.groupby('device_type').agg(
            count=('transaction_id', 'count'),
            avg_amt=('amount', 'mean'),
            sr=('status', lambda x: (x=='Success').mean()*100)
        ).sort_values('count', ascending=True).reset_index()
        
        fig = go.Figure(go.Bar(
            y=device['device_type'], x=device['count'],
            orientation='h', marker_color=COLORS['cyan'],
            text=device['count'], textposition='outside',
            textfont=dict(color=COLORS['text'])
        ))
        fig.update_layout(**chart_layout("Device Type Distribution", height=370, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    # Android vs iOS deep dive
    mobile = fdf[fdf['device_type'].isin(['Android', 'iOS'])]
    if len(mobile) > 0:
        st.markdown("#### 📱 Android vs iOS Comparison")
        
        os_stats = mobile.groupby('device_type').agg(
            txn_count=('transaction_id', 'count'),
            avg_amount=('amount', 'mean'),
            success_rate=('status', lambda x: (x=='Success').mean()*100),
            total_volume=('amount', 'sum'),
            avg_proc=('processing_time_sec', 'mean'),
            cashback=('cashback_earned', 'sum'),
            flagged=('is_flagged', 'sum')
        ).reset_index()
        
        m1, m2, m3, m4 = st.columns(4)
        android = os_stats[os_stats['device_type']=='Android'].iloc[0] if 'Android' in os_stats['device_type'].values else None
        ios = os_stats[os_stats['device_type']=='iOS'].iloc[0] if 'iOS' in os_stats['device_type'].values else None
        
        if android is not None and ios is not None:
            with m1:
                st.metric("Android Txns", f"{int(android['txn_count']):,}")
                st.metric("iOS Txns", f"{int(ios['txn_count']):,}")
            with m2:
                st.metric("Android Avg ₹", f"₹{android['avg_amount']:,.0f}")
                st.metric("iOS Avg ₹", f"₹{ios['avg_amount']:,.0f}")
            with m3:
                st.metric("Android Success", f"{android['success_rate']:.1f}%")
                st.metric("iOS Success", f"{ios['success_rate']:.1f}%")
            with m4:
                st.metric("Android Proc Time", f"{android['avg_proc']:.2f}s")
                st.metric("iOS Proc Time", f"{ios['avg_proc']:.2f}s")
    
    # Cashback & Discount effectiveness
    st.markdown("---")
    st.markdown("#### 💰 Cashback & Discount Effectiveness")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cb = fdf[fdf['cashback_earned'] > 0].groupby('payment_method')['cashback_earned'].agg(['sum','count']).sort_values('sum', ascending=True).reset_index()
        cb.columns = ['method', 'total', 'count']
        fig = go.Figure(go.Bar(
            y=cb['method'], x=cb['total']/1e3,
            orientation='h', marker_color=COLORS['green'],
            text=[f"₹{v:.1f}K ({c} txns)" for v, c in zip(cb['total']/1e3, cb['count'])],
            textposition='outside', textfont=dict(color=COLORS['text'])
        ))
        fig.update_layout(**chart_layout("Cashback by Payment Method (₹K)", height=320, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        disc = fdf[fdf['discount_applied'] > 0].groupby('category')['discount_applied'].agg(['sum','count']).sort_values('sum', ascending=True).reset_index()
        disc.columns = ['category', 'total', 'count']
        fig = go.Figure(go.Bar(
            y=disc['category'], x=disc['total']/1e3,
            orientation='h', marker_color=COLORS['purple'],
            text=[f"₹{v:.1f}K ({c} txns)" for v, c in zip(disc['total']/1e3, disc['count'])],
            textposition='outside', textfont=dict(color=COLORS['text'])
        ))
        fig.update_layout(**chart_layout("Discounts by Category (₹K)", height=320, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; color: {COLORS["muted"]}; font-size: 12px; padding: 10px;'>
    Digital Payment Transaction Analysis Dashboard · Built with Streamlit & Plotly · 
    Dataset: {len(df):,} transactions · {df['user_id'].nunique()} users · Jan–Dec 2024
    </div>""",
    unsafe_allow_html=True
)
