"""
CSV 导入导出模块：数据点批量导入、全量数据导出、指标定义导出。
"""

import csv
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional, Callable
import database as db


# ============ CSV 导入 ============

def import_data_points_from_csv(
    file_path: str,
    indicator_id: Optional[int] = None,
    indicator_name_col: str = "indicator_name",
    date_col: str = "date",
    value_col: str = "value",
    source_col: str = "source",
    notes_col: str = "notes",
    date_format: str = "%Y-%m-%d",
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Dict:
    """
    从 CSV 文件批量导入数据点。

    CSV 格式要求：
    - 若指定 indicator_id，则所有数据导入该指标
    - 若不指定 indicator_id，CSV 必须包含 indicator_name 列，
      程序会按名称匹配已有指标

    必填列：date, value
    可选列：indicator_name, source, notes

    返回导入结果统计。
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"文件不存在: {file_path}"}

    imported = 0
    skipped = 0
    errors = []
    total_rows = 0

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        total_rows = len(rows)

        for idx, row in enumerate(rows):
            try:
                date_str = row.get(date_col, "").strip()
                value_str = row.get(value_col, "").strip()

                if not date_str:
                    skipped += 1
                    errors.append(f"第 {idx + 2} 行: 日期为空")
                    continue

                try:
                    datetime.strptime(date_str, date_format)
                except ValueError:
                    skipped += 1
                    errors.append(f"第 {idx + 2} 行: 日期格式错误 '{date_str}' (期望 {date_format})")
                    continue

                if value_str == "":
                    value = None
                else:
                    try:
                        value = float(value_str)
                    except ValueError:
                        skipped += 1
                        errors.append(f"第 {idx + 2} 行: 数值格式错误 '{value_str}'")
                        continue

                if indicator_id is not None:
                    target_id = indicator_id
                else:
                    ind_name = row.get(indicator_name_col, "").strip()
                    if not ind_name:
                        skipped += 1
                        errors.append(f"第 {idx + 2} 行: 未指定指标名称且未提供 indicator_id")
                        continue
                    target_id = _find_indicator_by_name(ind_name)
                    if target_id is None:
                        skipped += 1
                        errors.append(f"第 {idx + 2} 行: 指标 '{ind_name}' 未找到")
                        continue

                source = row.get(source_col, "").strip()
                notes = row.get(notes_col, "").strip()

                db.add_data_point(
                    indicator_id=target_id,
                    date=date_str,
                    value=value,
                    source=source,
                    notes=notes,
                )
                imported += 1

            except Exception as e:
                skipped += 1
                errors.append(f"第 {idx + 2} 行: {str(e)}")

            if progress_callback and (idx + 1) % max(1, total_rows // 10) == 0:
                progress_callback(idx + 1, total_rows, date_str)

    return {
        "success": True,
        "total_rows": total_rows,
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:20],
        "file_path": file_path,
    }


def _find_indicator_by_name(name: str) -> Optional[int]:
    """按名称查找指标，支持精确匹配和包含匹配"""
    indicators = db.get_indicators()
    for ind in indicators:
        if ind["name"] == name:
            return ind["id"]
    for ind in indicators:
        if name in ind["name"] or ind["name"] in name:
            return ind["id"]
    return None


def import_data_from_csv_by_path(
    file_path: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Dict:
    """
    便捷方法：从 CSV 路径自动识别格式并导入。
    CSV 需包含 indicator_name, date, value 列。
    """
    return import_data_points_from_csv(
        file_path=file_path,
        indicator_id=None,
        progress_callback=progress_callback,
    )


# ============ CSV 导出 ============

def export_all_data_to_csv(output_path: Optional[str] = None, category: Optional[str] = None) -> str:
    """
    导出全部数据点为 CSV 文件。
    包含列：指标ID、分类、子分类、指标名称、日期、数值、文本值、来源、备注、是否估算
    """
    indicators = db.get_indicators(category=category)
    all_rows = []

    for ind in indicators:
        data_points = db.get_data_points(ind["id"])
        for dp in data_points:
            all_rows.append({
                "indicator_id": ind["id"],
                "category": ind["category"],
                "sub_category": ind.get("sub_category", ""),
                "indicator_name": ind["name"],
                "date": dp["date"],
                "value": dp["value"],
                "value_text": dp.get("value_text", ""),
                "source": dp.get("source", ""),
                "notes": dp.get("notes", ""),
                "is_estimated": dp.get("is_estimated", 0),
            })

    fieldnames = [
        "indicator_id", "category", "sub_category", "indicator_name",
        "date", "value", "value_text", "source", "notes", "is_estimated",
    ]

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "data_exports", f"all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    return output_path


def export_indicators_to_csv(output_path: Optional[str] = None, category: Optional[str] = None) -> str:
    """
    导出指标定义为 CSV 文件。
    包含列：ID、分类、子分类、指标名称、频率、数据类型、单位、描述、数据源、自动化级别、创建时间
    """
    indicators = db.get_indicators(category=category)

    fieldnames = [
        "id", "category", "sub_category", "name", "frequency",
        "data_type", "unit", "description", "source",
        "automation_level", "fetch_url", "created_at", "updated_at",
    ]

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "data_exports", f"indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ind in indicators:
            row = {k: ind.get(k, "") for k in fieldnames}
            writer.writerow(row)

    return output_path


def export_signals_to_csv(output_path: Optional[str] = None, include_resolved: bool = True) -> str:
    """
    导出信号事件为 CSV 文件。
    """
    events = db.get_signal_events(is_resolved=None if include_resolved else False)

    rows = []
    for evt in events:
        rows.append({
            "event_id": evt["id"],
            "rule_id": evt["rule_id"],
            "rule_name": evt.get("rule_name", ""),
            "level": evt.get("level", ""),
            "indicator_name": evt.get("indicator_name", ""),
            "trigger_date": evt["trigger_date"],
            "trigger_value": evt.get("trigger_value", ""),
            "severity": evt.get("severity", ""),
            "notes": evt.get("notes", ""),
            "is_resolved": evt.get("is_resolved", 0),
            "resolved_at": evt.get("resolved_at", ""),
            "created_at": evt.get("created_at", ""),
        })

    fieldnames = [
        "event_id", "rule_id", "rule_name", "level", "indicator_name",
        "trigger_date", "trigger_value", "severity", "notes",
        "is_resolved", "resolved_at", "created_at",
    ]

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "data_exports", f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def export_to_temp_csv(data_type: str = "all", category: Optional[str] = None) -> str:
    """
    导出数据到临时 CSV 文件，返回文件路径。
    data_type: 'all' | 'indicators' | 'signals'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.gettempdir()

    if data_type == "all":
        filename = f"ai_tracker_data_{timestamp}.csv"
        return export_all_data_to_csv(os.path.join(temp_dir, filename), category=category)
    elif data_type == "indicators":
        filename = f"ai_tracker_indicators_{timestamp}.csv"
        return export_indicators_to_csv(os.path.join(temp_dir, filename), category=category)
    elif data_type == "signals":
        filename = f"ai_tracker_signals_{timestamp}.csv"
        return export_signals_to_csv(os.path.join(temp_dir, filename))
    else:
        raise ValueError(f"未知的 data_type: {data_type}，可选: all, indicators, signals")


def get_csv_template() -> Dict[str, List[str]]:
    """
    获取 CSV 导入模板的列定义，用于生成模板文件。
    """
    return {
        "data_points": [
            "indicator_name",
            "date",
            "value",
            "source",
            "notes",
        ],
        "indicators": [
            "category",
            "sub_category",
            "name",
            "frequency",
            "data_type",
            "unit",
            "source",
            "description",
            "automation_level",
            "fetch_url",
        ],
    }


def generate_template_csv(output_path: str, template_type: str = "data_points") -> str:
    """
    生成 CSV 导入模板文件。
    template_type: 'data_points' | 'indicators'
    """
    templates = get_csv_template()
    if template_type not in templates:
        raise ValueError(f"未知的模板类型: {template_type}")

    fieldnames = templates[template_type]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    return output_path