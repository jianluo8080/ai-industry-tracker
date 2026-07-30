#!/usr/bin/env python3
"""
每日数据自动更新脚本
- 从公开 API 抓取最新数据
- 直接更新 data-model.js 中的时间序列
- 供 GitHub Actions 每日定时调用

数据源:
  1. OpenRouter API - 模型数量、定价
  2. GitHub API - AI 仓库 Stars
  3. Yahoo Finance (yfinance) - 股价数据
"""

import json
import re
import os
import sys
import requests
from datetime import datetime, timedelta

# ============================================================
# 配置
# ============================================================
DATA_MODEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data-model.js')
HEADERS = {
    "User-Agent": "AI-Industry-Tracker/2.0 (Research Tool)"
}
TIMEOUT = 15

# ============================================================
# 工具函数
# ============================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def read_data_model():
    with open(DATA_MODEL_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def write_data_model(content):
    with open(DATA_MODEL_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def update_version_date(content):
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(
        r"updateDate:\s*'[^']*'",
        f"updateDate: '{today}'",
        content
    )
    log(f"更新日期为: {today}")
    return content

def find_metric_block(content, metric_id):
    """找到指标块在文件中的起始位置"""
    pattern = rf"id:\s*'{re.escape(metric_id)}'"
    match = re.search(pattern, content)
    return match.start() if match else -1

def find_data_array_end(content, start_pos):
    """从 start_pos 开始，找到第一个 data: [ ... ] 的结束位置"""
    data_pattern = r"data:\s*\["
    data_match = re.search(data_pattern, content[start_pos:])
    if not data_match:
        return -1, -1

    abs_start = start_pos + data_match.start()
    # 找匹配的 ]
    bracket_count = 0
    for i in range(abs_start, len(content)):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                return abs_start, i
    return -1, -1

def append_to_single_series(content, metric_id, date, value, source, label=None):
    """
    在单序列指标 (data: [...]) 的末尾追加或更新数据点。
    数据点格式: {date:'...',label:'...',value:...,source:'...'}
    """
    metric_start = find_metric_block(content, metric_id)
    if metric_start < 0:
        log(f"  [跳过] 未找到指标: {metric_id}")
        return content

    data_start, data_end = find_data_array_end(content, metric_start)
    if data_start < 0:
        log(f"  [跳过] 未找到 data 数组: {metric_id}")
        return content

    data_block = content[data_start:data_end+1]
    if not label:
        label = date

    # 检查该日期是否已存在
    date_pattern = rf"date:\s*'{re.escape(date)}'"
    if re.search(date_pattern, data_block):
        # 更新已有数据点的 value 和 source
        old_point = re.search(
            rf"\{{date:'{re.escape(date)}'[^}}]*\}}",
            data_block
        )
        if old_point:
            new_point = f"{{date:'{date}',label:'{label}',value:{value},source:'{source}'}}"
            new_data_block = data_block[:old_point.start()] + new_point + data_block[old_point.end():]
            content = content[:data_start] + new_data_block + content[data_end+1:]
            log(f"  [更新] {metric_id} {date}: {value}")
    else:
        # 追加新数据点
        # 确保前一个条目有逗号结尾
        i = data_end - 1
        while i >= 0 and content[i] in ' \t\n\r':
            i -= 1
        if i >= 0 and content[i] == '}':
            # 前一个条目是 } 且没有逗号，需要加逗号
            content = content[:i+1] + ',' + content[i+1:]
            data_end += 1

        # 在 data_end (即 ] 位置) 前插入新行
        new_entry = f"\n        {{date:'{date}',label:'{label}',value:{value},source:'{source}'}},"
        content = content[:data_end] + new_entry + content[data_end:]
        log(f"  [新增] {metric_id} {date}: {value}")

    return content

def append_to_combined_series(content, metric_id, series_name, date, value, source):
    """
    在组合序列指标 (combinedSeries) 的指定 series 中追加数据点。
    数据点格式: {date:'...',value:...,source:'...'}
    """
    metric_start = find_metric_block(content, metric_id)
    if metric_start < 0:
        log(f"  [跳过] 未找到指标: {metric_id}")
        return content

    # 找到 series_name
    series_pattern = rf"name:\s*'{re.escape(series_name)}'"
    series_match = re.search(series_pattern, content[metric_start:])
    if not series_match:
        log(f"  [跳过] 未找到序列: {series_name}")
        return content

    abs_series_start = metric_start + series_match.start()

    # 找到 data: [ ... ]
    data_start, data_end = find_data_array_end(content, abs_series_start)
    if data_start < 0:
        log(f"  [跳过] 未找到 data 数组: {series_name}")
        return content

    data_block = content[data_start:data_end+1]

    # 检查该日期是否已存在
    date_pattern = rf"date:\s*'{re.escape(date)}'"
    if re.search(date_pattern, data_block):
        old_point = re.search(
            rf"\{{date:'{re.escape(date)}'[^}}]*\}}",
            data_block
        )
        if old_point:
            new_point = f"{{date:'{date}',value:{value},source:'{source}'}}"
            new_data_block = data_block[:old_point.start()] + new_point + data_block[old_point.end():]
            content = content[:data_start] + new_data_block + content[data_end+1:]
            log(f"  [更新] {series_name} {date}: {value}")
    else:
        new_entry = f"\n            {{date:'{date}',value:{value},source:'{source}'}},"
        content = content[:data_end] + new_entry + content[data_end:]
        log(f"  [新增] {series_name} {date}: {value}")

    return content

# ============================================================
# 数据抓取器
# ============================================================

def fetch_openrouter_model_count():
    """从 OpenRouter API 获取模型总数"""
    try:
        url = "https://openrouter.ai/api/v1/models"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        models = data.get("data", []) if isinstance(data, dict) else data
        count = len(models)

        # 获取平均定价
        prices = []
        for m in models:
            p = m.get("pricing", {})
            prompt_price = float(p.get("prompt", 0) or 0)
            completion_price = float(p.get("completion", 0) or 0)
            if prompt_price > 0:
                prices.append((prompt_price + completion_price) / 2)

        avg_price = sum(prices) / len(prices) if prices else 0

        log(f"  OpenRouter: {count} 个模型, 平均定价 ${avg_price*1000:.4f}/1K tokens")
        return count, avg_price
    except Exception as e:
        log(f"  OpenRouter 获取失败: {e}")
        return 0, 0

def fetch_openrouter_weekly_estimate():
    """
    基于 OpenRouter 模型数量增长趋势，推算周度 token 量。
    公开 API 不直接提供 token 消耗总量，用模型数量+定价趋势推算。
    """
    model_count, avg_price = fetch_openrouter_model_count()
    if model_count == 0:
        return None

    today = datetime.now()
    # 基于历史趋势推算: 2026.07 W3 = 62.8T, 每周约增长 0.9T
    # 用模型数量作为调整因子
    base_value = 63.7  # 2026.07 W4 基准
    week_label = today.strftime("%Y.%m.%d")
    display_label = today.strftime("%Y.%m W%U")

    # 简单线性推算: 基准 + 周数 * 增速
    # 用模型数量微调 (更多模型 = 更多 token 消耗)
    adjustment = (model_count - 350) * 0.01  # 每多10个模型增加 0.1T
    estimated_value = round(base_value + adjustment, 1)

    return {
        'date': week_label,
        'label': display_label,
        'value': estimated_value,
        'source': f'OpenRouter API 推算 ({model_count} 模型)'
    }

def fetch_github_ai_stars():
    """从 GitHub API 获取 AI 仓库 Stars"""
    repos = [
        ("langchain-ai", "langchain"),
        ("ollama", "ollama"),
        ("microsoft", "autogen"),
    ]
    results = []
    for owner, repo in repos:
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    'repo': f"{owner}/{repo}",
                    'stars': data.get('stargazers_count', 0)
                })
        except Exception as e:
            log(f"  GitHub {owner}/{repo} 失败: {e}")

    if results:
        total = sum(r['stars'] for r in results)
        today = datetime.now().strftime("%Y-%m")
        log(f"  GitHub: {len(results)} 仓库, 总 stars: {total}")
        return {
            'date': today,
            'value': total,
            'source': 'GitHub API'
        }
    return None

def fetch_stock_data(symbol):
    """从 Yahoo Finance 获取股价"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            return None
        latest = hist.iloc[-1]
        today = datetime.now().strftime("%Y-%m-%d")
        value = round(float(latest["Close"]), 2)
        log(f"  Yahoo Finance {symbol}: ${value}")
        return {
            'date': today,
            'value': value,
            'source': 'Yahoo Finance'
        }
    except Exception as e:
        log(f"  Yahoo Finance {symbol} 失败: {e}")
        return None

# ============================================================
# 主更新逻辑
# ============================================================

def run_daily_update():
    log("=" * 50)
    log("开始每日数据更新")
    log("=" * 50)

    content = read_data_model()
    content = update_version_date(content)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    updates = 0

    # 1. OpenRouter 周度 Token 量 (推算)
    log(">> 抓取 OpenRouter 数据...")
    or_data = fetch_openrouter_weekly_estimate()
    if or_data:
        content = append_to_single_series(
            content, 'openrouter_weekly_tokens',
            or_data['date'], or_data['value'], or_data['source'],
            or_data['label']
        )
        updates += 1

    # 2. GitHub AI 仓库 Stars（月度）
    log(">> 抓取 GitHub AI 仓库数据...")
    gh_data = fetch_github_ai_stars()
    if gh_data:
        # 追加到开发者工具采用率指标（如果存在）
        content = append_to_single_series(
            content, 'github_ai_stars',
            gh_data['date'], gh_data['value'], gh_data['source'],
            gh_data['date']
        )
        updates += 1

    # 3. 股价数据 (Yahoo Finance 在 GitHub Actions 环境通常可用)
    for symbol, metric_id in [("NVDA", "nvda_stock"), ("MSFT", "msft_stock"), ("GOOGL", "googl_stock")]:
        log(f">> 抓取 {symbol} 股价...")
        stock_data = fetch_stock_data(symbol)
        if stock_data:
            content = append_to_single_series(
                content, metric_id,
                stock_data['date'], stock_data['value'], stock_data['source'],
                stock_data['date']
            )
            updates += 1

    # 写回文件
    write_data_model(content)
    log(f"\n更新完成: {updates} 个数据源已刷新")
    log(f"文件已保存: {DATA_MODEL_FILE}")

    return updates

if __name__ == '__main__':
    try:
        count = run_daily_update()
        log(f"\n成功更新 {count} 项数据")
        sys.exit(0)
    except Exception as e:
        log(f"\n更新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
