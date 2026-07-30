"""
全球 AI 产业跟踪框架 - 增强版 Streamlit 仪表板
整合数据追踪、分析与可视化，支持相关性分析、动量指标、拐点检测、
加权健康度评分、热力图数据生成、完整报告生成及 CSV 导入导出。
所有指标一律折线图展示，新增趋势矩阵Tab。
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import sys
import tempfile
import math

sys.path.insert(0, os.path.dirname(__file__))

import database as db
from seed_data import seed_all
from fetchers import auto_fetch_all
from analysis import (
    check_all_signals,
    analyze_trend,
    analyze_category_trends,
    compute_health_score,
    get_signal_summary,
    generate_analysis_report,
    compute_correlation_matrix,
    compute_momentum,
    compute_all_momentum,
    detect_inflection_points,
    detect_all_inflections,
    compute_weighted_health_score,
    generate_heatmap_data,
    generate_full_report,
)
from data_io import (
    import_data_points_from_csv,
    export_all_data_to_csv,
    export_indicators_to_csv,
    export_signals_to_csv,
    generate_template_csv,
)

# ============ 配色方案 ============
COLOR_PALETTE = {
    "primary": "#1a73e8",
    "success": "#34a853",
    "warning": "#fbbc04",
    "danger": "#ea4335",
    "info": "#4285f4",
    "light_bg": "#f8f9fa",
    "dark_text": "#202124",
}

CATEGORY_COLORS = {
    "供给端": "#1f77b4",
    "需求端": "#ff7f0e",
    "资本与融资": "#2ca02c",
    "中游数据代理": "#d62728",
    "Coding渗透": "#9467bd",
    "非Coding渗透": "#8c564b",
    "个人用户渗透": "#e377c2",
    "企业用户渗透": "#7f7f7f",
    "开源生态": "#ff9f1c",
}

TREND_COLORS = {
    "上升": "#34a853",
    "下降": "#ea4335",
    "平稳": "#fbbc04",
}

# ============ 页面配置 ============
st.set_page_config(
    page_title="全球 AI 产业跟踪框架",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ 自定义 CSS ============
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
    }
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1a73e8;
    }
    .trend-up { color: #34a853; }
    .trend-down { color: #ea4335; }
    .trend-flat { color: #fbbc04; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .health-score-high { color: #34a853; }
    .health-score-mid { color: #fbbc04; }
    .health-score-low { color: #ea4335; }
</style>
""", unsafe_allow_html=True)


# ============ 初始化 ============
def ensure_initialized():
    if not os.path.exists(db.DB_PATH):
        seed_all()


ensure_initialized()


# ============ 侧边栏 ============
with st.sidebar:
    st.header("⚙ 控制面板")

    if st.button("🔄 重置数据库", use_container_width=True, help="删除现有数据库并重新预填"):
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
            seed_all()
            st.success("数据库已重置并预填完成！")
            st.rerun()

    st.divider()

    st.subheader("📥 数据同步")
    if st.button("🌐 从OpenRouter获取最新排名", use_container_width=True):
        with st.spinner("正在获取OpenRouter数据..."):
            results = auto_fetch_all()
            if results.get("openrouter", {}).get("status") == "success":
                st.success(f"成功获取 {results['openrouter']['model_count']} 个模型数据")
            else:
                st.warning("获取失败，请检查网络连接")

    st.divider()

    st.subheader("📊 信号检测")
    if st.button("🔍 运行信号检测", use_container_width=True):
        with st.spinner("正在检测见顶信号..."):
            triggered = check_all_signals()
            if triggered:
                st.warning(f"检测到 {len(triggered)} 个触发信号！")
            else:
                st.success("当前无触发信号")

    st.divider()

    st.subheader("📤 CSV 导入导出")

    uploaded_file = st.file_uploader("导入 CSV 文件", type=["csv"], key="csv_import")
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            result = import_data_points_from_csv(tmp_path)
            if result.get("success"):
                st.success(f"导入成功: {result['imported']} 条数据 (跳过: {result['skipped']})")
                if result.get("errors"):
                    with st.expander("查看导入警告"):
                        for err in result["errors"]:
                            st.warning(err)
            else:
                st.error(f"导入失败: {result.get('error', '未知错误')}")
        finally:
            os.unlink(tmp_path)

    st.divider()
    st.subheader("📋 导出工具")

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("📊 导出全部数据", use_container_width=True):
            tmp_path = os.path.join(tempfile.gettempdir(), f"ai_all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            export_all_data_to_csv(tmp_path)
            st.success(f"已导出: {tmp_path}")
            with open(tmp_path, "r") as f:
                st.download_button(
                    "下载数据 CSV", f.read(),
                    f"ai_all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv", key="download_all_data"
                )

    with col_exp2:
        if st.button("📋 导出指标定义", use_container_width=True):
            tmp_path = os.path.join(tempfile.gettempdir(), f"ai_indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            export_indicators_to_csv(tmp_path)
            st.success(f"已导出: {tmp_path}")
            with open(tmp_path, "r") as f:
                st.download_button(
                    "下载指标 CSV", f.read(),
                    f"ai_indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv", key="download_indicators"
                )

    col_exp3, col_exp4 = st.columns(2)
    with col_exp3:
        if st.button("🚨 导出信号事件", use_container_width=True):
            tmp_path = os.path.join(tempfile.gettempdir(), f"ai_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            export_signals_to_csv(tmp_path)
            st.success(f"已导出: {tmp_path}")
            with open(tmp_path, "r") as f:
                st.download_button(
                    "下载信号 CSV", f.read(),
                    f"ai_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv", key="download_signals"
                )

    with col_exp4:
        if st.button("📝 生成导入模板", use_container_width=True):
            template_path = os.path.join(tempfile.gettempdir(), "ai_import_template.csv")
            generate_template_csv(template_path, "data_points")
            with open(template_path, "r") as f:
                st.download_button(
                    "下载模板 CSV", f.read(),
                    "ai_import_template.csv",
                    "text/csv", key="download_template"
                )

    st.divider()
    st.markdown("**框架版本**: 增强版 2.0 | **更新**: 2026-07-29")


# ============ 通用辅助函数 ============
def get_category_indicators(category):
    return [i for i in db.get_indicators() if i["category"] == category]


def create_kpi_card(title, value, delta=None, color="#1a73e8", help_text=""):
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {color};">
        <div style="color: #5f6368; font-size: 0.9rem;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: bold; color: {color};">{value}</div>
        {f'<div style="color: #5f6368; font-size: 0.8rem;">{delta}</div>' if delta else ''}
        {f'<div style="color: #80868b; font-size: 0.75rem;">💡 {help_text}</div>' if help_text else ''}
    </div>
    """, unsafe_allow_html=True)


def get_severity_emoji(level):
    return {"领先": "🔴", "同步": "🟠", "滞后": "🟡"}.get(level, "⚪")


# ============ 核心渲染函数 ============
def render_indicator_chart(indicator, height=360):
    """渲染单个指标折线图：折线+标记点+趋势线+拐点标注"""
    dps = db.get_data_points(indicator["id"])
    if not dps:
        return None

    df = pd.DataFrame(dps)
    cat_color = CATEGORY_COLORS.get(indicator["category"], "#1a73e8")
    unit = indicator.get("unit", "")

    fig = go.Figure()

    mode = "lines+markers" if len(df) >= 2 else "markers"
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["value"],
        mode=mode,
        name=indicator["name"],
        marker=dict(size=7, color=cat_color),
        line=dict(width=2, color=cat_color),
        hovertemplate="<b>%{y}</b><br>%{x}<extra></extra>",
    ))

    if len(df) >= 2:
        trend = analyze_trend(indicator["id"])
        if trend.get("slope") is not None:
            x_numeric = list(range(len(df)))
            slope = trend["slope"]
            intercept = df["value"].iloc[0]
            trend_y = [intercept + slope * x for x in x_numeric]
            fig.add_trace(go.Scatter(
                x=df["date"], y=trend_y,
                mode="lines",
                name="趋势线",
                line=dict(dash="dash", color="rgba(128,128,128,0.6)", width=1),
                hoverinfo="skip",
            ))

        inflection = detect_inflection_points(indicator["id"])
        for ip in inflection.get("inflection_points", []):
            ip_color = COLOR_PALETTE["danger"] if ip["type"] == "上拐点" else COLOR_PALETTE["success"]
            fig.add_vline(
                x=ip["date"],
                line_dash="dot",
                line_color=ip_color,
                line_width=1.5,
                annotation_text=f"{ip['type']}",
                annotation_position="top",
                annotation_font_size=10,
            )

    fig.update_layout(
        title=dict(text=f"{indicator['name']} ({unit})", font=dict(size=14)),
        height=height,
        margin=dict(l=50, r=20, t=50, b=40),
        showlegend=False,
        xaxis_title="日期",
        yaxis_title=unit,
    )
    return fig


def render_category_charts(category, cols=2):
    """渲染某分类下所有指标的子图网格（折线+标记+趋势线）"""
    indicators = get_category_indicators(category)
    with_data = [ind for ind in indicators if db.get_data_points(ind["id"])]

    if not with_data:
        st.info(f"「{category}」暂无数据")
        return

    n = len(with_data)
    rows = math.ceil(n / cols)
    cat_color = CATEGORY_COLORS.get(category, "#1a73e8")

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=[ind["name"] for ind in with_data],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    for idx, ind in enumerate(with_data):
        row, col = idx // cols + 1, idx % cols + 1
        dps = db.get_data_points(ind["id"])
        df = pd.DataFrame(dps)

        mode = "lines+markers" if len(df) >= 2 else "markers"
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"],
            mode=mode,
            name=ind["name"],
            line=dict(color=cat_color, width=2),
            marker=dict(size=3),
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>%{x}<extra></extra>",
        ), row=row, col=col)

        if len(df) >= 2:
            trend = analyze_trend(ind["id"])
            if trend.get("slope") is not None:
                x_num = list(range(len(df)))
                slope = trend["slope"]
                intercept = df["value"].iloc[0]
                t_y = [intercept + slope * x for x in x_num]
                fig.add_trace(go.Scatter(
                    x=df["date"], y=t_y,
                    mode="lines",
                    line=dict(dash="dash", color="rgba(128,128,128,0.5)", width=1),
                    showlegend=False,
                    hoverinfo="skip",
                ), row=row, col=col)

    fig.update_layout(
        height=max(320, rows * 260),
        showlegend=False,
        margin=dict(l=50, r=20, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_category_charts_for_list(indicators, cols=2):
    """渲染一组指标的子图网格（按列表传入，支持子分类筛选后的子集）"""
    with_data = [ind for ind in indicators if db.get_data_points(ind["id"])]

    if not with_data:
        st.info("暂无数据")
        return

    n = len(with_data)
    rows = math.ceil(n / cols)
    if with_data:
        cat_color = CATEGORY_COLORS.get(with_data[0]["category"], "#1a73e8")
    else:
        cat_color = "#1a73e8"

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=[ind["name"] for ind in with_data],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    for idx, ind in enumerate(with_data):
        row, col = idx // cols + 1, idx % cols + 1
        dps = db.get_data_points(ind["id"])
        df = pd.DataFrame(dps)

        mode = "lines+markers" if len(df) >= 2 else "markers"
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"],
            mode=mode,
            name=ind["name"],
            line=dict(color=cat_color, width=2),
            marker=dict(size=3),
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>%{x}<extra></extra>",
        ), row=row, col=col)

        if len(df) >= 2:
            trend = analyze_trend(ind["id"])
            if trend.get("slope") is not None:
                x_num = list(range(len(df)))
                slope = trend["slope"]
                intercept = df["value"].iloc[0]
                t_y = [intercept + slope * x for x in x_num]
                fig.add_trace(go.Scatter(
                    x=df["date"], y=t_y,
                    mode="lines",
                    line=dict(dash="dash", color="rgba(128,128,128,0.5)", width=1),
                    showlegend=False,
                    hoverinfo="skip",
                ), row=row, col=col)

    fig.update_layout(
        height=max(320, rows * 260),
        showlegend=False,
        margin=dict(l=50, r=20, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_trend_matrix(category_filter=None, normalize=False):
    """渲染趋势矩阵：所有指标缩略图"""
    indicators = db.get_indicators()
    if category_filter:
        indicators = [ind for ind in indicators if ind["category"] in category_filter]

    rows = []
    for ind in indicators:
        dps = db.get_data_points(ind["id"])
        if not dps:
            continue
        for dp in dps:
            val = dp["value"]
            if normalize and dps[0]["value"] != 0:
                val = val / dps[0]["value"] * 100
            rows.append({
                "日期": dp["date"],
                "数值": val,
                "指标": ind["name"],
                "分类": ind["category"],
            })

    if not rows:
        st.info("暂无数据")
        return

    df_all = pd.DataFrame(rows)
    n_indicators = df_all["指标"].nunique()
    wrap = 6 if n_indicators > 20 else (5 if n_indicators > 10 else 4)

    fig = px.line(
        df_all, x="日期", y="数值",
        facet_col="指标", facet_col_wrap=wrap,
        markers=True,
        height=max(600, math.ceil(n_indicators / wrap) * 220),
    )
    fig.for_each_annotation(lambda a: a.update(
        text=a.text.split("=")[-1],
        font=dict(size=10),
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(l=40, r=20, t=30, b=30),
    )
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    st.plotly_chart(fig, use_container_width=True)


# ============ 主内容 ============
tab_overview, tab_signals, tab_matrix, tab_coding, tab_supply, tab_demand, tab_users, tab_enterprise, tab_capital, tab_oss, tab_data = st.tabs([
    "🏠 概览",
    "🚨 见顶信号",
    "📈 趋势矩阵",
    "💻 Coding渗透",
    "⚙ 供给端",
    "📊 需求端",
    "👥 用户渗透",
    "🏢 企业渗透",
    "💰 资本融资",
    "🌍 开源生态",
    "📋 数据管理",
])


# ============ Tab 1: 概览 ============
with tab_overview:
    st.title("🤖 全球 AI 产业跟踪框架")
    st.markdown("---")

    col_health1, col_health2 = st.columns(2)
    with col_health1:
        health = compute_health_score()
        score_color = COLOR_PALETTE["success"] if health["score"] >= 70 else (
            COLOR_PALETTE["warning"] if health["score"] >= 40 else COLOR_PALETTE["danger"]
        )
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, {score_color} 0%, #764ba2 100%);">
            <div style="font-size: 1rem; opacity: 0.9;">基础健康度</div>
            <div style="font-size: 3rem; font-weight: bold;">{health['score']}/100</div>
            <div style="font-size: 1.2rem;">{health['emoji']} {health['status']}</div>
        </div>
        """, unsafe_allow_html=True)

        hcol1, hcol2, hcol3 = st.columns(3)
        with hcol1:
            create_kpi_card("🟢 领先信号", health["leading_signals"], color=COLOR_PALETTE["danger"])
        with hcol2:
            create_kpi_card("🟡 同步信号", health["sync_signals"], color=COLOR_PALETTE["warning"])
        with hcol3:
            create_kpi_card("🔴 滞后信号", health["lagging_signals"], color=COLOR_PALETTE["info"])

    with col_health2:
        weighted = compute_weighted_health_score()
        w_score_color = COLOR_PALETTE["success"] if weighted["score"] >= 70 else (
            COLOR_PALETTE["warning"] if weighted["score"] >= 40 else COLOR_PALETTE["danger"]
        )
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, {w_score_color} 0%, #4a90d9 100%);">
            <div style="font-size: 1rem; opacity: 0.9;">加权健康度（按板块权重）</div>
            <div style="font-size: 3rem; font-weight: bold;">{weighted['score']}/100</div>
            <div style="font-size: 1.2rem;">{weighted['emoji']} {weighted['status']}</div>
        </div>
        """, unsafe_allow_html=True)

        wcol1, wcol2 = st.columns(2)
        with wcol1:
            create_kpi_card("总扣分", f"{weighted['total_penalty']:.1f}", color=COLOR_PALETTE["danger"])
        with wcol2:
            create_kpi_card("活跃信号", weighted["active_signal_count"], color=COLOR_PALETTE["warning"])

    st.markdown(f"### 💡 综合建议")
    st.info(f"**基础**: {health['recommendation']}")
    st.warning(f"**加权**: {weighted['recommendation']}")

    summary = db.get_data_summary()
    st.markdown("---")
    st.subheader("📊 数据统计")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        create_kpi_card("📋 追踪指标", summary["indicator_count"], color=COLOR_PALETTE["primary"])
    with sc2:
        create_kpi_card("📊 数据点数", summary["data_point_count"], color=COLOR_PALETTE["info"])
    with sc3:
        create_kpi_card("🚨 活跃信号", summary["active_signals"], color=COLOR_PALETTE["danger"])
    with sc4:
        indicators = db.get_indicators()
        total_dps = sum(len(db.get_data_points(ind["id"])) for ind in indicators)
        create_kpi_card("📈 平均点数/指标", f"{total_dps / max(1, len(indicators)):.1f}", color=COLOR_PALETTE["success"])

    # 板块 KPI 卡片
    st.markdown("---")
    st.subheader("🏭 板块 KPI 卡片")

    heatmap_data = generate_heatmap_data()
    if heatmap_data["category_stats"]:
        categories_grid = st.columns(4)
        for idx, (cat, stats) in enumerate(heatmap_data["category_stats"].items()):
            col_idx = idx % 4
            with categories_grid[col_idx]:
                avg_cr = stats["avg_change_rate"]
                card_color = COLOR_PALETTE["success"] if avg_cr > 0 else (
                    COLOR_PALETTE["danger"] if avg_cr < 0 else COLOR_PALETTE["warning"]
                )
                breadth_pct = stats["breadth"]
                st.markdown(f"""
                <div class="kpi-card" style="border-left-color: {CATEGORY_COLORS.get(cat, COLOR_PALETTE['primary'])};">
                    <div style="color: #202124; font-weight: bold; font-size: 1rem;">{cat}</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {card_color};">{avg_cr:+.1f}%</div>
                    <div style="color: #5f6368; font-size: 0.85rem;">
                        广度 {breadth_pct:.0f}% ({stats['up_count']}↑/{stats['down_count']}↓/{stats['flat_count']}→)
                    </div>
                    <div style="color: #80868b; font-size: 0.75rem;">{stats['total']} 个指标</div>
                </div>
                """, unsafe_allow_html=True)

    # 板块热力图
    st.markdown("---")
    st.subheader("🌡 板块热力图 — 各指标变化率")

    if heatmap_data["cells"]:
        hm_col1, hm_col2 = st.columns([3, 2])

        with hm_col1:
            cells = heatmap_data["cells"]
            categories_order = list(heatmap_data["category_stats"].keys())

            z_values, text_values = [], []
            for cat in categories_order:
                cat_cells = [c for c in cells if c["category"] == cat]
                row_z, row_text = [], []
                for c in cat_cells:
                    row_z.append(c["change_rate"])
                    row_text.append(f"{c['change_rate']:+.1f}%")
                if row_z:
                    z_values.append(row_z)
                    text_values.append(row_text)

            if z_values:
                max_len = max(len(row) for row in z_values)
                z_padded = [row + [None] * (max_len - len(row)) for row in z_values]
                text_padded = [row + [""] * (max_len - len(row)) for row in text_values]

                flat_z, flat_text, flat_y, flat_x = [], [], [], []
                for y_idx, row in enumerate(z_padded):
                    for x_idx, val in enumerate(row):
                        if val is not None:
                            flat_z.append(val)
                            flat_text.append(text_padded[y_idx][x_idx])
                            flat_y.append(categories_order[y_idx])

                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=flat_z,
                    x=list(range(len(flat_z))),
                    y=flat_y,
                    text=flat_text,
                    texttemplate="%{text}",
                    textfont={"size": 11},
                    colorscale=[
                        [0, COLOR_PALETTE["danger"]],
                        [0.5, COLOR_PALETTE["warning"]],
                        [1, COLOR_PALETTE["success"]],
                    ],
                    zmid=0,
                    colorbar=dict(title="变化率(%)", thickness=15),
                    showscale=True,
                ))

                x_labels_all = []
                for cat in categories_order:
                    for c in cells:
                        if c["category"] == cat:
                            x_labels_all.append(c["indicator_name"][:12])

                fig_heatmap.update_layout(
                    title="指标变化率热力图",
                    height=max(400, len(categories_order) * 80),
                    xaxis=dict(
                        tickvals=list(range(len(x_labels_all))),
                        ticktext=x_labels_all,
                        tickangle=45,
                        tickfont=dict(size=9),
                    ),
                    yaxis=dict(tickfont=dict(size=11)),
                    margin=dict(l=100, r=20, t=40, b=100),
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

        with hm_col2:
            st.markdown("#### 📊 板块汇总")
            summary_data = []
            for cat, stats in sorted(heatmap_data["category_stats"].items(),
                                     key=lambda x: x[1]["avg_change_rate"], reverse=True):
                summary_data.append({
                    "板块": cat,
                    "指标数": stats["total"],
                    "平均变化率": f"{stats['avg_change_rate']:+.1f}%",
                    "广度": f"{stats['breadth']:.0f}%",
                    "上涨": stats["up_count"],
                    "下跌": stats["down_count"],
                })
            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # 动量排名
    st.markdown("---")
    st.subheader("⚡ 动量排名 TOP 15")

    momentum_list = compute_all_momentum(window=3)
    if momentum_list:
        momentum_list.sort(key=lambda x: abs(x.get("pct_change") or 0), reverse=True)

        mom_data = []
        for rank, m in enumerate(momentum_list[:15], 1):
            pct = f"{m['pct_change']:+.1f}%" if m['pct_change'] is not None else "N/A"
            roc = f"{m['roc']:+.1f}%" if m.get("roc") is not None else "N/A"
            direction_icon = "🚀" if "加速上升" in m.get("direction", "") else (
                "📉" if "加速下降" in m.get("direction", "") else "➡️"
            )
            mom_data.append({
                "排名": rank,
                "指标": m["indicator_name"][:25],
                "变化率": pct,
                "ROC": roc,
                "方向": f"{direction_icon} {m.get('direction', 'N/A')}",
            })

        df_mom = pd.DataFrame(mom_data)
        st.dataframe(df_mom, use_container_width=True, hide_index=True)

        fig_mom = go.Figure()
        colors_mom = [COLOR_PALETTE["success"] if m.get("pct_change", 0) > 0 else COLOR_PALETTE["danger"]
                       for m in momentum_list[:15]]
        fig_mom.add_trace(go.Bar(
            x=[m["indicator_name"][:20] for m in momentum_list[:15]],
            y=[m.get("pct_change", 0) or 0 for m in momentum_list[:15]],
            marker_color=colors_mom,
            text=[f"{m['pct_change']:+.1f}%" if m.get("pct_change") is not None else "N/A"
                  for m in momentum_list[:15]],
            textposition="outside",
        ))
        fig_mom.update_layout(
            title="动量 TOP 15 柱状图",
            height=400,
            xaxis=dict(tickangle=45, tickfont=dict(size=10)),
            yaxis=dict(title="变化率 (%)"),
            margin=dict(l=50, r=20, t=40, b=80),
        )
        st.plotly_chart(fig_mom, use_container_width=True)

    # 拐点检测摘要
    st.markdown("---")
    st.subheader("🔄 拐点检测摘要")

    inflections = detect_all_inflections()
    inflection_with_points = [i for i in inflections if i["inflection_count"] > 0]
    inflection_with_points.sort(key=lambda x: x["inflection_count"], reverse=True)

    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.markdown("**检测到拐点的指标**")
        if inflection_with_points:
            for info in inflection_with_points[:5]:
                latest_ip = info["inflection_points"][-1]
                icon = "🔼" if latest_ip["type"] == "上拐点" else "🔽"
                st.markdown(f"- {icon} **{info['indicator_name']}**: {info['inflection_count']}个拐点, 最新{latest_ip['type']}({latest_ip['date']})")
        else:
            st.info("暂未检测到明显拐点")

    with col_inf2:
        st.markdown("**当前阶段分布**")
        phase_counts = {}
        for info in inflections:
            phase = info.get("phase_detail", "未知")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        if phase_counts:
            fig_phase = go.Figure(data=[go.Pie(
                labels=list(phase_counts.keys()),
                values=list(phase_counts.values()),
                hole=0.4,
            )])
            fig_phase.update_layout(title="当前阶段分布", height=300)
            st.plotly_chart(fig_phase, use_container_width=True)

    # 最新触发信号
    st.markdown("---")
    st.subheader("🚨 最新信号事件")
    active_events = db.get_signal_events(is_resolved=False)
    if active_events:
        for event in active_events[:5]:
            level_emoji = get_severity_emoji(event.get("level", ""))
            with st.expander(f"{level_emoji} [{event.get('level', '-')}] {event.get('rule_name', '-')} - {event.get('trigger_date', '-')}"):
                st.write(f"**指标**: {event.get('indicator_name', '-')}")
                st.write(f"**触发值**: {event.get('trigger_value', '-')}")
                st.write(f"**说明**: {event.get('notes', '-')}")
    else:
        st.success("✅ 当前无活跃信号事件")

    # 中游数据代理 折线图
    st.markdown("---")
    st.subheader("📡 中游数据代理 — 趋势图")
    mid_indicators = get_category_indicators("中游数据代理")
    if mid_indicators:
        render_category_charts("中游数据代理", cols=3)

    # 完整报告
    st.markdown("---")
    st.subheader("📄 完整分析报告")
    col_rpt1, col_rpt2 = st.columns(2)
    with col_rpt1:
        if st.button("生成标准分析报告", use_container_width=True):
            report = generate_analysis_report()
            st.text(report)
            st.download_button(
                "下载标准报告", report,
                f"ai_industry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "text/plain",
            )
    with col_rpt2:
        if st.button("生成完整增强报告", use_container_width=True):
            full_report = generate_full_report()
            st.text(full_report)
            st.download_button(
                "下载完整报告", full_report,
                f"ai_full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "text/plain",
            )


# ============ Tab 2: 见顶信号 ============
with tab_signals:
    st.title("🚨 见顶信号体系")
    st.markdown("""
    > 框架第十节：按信号敏感度分层追踪。
    > - **领先信号**: Capex下修、ASIC侵蚀、ROIC预警、Coding饱和、ARR增速放缓
    > - **同步信号**: 折旧墙、NRR下行、API涨价、Token增速放缓
    > - **滞后信号**: ROI质疑、Capex下降、裁员
    """)

    st.subheader("📊 信号严重度分布")
    summary = get_signal_summary()
    col_sev1, col_sev2 = st.columns(2)

    with col_sev1:
        severity_data = {
            "等级": ["领先 (危险)", "同步 (警告)", "滞后 (信息)"],
            "数量": [summary["by_level"].get("领先", 0),
                     summary["by_level"].get("同步", 0),
                     summary["by_level"].get("滞后", 0)],
            "颜色": [COLOR_PALETTE["danger"], COLOR_PALETTE["warning"], COLOR_PALETTE["info"]]
        }
        df_severity = pd.DataFrame(severity_data)
        fig_pie = go.Figure(data=[go.Pie(
            labels=df_severity["等级"],
            values=df_severity["数量"],
            marker_colors=df_severity["颜色"],
            hole=0.4,
            textinfo="label+percent+value",
        )])
        fig_pie.update_layout(title="信号等级分布", height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_sev2:
        st.markdown("**信号事件时间线**")
        all_events = db.get_signal_events()
        if all_events:
            timeline_data = []
            for evt in all_events[-20:]:
                timeline_data.append({
                    "日期": evt.get("trigger_date", ""),
                    "等级": evt.get("level", ""),
                    "规则": evt.get("rule_name", ""),
                    "状态": "已解决" if evt.get("is_resolved") else "活跃",
                })
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data).sort_values("日期", ascending=False)
                fig_timeline = go.Figure(data=[
                    go.Scatter(
                        x=df_timeline["日期"],
                        y=[idx] * len(df_timeline),
                        mode="markers+text",
                        text=[f"{r}<br>{lvl}" for r, lvl in zip(df_timeline["规则"], df_timeline["等级"])],
                        textposition="top center",
                        marker=dict(
                            size=15,
                            color=[COLOR_PALETTE["danger"] if l == "领先" else
                                   (COLOR_PALETTE["warning"] if l == "同步" else COLOR_PALETTE["info"])
                                   for l in df_timeline["等级"]],
                        ),
                        hovertemplate="<b>%{text}</b><br>日期: %{x}<extra></extra>",
                    )
                ])
                fig_timeline.update_layout(
                    title="最近信号事件时间线",
                    height=350,
                    yaxis=dict(showticklabels=False, showgrid=False),
                    xaxis=dict(title="日期"),
                    margin=dict(l=20, r=20, t=40, b=40),
                )
                st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 信号规则定义")
    rules = db.get_signal_rules()
    if rules:
        rules_data = []
        for r in rules:
            indicator_name = ""
            if r.get("indicator_id"):
                ind = db.get_indicator_by_id(r["indicator_id"])
                indicator_name = ind["name"] if ind else ""
            rules_data.append({
                "层级": r["level"],
                "规则名称": r["rule_name"],
                "关联指标": indicator_name,
                "阈值": r.get("threshold", "-"),
                "条件": r.get("comparison", "-"),
                "描述": r.get("rule_description", ""),
            })
        df_rules = pd.DataFrame(rules_data)
        st.dataframe(df_rules, use_container_width=True, hide_index=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 已触发信号")
        triggered = check_all_signals()
        if triggered:
            for sig in triggered:
                level_color = COLOR_PALETTE["danger"] if sig["level"] == "领先" else (
                    COLOR_PALETTE["warning"] if sig["level"] == "同步" else COLOR_PALETTE["info"]
                )
                with st.expander(f"{get_severity_emoji(sig['level'])} [{sig['level']}] {sig['rule_name']}"):
                    st.markdown(f"""
                    <div class="kpi-card" style="border-left-color: {level_color};">
                        <div><b>指标</b>: {sig['indicator_name']}</div>
                        <div><b>当前值</b>: {sig['trigger_value']}</div>
                        <div><b>阈值</b>: {sig['threshold']} ({sig['comparison']})</div>
                        <div><b>描述</b>: {sig['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("暂无触发信号")

    with col2:
        st.subheader("📋 活跃信号事件")
        active_events = db.get_signal_events(is_resolved=False)
        if active_events:
            for event in active_events:
                with st.expander(f"{get_severity_emoji(event.get('level', ''))} [{event.get('level', '-')}] {event.get('rule_name', '-')}"):
                    st.write(f"**触发日期**: {event.get('trigger_date', '-')}")
                    st.write(f"**指标**: {event.get('indicator_name', '-')}")
                    st.write(f"**触发值**: {event.get('trigger_value', '-')}")
                    if st.button(f"标记为已解决 #{event['id']}", key=f"resolve_{event['id']}"):
                        db.resolve_signal_event(event['id'])
                        st.rerun()
        else:
            st.success("✅ 无活跃信号事件")

    st.markdown("---")
    st.subheader("📊 信号层级汇总")
    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
    with col_sum1:
        create_kpi_card("总事件数", summary["total_events"], color=COLOR_PALETTE["primary"])
    with col_sum2:
        create_kpi_card("未解决", summary["unresolved"], color=COLOR_PALETTE["danger"])
    with col_sum3:
        create_kpi_card("已解决", summary["resolved"], color=COLOR_PALETTE["success"])
    with col_sum4:
        create_kpi_card("领先/同步/滞后",
                        f"{summary['by_level']['领先']}/{summary['by_level']['同步']}/{summary['by_level']['滞后']}",
                        color=COLOR_PALETTE["warning"])


# ============ Tab 3: 趋势矩阵 ============
with tab_matrix:
    st.title("📈 趋势矩阵 — 全部指标缩略图")
    st.markdown("""
    > 以分面图（facet plot）方式展示全部指标的时间序列趋势。
    > 可按分类筛选，支持归一化（基准化到100）以便跨指标对比。
    """)

    all_categories = sorted(set(ind["category"] for ind in db.get_indicators()))
    sel_cats = st.multiselect("🔍 按分类筛选（可多选，默认全选）", all_categories, default=all_categories, key="matrix_cat")
    norm_on = st.checkbox("📊 归一化（基准=100）", value=False, key="matrix_norm",
                          help="将每个指标的首个数据点设为100，便于跨指标趋势对比")

    render_trend_matrix(category_filter=sel_cats, normalize=norm_on)


# ============ Tab 4: Coding渗透 ============
with tab_coding:
    st.title("💻 Coding 渗透率（核心模块）")
    st.markdown("""
    > 框架第七节：判断 AI Coding 是否接近饱和，对整体 ARR 增长至关重要。
    > **核心逻辑链**：用户数饱和已出现（Copilot停滞），ARR增速放缓已出现（Anthropic 51%→8%），
    > Coding 对 ARR 拉动正在减速——从指数增长转入线性增长。
    """)

    coding_indicators = get_category_indicators("Coding渗透")
    for sub_cat in sorted(set(ind.get("sub_category", "") for ind in coding_indicators)):
        sub_inds = [ind for ind in coding_indicators if ind.get("sub_category", "") == sub_cat]
        if sub_inds:
            st.subheader(f"▸ {sub_cat}")
            render_category_charts_for_list(sub_inds, cols=2)

    st.markdown("---")
    st.subheader("⚠ Coding 减速信号")
    st.error("""
    **核心逻辑链**:
    1. ✅ **用户数饱和**: Copilot 增长已 stalled，4.7M 付费但增速停滞
    2. ✅ **ARR 增速放缓**: Anthropic 月度增速从 51% 降至 8%
    3. ⚠ **Coding 占比下降**: Claude 端 coding 占比 40% → 34%
    4. 💡 **结论**: Coding 对 ARR 拉动正在减速——从指数增长转入线性增长
    """)


# ============ Tab 5: 供给端 ============
with tab_supply:
    st.title("⚙ 供给端跟踪")
    st.markdown("""
    > 框架第二节：上游硬件、物理瓶颈、云基础设施供给。
    > **关键信号**: ASIC侵蚀率上升 + 英伟达毛利率触顶 = 硬件股见顶最强领先信号
    """)

    supply_indicators = get_category_indicators("供给端")
    for sub_cat in sorted(set(ind.get("sub_category", "") for ind in supply_indicators)):
        sub_inds = [ind for ind in supply_indicators if ind.get("sub_category", "") == sub_cat]
        if sub_inds:
            st.subheader(f"▸ {sub_cat}")
            render_category_charts_for_list(sub_inds, cols=3)


# ============ Tab 6: 需求端 ============
with tab_demand:
    st.title("📊 需求端与竞争格局")
    st.markdown("""
    > 框架第三节：企业采购强度与云厂商服务增速。
    > **关键代理**: Azure OpenAI / Google Cloud AI / AWS Bedrock 增速
    """)

    demand_indicators = get_category_indicators("需求端")
    if demand_indicators:
        render_category_charts_for_list(demand_indicators, cols=2)


# ============ Tab 7: 用户渗透 ============
with tab_users:
    st.title("👥 个人用户渗透率")
    st.markdown("""
    > 框架第四节：人口渗透（存量广度）与粘性变现。
    > **关键基准**: DAU/MAU 社交类 50-65%，工具类 20-40%，<20% 为猎奇尝鲜型
    """)

    mau_indicators = [ind for ind in get_category_indicators("个人用户渗透") if "MAU" in ind["name"]]
    other_indicators = [ind for ind in get_category_indicators("个人用户渗透") if "MAU" not in ind["name"]]

    if mau_indicators:
        st.subheader("▸ 主要产品 MAU 趋势（折线图）")
        render_category_charts_for_list(mau_indicators, cols=3)

    if other_indicators:
        st.subheader("▸ 粘性与变现指标")
        render_category_charts_for_list(other_indicators, cols=2)


# ============ Tab 8: 企业渗透 ============
with tab_enterprise:
    st.title("🏢 企业用户渗透率与 Agent 落地")
    st.markdown("""
    > 框架第五节：企业渗透广度/深度与 Agent 落地可靠性。
    > **关键基准**: 座席利用率 >70%，NRR >100%
    """)

    ent_indicators = get_category_indicators("企业用户渗透")
    for sub_cat in sorted(set(ind.get("sub_category", "") for ind in ent_indicators)):
        sub_inds = [ind for ind in ent_indicators if ind.get("sub_category", "") == sub_cat]
        if sub_inds:
            st.subheader(f"▸ {sub_cat}")
            render_category_charts_for_list(sub_inds, cols=3)

    st.markdown("---")
    st.subheader("⚠ 非 Coding 场景接力判断（框架第八节）")
    nc_indicators = get_category_indicators("非Coding渗透")
    if nc_indicators:
        for sub_cat in sorted(set(ind.get("sub_category", "") for ind in nc_indicators)):
            sub_inds = [ind for ind in nc_indicators if ind.get("sub_category", "") == sub_cat]
            if sub_inds:
                st.markdown(f"**{sub_cat}**")
                render_category_charts_for_list(sub_inds, cols=3)


# ============ Tab 9: 资本融资 ============
with tab_capital:
    st.title("💰 资本与融资健康度")
    st.markdown("""
    > 框架第六节：私募信贷、Neocloud、GPU 抵押贷款。
    > **关键风险**: GPU生命周期(~7年) vs 数据中心设施寿命(20-30年)错配敞口
    """)

    capital_indicators = get_category_indicators("资本与融资")
    if capital_indicators:
        render_category_charts_for_list(capital_indicators, cols=3)


# ============ Tab 10: 开源生态 ============
with tab_oss:
    st.title("🌍 开源与开发者生态")
    st.markdown("""
    > 开源生态是 AI 产业的"温度计"——开源活跃度直接反映开发者信心与创新节奏。
    > **关键信号**: GitHub Trending 周度创新高 = 开发者热情；Stars 增速放缓 = 成熟饱和
    """)

    oss_indicators = get_category_indicators("开源生态")
    if oss_indicators:
        render_category_charts_for_list(oss_indicators, cols=2)


# ============ Tab 11: 数据管理 ============
with tab_data:
    st.title("📋 数据管理中心")

    st.subheader("➕ 添加数据点")
    indicators = db.get_indicators()

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_indicator = st.selectbox(
            "选择指标",
            options=[(ind["id"], f"[{ind['category']}] {ind['name']}") for ind in indicators],
            format_func=lambda x: x[1],
            key="add_indicator_select"
        )
    with col2:
        data_date = st.date_input("日期", value=datetime.now(), key="add_data_date")

    col3, col4 = st.columns([1, 2])
    with col3:
        data_value = st.number_input("数值", value=0.0, key="add_data_value")
    with col4:
        data_notes = st.text_input("备注", key="add_data_notes")

    if st.button("添加数据点", key="add_data_btn"):
        ind_id = selected_indicator[0] if isinstance(selected_indicator, tuple) else selected_indicator
        db.add_data_point(
            indicator_id=ind_id,
            date=data_date.strftime("%Y-%m-%d"),
            value=data_value,
            notes=data_notes
        )
        st.success(f"✓ 数据点已添加: {selected_indicator[1] if isinstance(selected_indicator, tuple) else selected_indicator} @ {data_date}")
        st.rerun()

    st.markdown("---")

    st.subheader("📤 CSV 批量导入导出")
    col_csv1, col_csv2 = st.columns(2)
    with col_csv1:
        st.markdown("**📥 导入数据**")
        import_file = st.file_uploader("上传 CSV 文件", type=["csv"], key="tab_csv_import")
        if import_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(import_file.getvalue())
                tmp_path = tmp.name
            try:
                result = import_data_points_from_csv(tmp_path)
                if result.get("success"):
                    st.success(f"导入成功: {result['imported']} 条 (跳过: {result['skipped']})")
                else:
                    st.error(f"导入失败: {result.get('error', '未知错误')}")
            finally:
                os.unlink(tmp_path)

        st.download_button(
            "📝 下载导入模板",
            pd.DataFrame(columns=["indicator_name", "date", "value", "source", "notes"]).to_csv(index=False),
            "ai_import_template.csv",
            "text/csv",
            key="download_template_btn"
        )

    with col_csv2:
        st.markdown("**📤 导出数据**")
        export_type = st.selectbox("导出类型", ["全部数据", "指标定义", "信号事件"], key="export_type")
        if st.button("生成导出文件", key="generate_export"):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if export_type == "全部数据":
                tmp_path = os.path.join(tempfile.gettempdir(), f"ai_all_{timestamp}.csv")
                export_all_data_to_csv(tmp_path)
                with open(tmp_path, "r") as f:
                    st.download_button("下载全部数据", f.read(), f"ai_all_{timestamp}.csv", "text/csv", key="dl_all")
            elif export_type == "指标定义":
                tmp_path = os.path.join(tempfile.gettempdir(), f"ai_indicators_{timestamp}.csv")
                export_indicators_to_csv(tmp_path)
                with open(tmp_path, "r") as f:
                    st.download_button("下载指标定义", f.read(), f"ai_indicators_{timestamp}.csv", "text/csv", key="dl_ind")
            else:
                tmp_path = os.path.join(tempfile.gettempdir(), f"ai_signals_{timestamp}.csv")
                export_signals_to_csv(tmp_path)
                with open(tmp_path, "r") as f:
                    st.download_button("下载信号事件", f.read(), f"ai_signals_{timestamp}.csv", "text/csv", key="dl_sig")

    st.markdown("---")

    st.subheader("📋 指标定义")
    categories = ["中游数据代理", "供给端", "需求端", "个人用户渗透", "企业用户渗透", "资本与融资", "Coding渗透", "非Coding渗透"]
    selected_cat = st.multiselect("筛选分类", categories, default=categories)

    filtered = [i for i in indicators if i["category"] in selected_cat]
    table_data = []
    for ind in filtered:
        dps = db.get_data_points(ind["id"])
        latest = dps[-1] if dps else None
        trend = analyze_trend(ind["id"])
        table_data.append({
            "ID": ind["id"],
            "分类": ind["category"],
            "子分类": ind.get("sub_category", ""),
            "指标名称": ind["name"],
            "频率": ind["frequency"],
            "数据类型": ind["data_type"],
            "单位": ind.get("unit", ""),
            "自动化": ind.get("automation_level", ""),
            "数据源": ind.get("source", ""),
            "最新值": f"{latest['value']} ({latest['date']})" if latest else "N/A",
            "趋势": trend["trend"] if trend["trend"] != "insufficient_data" else "N/A",
            "变化率": f"{trend.get('change_rate_pct', 'N/A')}%" if trend.get('change_rate_pct') is not None else "N/A",
        })

    if table_data:
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        st.download_button("📥 导出指标定义 (CSV)", df_table.to_csv(index=False), "indicators.csv", "text/csv", key="dl_ind_table")
    else:
        st.info("没有符合条件的指标")

    st.markdown("---")

    st.subheader("📊 原始数据浏览")
    if st.button("显示所有数据点"):
        all_data = []
        for ind in indicators:
            dps = db.get_data_points(ind["id"])
            for dp in dps:
                all_data.append({
                    "指标": ind["name"],
                    "分类": ind["category"],
                    "日期": dp["date"],
                    "数值": dp["value"],
                    "备注": dp["notes"],
                })
        if all_data:
            df_all = pd.DataFrame(all_data)
            st.dataframe(df_all, use_container_width=True, hide_index=True)
            st.download_button("📥 导出所有数据 (CSV)", df_all.to_csv(index=False), "all_data.csv", "text/csv", key="dl_all_raw")


# ============ 页脚 ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 20px;">
    <p><strong>全球 AI 产业跟踪框架</strong> | 增强版 2.0</p>
    <p>基于《全球 AI 产业跟踪框架》最后版 | 用途：股票/产业研究</p>
    <p>判断 AI 产业发展所处阶段、供需关系、渗透率空间、见顶信号</p>
</div>
""", unsafe_allow_html=True)