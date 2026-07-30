"""
数据库模块：定义指标元数据、时间序列数据点、见顶信号规则的数据模型。
使用 SQLite 作为存储，适合单机研究工具。
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import contextlib

DB_PATH = os.path.join(os.path.dirname(__file__), "ai_tracker.db")

SCHEMA_SQL = """
-- 指标元数据表：存储框架中所有追踪指标的定义
CREATE TABLE IF NOT EXISTS indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,           -- 分类：中游代理/供给端/需求端/用户渗透/企业渗透/资本/Coding/NonCoding
    sub_category TEXT,                -- 子分类
    name TEXT NOT NULL,               -- 指标名称
    frequency TEXT NOT NULL,          -- 更新频率：日/周/月/季/半年/年
    source TEXT,                      -- 数据源
    data_type TEXT NOT NULL,          -- 数据类型：numeric/percentage/currency/text
    unit TEXT,                        -- 单位
    description TEXT,                 -- 描述
    automation_level TEXT,            -- 自动化级别：automatic/semi_auto/manual
    fetch_url TEXT,                   -- 自动获取URL（如适用）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 时间序列数据表：存储每个指标的历史数据点
CREATE TABLE IF NOT EXISTS data_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_id INTEGER NOT NULL,
    date TEXT NOT NULL,               -- YYYY-MM-DD
    value REAL,                       -- 数值（数值型指标）
    value_text TEXT,                  -- 文本值（文本型指标）
    source TEXT,                      -- 数据来源
    notes TEXT,                       -- 备注
    is_estimated INTEGER DEFAULT 0,   -- 是否为估算值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES indicators(id),
    UNIQUE(indicator_id, date)
);

-- 见顶信号规则表：框架第十节的信号定义
CREATE TABLE IF NOT EXISTS signal_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,              -- 信号层级：领先/同步/滞后
    indicator_id INTEGER,             -- 关联指标（可为空，表示综合信号）
    rule_name TEXT NOT NULL,          -- 规则名称
    rule_description TEXT,            -- 规则描述
    threshold REAL,                   -- 触发阈值
    comparison TEXT DEFAULT 'below',  -- above/below/change_rate
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES indicators(id)
);

-- 信号触发记录表
CREATE TABLE IF NOT EXISTS signal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    indicator_id INTEGER,
    trigger_date TEXT NOT NULL,
    trigger_value REAL,
    severity TEXT DEFAULT 'warning',  -- info/warning/danger
    notes TEXT,
    is_resolved INTEGER DEFAULT 0,
    resolved_at TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES signal_rules(id),
    FOREIGN KEY (indicator_id) REFERENCES indicators(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_points_indicator_id ON data_points(indicator_id);
CREATE INDEX IF NOT EXISTS idx_data_points_date ON data_points(date);
CREATE INDEX IF NOT EXISTS idx_signal_events_rule_id ON signal_events(rule_id);
CREATE INDEX IF NOT EXISTS idx_indicators_category ON indicators(category);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextlib.contextmanager
def get_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_cursor() as cur:
        cur.executescript(SCHEMA_SQL)
    print(f"数据库已初始化: {DB_PATH}")


# ============ 指标 CRUD ============

def add_indicator(category: str, name: str, frequency: str, data_type: str,
                  sub_category: str = "", source: str = "", unit: str = "",
                  description: str = "", automation_level: str = "manual",
                  fetch_url: str = "") -> int:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO indicators (category, sub_category, name, frequency, source,
                                   data_type, unit, description, automation_level, fetch_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, sub_category, name, frequency, source, data_type, unit,
              description, automation_level, fetch_url))
        return cur.lastrowid


def get_indicators(category: Optional[str] = None) -> List[Dict]:
    with get_cursor() as cur:
        if category:
            cur.execute("SELECT * FROM indicators WHERE category = ? ORDER BY id", (category,))
        else:
            cur.execute("SELECT * FROM indicators ORDER BY category, sub_category, id")
        return [dict(row) for row in cur.fetchall()]


def get_indicator_by_id(indicator_id: int) -> Optional[Dict]:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM indicators WHERE id = ?", (indicator_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_indicator(indicator_id: int, **kwargs):
    fields = [f"{k} = ?" for k in kwargs]
    values = list(kwargs.values()) + [indicator_id]
    with get_cursor() as cur:
        cur.execute(f"UPDATE indicators SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)


# ============ 数据点 CRUD ============

def add_data_point(indicator_id: int, date: str, value: Optional[float] = None,
                   value_text: Optional[str] = None, source: str = "",
                   notes: str = "", is_estimated: bool = False):
    with get_cursor() as cur:
        cur.execute("""
            INSERT OR REPLACE INTO data_points (indicator_id, date, value, value_text,
                                                source, notes, is_estimated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (indicator_id, date, value, value_text, source, notes, int(is_estimated)))


def get_data_points(indicator_id: int, start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict]:
    with get_cursor() as cur:
        query = "SELECT * FROM data_points WHERE indicator_id = ?"
        params = [indicator_id]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " ORDER BY date"
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def get_latest_data_point(indicator_id: int) -> Optional[Dict]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM data_points WHERE indicator_id = ?
            ORDER BY date DESC LIMIT 1
        """, (indicator_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def delete_data_point(data_point_id: int):
    with get_cursor() as cur:
        cur.execute("DELETE FROM data_points WHERE id = ?", (data_point_id,))


# ============ 信号规则 CRUD ============

def add_signal_rule(level: str, rule_name: str, indicator_id: Optional[int] = None,
                    rule_description: str = "", threshold: Optional[float] = None,
                    comparison: str = "below") -> int:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO signal_rules (level, indicator_id, rule_name, rule_description,
                                     threshold, comparison)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (level, indicator_id, rule_name, rule_description, threshold, comparison))
        return cur.lastrowid


def get_signal_rules(level: Optional[str] = None) -> List[Dict]:
    with get_cursor() as cur:
        if level:
            cur.execute("SELECT * FROM signal_rules WHERE level = ? AND is_active = 1 ORDER BY id", (level,))
        else:
            cur.execute("SELECT * FROM signal_rules WHERE is_active = 1 ORDER BY level, id")
        return [dict(row) for row in cur.fetchall()]


# ============ 信号事件 CRUD ============

def add_signal_event(rule_id: int, indicator_id: Optional[int], trigger_date: str,
                     trigger_value: Optional[float] = None, severity: str = "warning",
                     notes: str = "") -> int:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO signal_events (rule_id, indicator_id, trigger_date, trigger_value,
                                       severity, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rule_id, indicator_id, trigger_date, trigger_value, severity, notes))
        return cur.lastrowid


def get_signal_events(is_resolved: Optional[bool] = None) -> List[Dict]:
    with get_cursor() as cur:
        if is_resolved is not None:
            cur.execute("""
                SELECT se.*, sr.rule_name, sr.level, i.name as indicator_name
                FROM signal_events se
                JOIN signal_rules sr ON se.rule_id = sr.id
                LEFT JOIN indicators i ON se.indicator_id = i.id
                WHERE se.is_resolved = ?
                ORDER BY se.trigger_date DESC
            """, (int(is_resolved),))
        else:
            cur.execute("""
                SELECT se.*, sr.rule_name, sr.level, i.name as indicator_name
                FROM signal_events se
                JOIN signal_rules sr ON se.rule_id = sr.id
                LEFT JOIN indicators i ON se.indicator_id = i.id
                ORDER BY se.trigger_date DESC
            """)
        return [dict(row) for row in cur.fetchall()]


def resolve_signal_event(event_id: int):
    with get_cursor() as cur:
        cur.execute("""
            UPDATE signal_events SET is_resolved = 1, resolved_at = ? WHERE id = ?
        """, (datetime.now().isoformat(), event_id))


# ============ 统计查询 ============

def get_indicators_by_category() -> Dict[str, List[Dict]]:
    indicators = get_indicators()
    result = {}
    for ind in indicators:
        cat = ind["category"]
        if cat not in result:
            result[cat] = []
        result[cat].append(ind)
    return result


def get_data_summary() -> Dict[str, Any]:
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM indicators")
        indicator_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM data_points")
        data_point_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM signal_events WHERE is_resolved = 0")
        active_signals = cur.fetchone()["cnt"]
        return {
            "indicator_count": indicator_count,
            "data_point_count": data_point_count,
            "active_signals": active_signals
        }
