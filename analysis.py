"""
增强版分析引擎：见顶信号检测、趋势分析、相关性、动量指标、拐点检测、
加权健康度评分、热力图数据生成、完整报告生成。
"""

import database as db
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import math


CATEGORY_WEIGHTS = {
    "供给端": 1.5,
    "需求端": 1.3,
    "资本与融资": 1.2,
    "中游数据代理": 1.1,
    "Coding渗透": 1.0,
    "非Coding渗透": 1.0,
    "个人用户渗透": 0.9,
    "企业用户渗透": 1.0,
}


# ============ 基础工具 ============

def _get_indicator_name(indicator_id: int) -> str:
    ind = db.get_indicator_by_id(indicator_id)
    return ind["name"] if ind else "Unknown"


def _map_severity(level: str) -> str:
    mapping = {"领先": "danger", "同步": "warning", "滞后": "info"}
    return mapping.get(level, "info")


def _extract_series(indicator_id: int) -> Tuple[List[str], List[float]]:
    dps = db.get_data_points(indicator_id)
    dates, values = [], []
    for dp in dps:
        if dp["value"] is not None:
            dates.append(dp["date"])
            values.append(float(dp["value"]))
    return dates, values


def _linear_regression(values: List[float]) -> Tuple[float, float]:
    n = len(values)
    if n < 2:
        return 0.0, 0.0
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
    den = sum((xi - x_mean) ** 2 for xi in x)
    slope = num / den if den != 0 else 0.0
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _pearson_correlation(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - x_mean) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - y_mean) ** 2 for yi in y))
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


# ============ 原有接口（保持向后兼容）============

def check_all_signals() -> List[Dict]:
    triggered = []
    rules = db.get_signal_rules()

    for rule in rules:
        indicator_id = rule.get("indicator_id")
        if not indicator_id:
            continue

        data_points = db.get_data_points(indicator_id)
        if len(data_points) < 1:
            continue

        latest = data_points[-1]
        latest_value = latest["value"]
        if latest_value is None:
            continue

        threshold = rule.get("threshold")
        comparison = rule.get("comparison", "below")
        is_triggered = False

        if threshold is not None:
            if comparison == "below" and latest_value <= threshold:
                is_triggered = True
            elif comparison == "above" and latest_value >= threshold:
                is_triggered = True

        if comparison == "change_rate" and len(data_points) >= 2:
            prev_value = data_points[-2]["value"]
            if prev_value and prev_value != 0:
                change_rate = (latest_value - prev_value) / prev_value * 100
                if threshold and abs(change_rate) >= threshold:
                    is_triggered = True

        if is_triggered:
            triggered.append({
                "rule_id": rule["id"],
                "rule_name": rule["rule_name"],
                "level": rule["level"],
                "indicator_id": indicator_id,
                "indicator_name": _get_indicator_name(indicator_id),
                "trigger_value": latest_value,
                "trigger_date": latest["date"],
                "severity": _map_severity(rule["level"]),
                "description": rule.get("rule_description", ""),
                "threshold": threshold,
                "comparison": comparison,
            })
            db.add_signal_event(
                rule_id=rule["id"],
                indicator_id=indicator_id,
                trigger_date=datetime.now().strftime("%Y-%m-%d"),
                trigger_value=latest_value,
                severity=_map_severity(rule["level"]),
                notes=f"自动检测触发: {rule['rule_name']}",
            )

    return triggered


def analyze_trend(indicator_id: int, window: int = 4) -> Dict:
    data = db.get_data_points(indicator_id)
    if len(data) < 2:
        return {"trend": "insufficient_data", "change_rate": None, "details": "数据点不足"}

    recent = data[-window:] if len(data) >= window else data
    values = [dp["value"] for dp in recent if dp["value"] is not None]
    dates = [dp["date"] for dp in recent if dp["value"] is not None]

    if len(values) < 2:
        return {"trend": "insufficient_data", "change_rate": None, "details": "有效数据点不足"}

    change_rate = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else None
    slope, _ = _linear_regression(values)

    if slope > 0:
        trend = "上升"
    elif slope < 0:
        trend = "下降"
    else:
        trend = "平稳"

    if len(values) >= 3:
        first_diff = [values[i+1] - values[i] for i in range(len(values)-1)]
        second_diff = [first_diff[i+1] - first_diff[i] for i in range(len(first_diff)-1)]
        avg_acceleration = sum(second_diff) / len(second_diff) if second_diff else 0
    else:
        avg_acceleration = 0

    return {
        "indicator_id": indicator_id,
        "indicator_name": _get_indicator_name(indicator_id),
        "trend": trend,
        "slope": round(slope, 4),
        "change_rate_pct": round(change_rate, 2) if change_rate else None,
        "acceleration": round(avg_acceleration, 4),
        "data_points_used": len(values),
        "date_range": f"{dates[0]} ~ {dates[-1]}",
        "details": f"斜率={slope:.4f}, 变化率={change_rate:.2f}%, 加速度={avg_acceleration:.4f}" if change_rate else "",
    }


def analyze_category_trends(category: str) -> List[Dict]:
    indicators = db.get_indicators(category=category)
    results = []
    for ind in indicators:
        trend = analyze_trend(ind["id"])
        if trend["trend"] != "insufficient_data":
            results.append(trend)
    return results


def compute_health_score() -> Dict:
    active_signals = db.get_signal_events(is_resolved=False)
    leading_count = sum(1 for s in active_signals if s.get("level") == "领先")
    sync_count = sum(1 for s in active_signals if s.get("level") == "同步")
    lagging_count = sum(1 for s in active_signals if s.get("level") == "滞后")

    penalty = leading_count * 30 + sync_count * 15 + lagging_count * 5
    score = max(0, 100 - penalty)

    if score >= 70:
        status, emoji = "健康", "🟢"
    elif score >= 40:
        status, emoji = "关注", "🟡"
    elif score >= 20:
        status, emoji = "预警", "🟠"
    else:
        status, emoji = "危险", "🔴"

    return {
        "score": score,
        "status": status,
        "emoji": emoji,
        "leading_signals": leading_count,
        "sync_signals": sync_count,
        "lagging_signals": lagging_count,
        "total_active": len(active_signals),
        "recommendation": _get_recommendation(score, leading_count, sync_count, lagging_count),
        "timestamp": datetime.now().isoformat(),
    }


def _get_recommendation(score: int, leading: int, sync: int, lagging: int) -> str:
    if score >= 70:
        return "产业整体健康，AI投资周期仍在扩张阶段。关注领先指标变化。"
    elif score >= 40:
        return "产业进入关注区间，部分领先信号已触发。建议降低新增敞口，密切跟踪同步信号。"
    elif score >= 20:
        return "产业面临明显调整压力，领先与同步信号大量触发。建议转向防御性头寸，准备应对滞后信号。"
    else:
        return "产业已进入衰退阶段，三类信号全面触发。建议减仓或做空，等待周期底部信号出现。"


def get_signal_summary() -> Dict:
    all_events = db.get_signal_events()
    by_level = {"领先": 0, "同步": 0, "滞后": 0}
    by_severity = {"danger": 0, "warning": 0, "info": 0}
    resolved = 0
    unresolved = 0

    for event in all_events:
        level = event.get("level", "未知")
        severity = event.get("severity", "info")
        if level in by_level:
            by_level[level] += 1
        if severity in by_severity:
            by_severity[severity] += 1
        if event.get("is_resolved"):
            resolved += 1
        else:
            unresolved += 1

    return {
        "total_events": len(all_events),
        "by_level": by_level,
        "by_severity": by_severity,
        "resolved": resolved,
        "unresolved": unresolved,
    }


def generate_analysis_report() -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("全球 AI 产业跟踪分析报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    health = compute_health_score()
    lines.append(f"\n{health['emoji']} 综合健康度: {health['score']}/100 ({health['status']})")
    lines.append(f"  领先信号: {health['leading_signals']} 个活跃")
    lines.append(f"  同步信号: {health['sync_signals']} 个活跃")
    lines.append(f"  滞后信号: {health['lagging_signals']} 个活跃")
    lines.append(f"  建议: {health['recommendation']}")

    triggered = check_all_signals()
    if triggered:
        lines.append("\n⚠ 已触发的信号:")
        for sig in triggered:
            lines.append(f"  [{sig['level']}] {sig['rule_name']}: "
                        f"{sig['indicator_name']} = {sig['trigger_value']} "
                        f"(阈值: {sig['threshold']})")
    else:
        lines.append("\n✓ 当前无新触发信号")

    active = db.get_signal_events(is_resolved=False)
    if active:
        lines.append("\n📋 活跃信号事件:")
        for event in active:
            lines.append(f"  [{event.get('level', '-')}] {event.get('rule_name', '-')} "
                        f"- 触发于 {event.get('trigger_date', '-')}")

    lines.append("\n📈 分类趋势分析:")
    categories = ["Coding渗透", "供给端", "需求端", "个人用户渗透", "企业用户渗透", "非Coding渗透"]
    for cat in categories:
        trends = analyze_category_trends(cat)
        if trends:
            lines.append(f"\n  【{cat}】")
            for t in trends:
                if t["trend"] != "insufficient_data":
                    arrow = "↗" if t["trend"] == "上升" else ("↘" if t["trend"] == "下降" else "→")
                    cr = f" ({t['change_rate_pct']:+.1f}%)" if t['change_rate_pct'] is not None else ""
                    lines.append(f"    {arrow} {t['indicator_name']}: {t['trend']}{cr}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# ============ 一、相关性分析 ============

def compute_correlation_matrix(indicator_ids: Optional[List[int]] = None,
                              min_overlap: int = 3) -> Dict:
    """
    计算指标间 Pearson 相关系数矩阵。
    仅使用双方都有数据的时间点进行对齐。
    返回矩阵和摘要统计。
    """
    if indicator_ids is None:
        indicators = db.get_indicators()
        indicator_ids = [ind["id"] for ind in indicators]

    series_map = {}
    valid_ids = []
    for iid in indicator_ids:
        dates, values = _extract_series(iid)
        if len(values) >= min_overlap:
            series_map[iid] = {"dates": dates, "values": values}
            valid_ids.append(iid)

    n = len(valid_ids)
    corr_matrix = [[0.0] * n for _ in range(n)]
    indicator_names = [_get_indicator_name(iid) for iid in valid_ids]

    for i in range(n):
        corr_matrix[i][i] = 1.0
        for j in range(i + 1, n):
            si = series_map[valid_ids[i]]
            sj = series_map[valid_ids[j]]
            aligned_x, aligned_y = _align_by_date(si["dates"], si["values"],
                                                  sj["dates"], sj["values"])
            if len(aligned_x) >= min_overlap:
                r = _pearson_correlation(aligned_x, aligned_y)
                corr_matrix[i][j] = round(r, 4)
                corr_matrix[j][i] = round(r, 4)

    strong_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            r = corr_matrix[i][j]
            if abs(r) >= 0.7:
                strong_pairs.append({
                    "indicator_1": indicator_names[i],
                    "indicator_2": indicator_names[j],
                    "correlation": r,
                    "strength": "强正相关" if r > 0 else "强负相关",
                })

    strong_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    return {
        "indicator_names": indicator_names,
        "correlation_matrix": corr_matrix,
        "strong_pairs": strong_pairs,
        "indicator_count": n,
        "timestamp": datetime.now().isoformat(),
    }


def _align_by_date(dates1: List[str], values1: List[float],
                    dates2: List[str], values2: List[float]) -> Tuple[List[float], List[float]]:
    """按日期对齐两个时间序列，返回对齐后的值对。"""
    map1 = dict(zip(dates1, values1))
    map2 = dict(zip(dates2, values2))
    common_dates = sorted(set(dates1) & set(dates2))
    aligned_x = [map1[d] for d in common_dates]
    aligned_y = [map2[d] for d in common_dates]
    return aligned_x, aligned_y


# ============ 二、动量指标 ============

def compute_roc(indicator_id: int, period: int = 5) -> Optional[float]:
    """
    计算 ROC（Rate of Change，变动率指标）。
    ROC = (当前值 - N期前值) / N期前值 * 100
    """
    _, values = _extract_series(indicator_id)
    if len(values) <= period:
        return None
    current = values[-1]
    past = values[-1 - period]
    if past == 0:
        return None
    return round((current - past) / past * 100, 2)


def compute_momentum(indicator_id: int, window: int = 3) -> Dict:
    """
    计算完整动量指标：变化率、加速度、速度。
    """
    dates, values = _extract_series(indicator_id)
    if len(values) < window + 1:
        return {
            "indicator_id": indicator_id,
            "indicator_name": _get_indicator_name(indicator_id),
            "momentum": "insufficient_data",
        }

    recent = values[-(window + 1):]
    changes = [recent[i] - recent[i - 1] for i in range(1, len(recent))]
    velocities = changes

    if len(velocities) >= 2:
        accelerations = [velocities[i] - velocities[i - 1] for i in range(1, len(velocities))]
        avg_acceleration = sum(accelerations) / len(accelerations)
    else:
        avg_acceleration = 0.0

    total_change = recent[-1] - recent[0]
    pct_change = (total_change / recent[0] * 100) if recent[0] != 0 else None
    avg_velocity = sum(velocities) / len(velocities)

    if avg_velocity > 0:
        direction = "加速上升" if avg_acceleration > 0 else "减速上升"
    elif avg_velocity < 0:
        direction = "加速下降" if avg_acceleration < 0 else "减速下降"
    else:
        direction = "平稳"

    return {
        "indicator_id": indicator_id,
        "indicator_name": _get_indicator_name(indicator_id),
        "window": window,
        "total_change": round(total_change, 4),
        "pct_change": round(pct_change, 2) if pct_change is not None else None,
        "avg_velocity": round(avg_velocity, 4),
        "avg_acceleration": round(avg_acceleration, 4),
        "direction": direction,
        "roc": compute_roc(indicator_id, period=window),
        "date_range": f"{dates[-(window+1)]} ~ {dates[-1]}",
    }


def compute_all_momentum(window: int = 3) -> List[Dict]:
    """计算所有指标的动量指标"""
    results = []
    for ind in db.get_indicators():
        m = compute_momentum(ind["id"], window=window)
        if m.get("momentum") != "insufficient_data":
            results.append(m)
    return results


# ============ 三、拐点检测 ============

def detect_inflection_points(indicator_id: int, min_points: int = 4) -> Dict:
    """
    通过二阶导符号变化检测拐点。
    - 二阶导由正转负：上拐点（增速由加速转减速）
    - 二阶导由负转正：下拐点（减速后开始加速）
    """
    dates, values = _extract_series(indicator_id)
    if len(values) < min_points:
        return {
            "indicator_id": indicator_id,
            "indicator_name": _get_indicator_name(indicator_id),
            "inflection_points": [],
            "current_phase": "insufficient_data",
        }

    first_diff = [values[i+1] - values[i] for i in range(len(values) - 1)]
    second_diff = [first_diff[i+1] - first_diff[i] for i in range(len(first_diff) - 1)]

    inflection_points = []
    for i in range(1, len(second_diff)):
        prev_sign = second_diff[i - 1]
        curr_sign = second_diff[i]
        if (prev_sign > 0 and curr_sign < 0) or (prev_sign < 0 and curr_sign > 0):
            inflection_idx = i + 1
            inflection_points.append({
                "date": dates[inflection_idx],
                "value": values[inflection_idx],
                "type": "上拐点" if prev_sign > 0 else "下拐点",
                "change": round(curr_sign - prev_sign, 4),
            })

    if second_diff:
        current_curvature = second_diff[-1]
        if current_curvature > 0:
            current_phase = "加速阶段"
        elif current_curvature < 0:
            current_phase = "减速阶段"
        else:
            current_phase = "线性阶段"
    else:
        current_phase = "数据不足"

    if len(values) >= 2:
        recent_slope = (values[-1] - values[-2])
        if recent_slope > 0 and current_curvature < 0:
            phase_detail = "上升但减速（可能见顶）"
        elif recent_slope > 0 and current_curvature > 0:
            phase_detail = "上升且加速（繁荣期）"
        elif recent_slope < 0 and current_curvature < 0:
            phase_detail = "下降且加速（衰退期）"
        elif recent_slope < 0 and current_curvature > 0:
            phase_detail = "下降但减速（可能见底）"
        else:
            phase_detail = "平稳"
    else:
        phase_detail = "数据不足"

    return {
        "indicator_id": indicator_id,
        "indicator_name": _get_indicator_name(indicator_id),
        "inflection_points": inflection_points,
        "inflection_count": len(inflection_points),
        "current_phase": current_phase,
        "phase_detail": phase_detail,
        "current_curvature": round(current_curvature, 4) if second_diff else None,
        "data_range": f"{dates[0]} ~ {dates[-1]}",
    }


def detect_all_inflections() -> List[Dict]:
    """检测所有指标的拐点"""
    results = []
    for ind in db.get_indicators():
        info = detect_inflection_points(ind["id"])
        if info["current_phase"] != "insufficient_data":
            results.append(info)
    return results


# ============ 四、增强的健康度评分（按分类权重）============

def compute_weighted_health_score() -> Dict:
    """
    按分类权重计算加权健康度评分。
    供给端、需求端、资本端权重更高。
    """
    active_signals = db.get_signal_events(is_resolved=False)
    category_penalties = {}

    for sig in active_signals:
        level = sig.get("level", "")
        indicator_id = sig.get("indicator_id")
        if indicator_id:
            ind = db.get_indicator_by_id(indicator_id)
            if ind:
                cat = ind["category"]
                weight = CATEGORY_WEIGHTS.get(cat, 1.0)
                penalty_map = {"领先": 30, "同步": 15, "滞后": 5}
                base_penalty = penalty_map.get(level, 5)
                if cat not in category_penalties:
                    category_penalties[cat] = 0
                category_penalties[cat] += base_penalty * weight

    total_penalty = sum(category_penalties.values())
    score = max(0, round(100 - total_penalty))

    if score >= 70:
        status, emoji = "健康", "🟢"
    elif score >= 40:
        status, emoji = "关注", "🟡"
    elif score >= 20:
        status, emoji = "预警", "🟠"
    else:
        status, emoji = "危险", "🔴"

    category_details = {}
    for cat, penalty in category_penalties.items():
        max_penalty = 100 * CATEGORY_WEIGHTS.get(cat, 1.0)
        category_details[cat] = {
            "penalty": round(penalty, 1),
            "weight": CATEGORY_WEIGHTS.get(cat, 1.0),
            "sub_score": round(max(0, 100 - penalty), 1),
        }

    return {
        "score": score,
        "status": status,
        "emoji": emoji,
        "total_penalty": round(total_penalty, 1),
        "category_penalties": category_penalties,
        "category_details": category_details,
        "active_signal_count": len(active_signals),
        "recommendation": _get_weighted_recommendation(score, category_penalties),
        "timestamp": datetime.now().isoformat(),
    }


def _get_weighted_recommendation(score: int, category_penalties: Dict) -> str:
    if not category_penalties:
        return "无活跃信号，各分类均处于正常状态。"

    sorted_cats = sorted(category_penalties.items(), key=lambda x: x[1], reverse=True)
    top_issues = sorted_cats[:2] if len(sorted_cats) >= 2 else sorted_cats

    if score >= 70:
        return f"整体健康。关注 {top_issues[0][0]} 分类的潜在风险。"
    elif score >= 40:
        cats_str = "、".join(c[0] for c in top_issues)
        return f"进入关注区间。重点关注: {cats_str}。建议降低新增敞口。"
    elif score >= 20:
        cats_str = "、".join(c[0] for c in top_issues)
        return f"面临调整压力。重灾区: {cats_str}。建议转向防御性头寸。"
    else:
        cats_str = "、".join(c[0] for c in top_issues)
        return f"产业进入衰退。重灾区: {cats_str}。建议减仓或做空。"


# ============ 五、综合热力图数据生成 ============

def generate_heatmap_data(indicator_ids: Optional[List[int]] = None) -> Dict:
    """
    生成用于热力图的数据，包含：
    - 变化率矩阵（按分类×指标）
    - 热力图颜色映射值
    - 分类汇总
    """
    if indicator_ids is None:
        indicators = db.get_indicators()
        indicator_ids = [ind["id"] for ind in indicators]

    heatmap_cells = []
    category_summary = {}

    for iid in indicator_ids:
        ind = db.get_indicator_by_id(iid)
        if not ind:
            continue
        dates, values = _extract_series(iid)
        if len(values) < 2:
            continue

        change_rate = (values[-1] - values[-2]) / values[-2] * 100 if values[-2] != 0 else 0
        momentum = compute_momentum(iid, window=3)
        inflection = detect_inflection_points(iid)

        if ind["category"] not in category_summary:
            category_summary[ind["category"]] = []

        cell = {
            "indicator_id": iid,
            "indicator_name": ind["name"],
            "category": ind["category"],
            "sub_category": ind.get("sub_category", ""),
            "change_rate": round(change_rate, 2),
            "current_value": values[-1],
            "current_date": dates[-1],
            "trend": momentum.get("direction", "N/A"),
            "phase": inflection.get("phase_detail", "N/A"),
            "curvature": inflection.get("current_curvature"),
        }
        heatmap_cells.append(cell)
        category_summary[ind["category"]].append(cell)

    category_stats = {}
    for cat, cells in category_summary.items():
        rates = [c["change_rate"] for c in cells]
        avg_rate = sum(rates) / len(rates) if rates else 0
        up_count = sum(1 for r in rates if r > 0)
        down_count = sum(1 for r in rates if r < 0)
        flat_count = sum(1 for r in rates if r == 0)
        category_stats[cat] = {
            "avg_change_rate": round(avg_rate, 2),
            "up_count": up_count,
            "down_count": down_count,
            "flat_count": flat_count,
            "total": len(cells),
            "breadth": round(up_count / len(cells) * 100, 1) if cells else 0,
        }

    return {
        "cells": heatmap_cells,
        "category_stats": category_stats,
        "total_indicators": len(heatmap_cells),
        "timestamp": datetime.now().isoformat(),
    }


# ============ 六、完整报告生成 ============

def generate_full_report() -> str:
    """
    生成包含表格和建议的完整分析报告。
    整合健康度、趋势、动量、拐点、相关性、热力图。
    """
    lines = []
    lines.append("=" * 70)
    lines.append("全球 AI 产业跟踪框架 - 完整分析报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    # 1. 健康度概览
    lines.append("\n" + "━" * 70)
    lines.append("📊 一、产业健康度概览")
    lines.append("━" * 70)

    health = compute_health_score()
    weighted = compute_weighted_health_score()

    lines.append(f"\n  综合评分: {health['score']}/100 ({health['status']}) {health['emoji']}")
    lines.append(f"  加权评分: {weighted['score']}/100 ({weighted['status']}) {weighted['emoji']}")
    lines.append(f"  领先信号: {health['leading_signals']} 个 | 同步: {health['sync_signals']} | 滞后: {health['lagging_signals']}")
    lines.append(f"  建议: {health['recommendation']}")

    if weighted.get("category_details"):
        lines.append("\n  分类加权评分:")
        lines.append(f"  {'分类':<12} {'权重':<6} {'扣分':<8} {'子评分':<8}")
        lines.append(f"  {'─' * 34}")
        for cat, detail in sorted(weighted["category_details"].items(),
                                   key=lambda x: x[1]["sub_score"]):
            lines.append(f"  {cat:<10} {detail['weight']:<6.1f} {detail['penalty']:<8.1f} {detail['sub_score']:<8.1f}")

    # 2. 信号汇总
    lines.append("\n" + "━" * 70)
    lines.append("🚨 二、见顶信号检测")
    lines.append("━" * 70)

    triggered = check_all_signals()
    if triggered:
        lines.append(f"\n  新触发信号 ({len(triggered)} 个):")
        for sig in triggered:
            lines.append(f"    [{sig['level']}] {sig['rule_name']}")
            lines.append(f"      指标: {sig['indicator_name']} = {sig['trigger_value']}")
            lines.append(f"      阈值: {sig['threshold']} ({sig['comparison']})")
    else:
        lines.append("\n  ✓ 当前无新触发信号")

    active = db.get_signal_events(is_resolved=False)
    if active:
        lines.append(f"\n  活跃信号事件 ({len(active)} 个):")
        for event in active:
            lines.append(f"    [{event.get('level', '-')}] {event.get('rule_name', '-')} "
                        f"({event.get('trigger_date', '-')})")

    # 3. 分类趋势表
    lines.append("\n" + "━" * 70)
    lines.append("📈 三、分类趋势分析")
    lines.append("━" * 70)

    categories = ["供给端", "需求端", "资本与融资", "中游数据代理",
                  "Coding渗透", "非Coding渗透", "个人用户渗透", "企业用户渗透"]
    lines.append(f"\n  {'分类':<10} {'指标数':<8} {'上升':<6} {'下降':<6} {'平稳':<6} {'平均变化率':<12}")
    lines.append(f"  {'─' * 50}")

    heatmap = generate_heatmap_data()
    for cat in categories:
        if cat in heatmap["category_stats"]:
            stats = heatmap["category_stats"][cat]
            avg_cr = f"{stats['avg_change_rate']:+.1f}%"
            lines.append(f"  {cat:<10} {stats['total']:<8} {stats['up_count']:<6} "
                        f"{stats['down_count']:<6} {stats['flat_count']:<6} {avg_cr:<12}")

    # 4. 动量指标
    lines.append("\n" + "━" * 70)
    lines.append("⚡ 四、动量指标排名（按绝对变化率排序）")
    lines.append("━" * 70)

    momentum_list = compute_all_momentum(window=3)
    momentum_list.sort(key=lambda x: abs(x.get("pct_change") or 0), reverse=True)

    lines.append(f"\n  {'排名':<5} {'指标':<30} {'变化率':<10} {'ROC':<10} {'方向':<12}")
    lines.append(f"  {'─' * 67}")
    for rank, m in enumerate(momentum_list[:15], 1):
        pct = f"{m['pct_change']:+.1f}%" if m['pct_change'] is not None else "N/A"
        roc = f"{m['roc']:+.1f}%" if m.get("roc") is not None else "N/A"
        lines.append(f"  {rank:<5} {m['indicator_name']:<30.30} {pct:<10} {roc:<10} {m['direction']:<12}")

    # 5. 拐点检测
    lines.append("\n" + "━" * 70)
    lines.append("🔄 五、关键拐点检测")
    lines.append("━" * 70)

    inflections = detect_all_inflections()
    inflections_with_points = [i for i in inflections if i["inflection_count"] > 0]
    inflections_with_points.sort(key=lambda x: x["inflection_count"], reverse=True)

    if inflections_with_points:
        lines.append(f"\n  检测到拐点的指标 ({len(inflections_with_points)} 个):")
        for info in inflections_with_points[:10]:
            ip_types = [p["type"] for p in info["inflection_points"]]
            latest_type = info["inflection_points"][-1]["type"]
            lines.append(f"    {info['indicator_name']:<30.30} "
                        f"拐点={info['inflection_count']} 最新={latest_type} ({info['inflection_points'][-1]['date']})")
            lines.append(f"      当前阶段: {info['phase_detail']}")
    else:
        lines.append("\n  暂未检测到明显拐点。")

    current_phases = {}
    for info in inflections:
        phase = info["phase_detail"]
        if phase not in current_phases:
            current_phases[phase] = []
        current_phases[phase].append(info["indicator_name"])

    lines.append("\n  当前阶段分布:")
    for phase, names in sorted(current_phases.items(), key=lambda x: len(x[1]), reverse=True):
        lines.append(f"    【{phase}】({len(names)} 个): {', '.join(names[:5])}"
                    + ("..." if len(names) > 5 else ""))

    # 6. 相关性
    lines.append("\n" + "━" * 70)
    lines.append("🔗 六、指标相关性分析")
    lines.append("━" * 70)

    corr = compute_correlation_matrix()
    if corr["strong_pairs"]:
        lines.append(f"\n  强相关指标对 (|r| >= 0.7, 共 {len(corr['strong_pairs'])} 对):")
        lines.append(f"  {'指标1':<30} {'指标2':<30} {'相关系数':<10} {'强度':<10}")
        lines.append(f"  {'─' * 80}")
        for pair in corr["strong_pairs"][:15]:
            lines.append(f"  {pair['indicator_1']:<30.30} {pair['indicator_2']:<30.30} "
                        f"{pair['correlation']:>+8.4f}   {pair['strength']}")
    else:
        lines.append("\n  未发现强相关指标对。")

    # 7. 热力图摘要
    lines.append("\n" + "━" * 70)
    lines.append("🌡 七、产业热力图摘要")
    lines.append("━" * 70)

    if heatmap["category_stats"]:
        lines.append(f"\n  {'分类':<12} {'指标数':<8} {'上涨':<6} {'下跌':<6} {'广度':<10} {'平均变化率':<12}")
        lines.append(f"  {'─' * 54}")
        for cat, stats in sorted(heatmap["category_stats"].items(),
                                  key=lambda x: x[1]["avg_change_rate"], reverse=True):
            breadth = f"{stats['breadth']:.0f}%"
            avg_cr = f"{stats['avg_change_rate']:+.1f}%"
            lines.append(f"  {cat:<12} {stats['total']:<8} {stats['up_count']:<6} "
                        f"{stats['down_count']:<6} {breadth:<10} {avg_cr:<12}")

    # 8. 总结与建议
    lines.append("\n" + "━" * 70)
    lines.append("💡 八、总结与投资建议")
    lines.append("━" * 70)

    lines.append(f"\n  {weighted['emoji']} 综合判断: {weighted['status']}")
    lines.append(f"  {weighted['recommendation']}")

    if heatmap["category_stats"]:
        hottest = max(heatmap["category_stats"].items(),
                      key=lambda x: x[1]["avg_change_rate"])
        coldest = min(heatmap["category_stats"].items(),
                      key=lambda x: x[1]["avg_change_rate"])
        lines.append(f"\n  🔥 最强板块: {hottest[0]} (平均变化率 {hottest[1]['avg_change_rate']:+.1f}%, 广度 {hottest[1]['breadth']:.0f}%)")
        lines.append(f"  ❄ 最弱板块: {coldest[0]} (平均变化率 {coldest[1]['avg_change_rate']:+.1f}%, 广度 {coldest[1]['breadth']:.0f}%)")

    lines.append("\n" + "━" * 70)
    lines.append("报告结束")
    lines.append("=" * 70)

    return "\n".join(lines)