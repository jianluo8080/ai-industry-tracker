"""
数据获取模块（增强版）：从公开API和网页抓取数据。

数据源:
  - Yahoo Finance (yfinance): 股票/指数
  - OpenRouter: 模型排名/定价/Token趋势
  - GitHub Trending + API: 开发者趋势/仓库统计
  - EIA: 电力数据/电价趋势
  - 行业公开数据: 英伟达财报/云定价
"""

import requests
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import database as db

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15
HEADERS = {
    "User-Agent": "AI-Industry-Tracker/1.0 (Research Tool)"
}


# ============ 辅助函数 ============

def _try_import(module_name: str):
    try:
        return __import__(module_name)
    except ImportError:
        return None


_INDICATOR_CACHE: Dict[str, int] = {}


def _get_indicator_id(name: str) -> Optional[int]:
    if name in _INDICATOR_CACHE:
        return _INDICATOR_CACHE[name]
    try:
        with db.get_cursor() as cur:
            cur.execute("SELECT id FROM indicators WHERE name = ?", (name,))
            row = cur.fetchone()
            if row:
                _INDICATOR_CACHE[name] = row["id"]
                return row["id"]
    except Exception as e:
        logger.error(f"查找指标 '{name}' 失败: {e}")
    return None


def save_fetched_to_db(metric_name: str, data: List[Dict]):
    """将获取的数据列表写入数据库对应指标。"""
    ind_id = _get_indicator_id(metric_name)
    if not ind_id:
        logger.warning(f"未找到指标: {metric_name}（{len(data)} 条数据被跳过）")
        return

    for point in data:
        try:
            db.add_data_point(
                indicator_id=ind_id,
                date=point.get("date", datetime.now().strftime("%Y-%m-%d")),
                value=point.get("value"),
                value_text=point.get("value_text"),
                source=point.get("source", "auto_fetched"),
                notes=point.get("notes", "")[:500] if point.get("notes") else "",
                is_estimated=point.get("is_estimated", False),
            )
        except Exception as e:
            logger.error(f"写入数据点失败 [{metric_name}]: {e}")


# ============ Yahoo Finance 股票数据 ============

def fetch_nvda_stock() -> List[Dict]:
    yf = _try_import("yfinance")
    if not yf:
        logger.warning("yfinance 未安装，跳过 NVDA 股票数据")
        return []
    try:
        ticker = yf.Ticker("NVDA")
        hist = ticker.history(period="3mo")
        results = []
        for date, row in hist.iterrows():
            results.append({
                "source": "Yahoo Finance",
                "metric": "NVDA股价",
                "date": date.strftime("%Y-%m-%d"),
                "value": round(float(row["Close"]), 2),
                "unit": "USD",
                "notes": f"成交量: {int(row['Volume'])}",
            })
        logger.info(f"获取到 NVDA {len(results)} 条股价数据")
        return results
    except Exception as e:
        logger.error(f"获取 NVDA 股票数据失败: {e}")
        return []


def fetch_cloud_stocks() -> List[Dict]:
    yf = _try_import("yfinance")
    if not yf:
        logger.warning("yfinance 未安装，跳过云厂商股价")
        return []
    tickers = {"MSFT": "微软", "AMZN": "亚马逊", "GOOGL": "谷歌", "META": "Meta"}
    results = []
    for symbol, name in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            for date, row in hist.iterrows():
                results.append({
                    "source": "Yahoo Finance",
                    "metric": f"{name}({symbol})股价",
                    "date": date.strftime("%Y-%m-%d"),
                    "value": round(float(row["Close"]), 2),
                    "unit": "USD",
                    "notes": f"成交量: {int(row['Volume'])}",
                })
        except Exception as e:
            logger.error(f"获取 {symbol} 股价失败: {e}")
    logger.info(f"获取到 {len(results)} 条云厂商股价数据")
    return results


def fetch_nasdaq_ai_index() -> List[Dict]:
    yf = _try_import("yfinance")
    if not yf:
        logger.warning("yfinance 未安装，跳过 AI 指数")
        return []
    try:
        ticker = yf.Ticker("NDX")
        hist = ticker.history(period="3mo")
        results = []
        for date, row in hist.iterrows():
            results.append({
                "source": "Yahoo Finance",
                "metric": "NASDAQ100指数",
                "date": date.strftime("%Y-%m-%d"),
                "value": round(float(row["Close"]), 2),
                "unit": "pts",
            })
        logger.info(f"获取到 NASDAQ100 {len(results)} 条数据")
        return results
    except Exception as e:
        logger.error(f"获取 NASDAQ 指数失败: {e}")
        return []


# ============ OpenRouter 排名（保留原有） ============

def fetch_openrouter_rankings() -> List[Dict]:
    try:
        url = "https://openrouter.ai/api/v1/models"
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict) and "data" in data:
            models = data.get("data", [])
        elif isinstance(data, list):
            models = data
        else:
            models = []

        rankings = []
        for m in models:
            rankings.append({
                "model": m.get("name", m.get("id", "Unknown")),
                "provider": m.get("provider", ""),
                "requests": m.get("request_count", 0),
                "tokens": m.get("token_count", 0),
                "context_length": m.get("context_length", 0),
                "pricing": m.get("pricing", {}),
            })

        rankings.sort(key=lambda x: x["tokens"], reverse=True)
        logger.info(f"获取到 {len(rankings)} 个模型的排名数据")
        return rankings
    except Exception as e:
        logger.error(f"获取 OpenRouter 排名失败: {e}")
        return []


def fetch_openrouter_model_stats(model_id: str) -> Optional[Dict]:
    try:
        url = f"https://openrouter.ai/api/v1/models/{model_id}/stats"
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"获取模型 {model_id} 统计失败: {e}")
        return None


# ============ OpenRouter 增强 ============

def fetch_openrouter_timeseries() -> List[Dict]:
    try:
        models = fetch_openrouter_rankings()
        today = datetime.now().strftime("%Y-%m-%d")
        results = []
        for m in models[:20]:
            results.append({
                "source": "OpenRouter",
                "metric": "全行业Token消耗量",
                "date": today,
                "value": m.get("tokens", 0),
                "unit": "tokens",
                "notes": f"{m.get('model', 'Unknown')} | 请求: {m.get('requests', 0)}",
            })
        logger.info(f"获取到 {len(results)} 条 OpenRouter 时间序列数据")
        return results
    except Exception as e:
        logger.error(f"获取 OpenRouter 时间序列失败: {e}")
        return []


def fetch_openrouter_model_pricing() -> List[Dict]:
    try:
        models = fetch_openrouter_rankings()
        today = datetime.now().strftime("%Y-%m-%d")
        results = []
        for m in models:
            pricing = m.get("pricing", {})
            prompt_price = float(pricing.get("prompt", 0))
            completion_price = float(pricing.get("completion", 0))
            if prompt_price or completion_price:
                avg = (prompt_price + completion_price) / 2 if (prompt_price and completion_price) else (prompt_price or completion_price)
                results.append({
                    "source": "OpenRouter",
                    "metric": "API定价变动与速度对比",
                    "date": today,
                    "value": round(avg * 1000, 6),
                    "unit": "$/1K tokens",
                    "notes": f"{m.get('model', 'Unknown')} | in: ${prompt_price:.6f} | out: ${completion_price:.6f}",
                })
        logger.info(f"获取到 {len(results)} 条模型定价数据")
        return results
    except Exception as e:
        logger.error(f"获取模型定价失败: {e}")
        return []


# ============ GitHub 开发者趋势 ============

def fetch_github_trending() -> List[Dict]:
    bs4 = _try_import("bs4")
    if not bs4:
        logger.warning("beautifulsoup4 未安装，跳过 GitHub Trending")
        return []
    try:
        url = "https://github.com/trending"
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.text, "lxml")
        articles = soup.select("article.Box-row")
        today = datetime.now().strftime("%Y-%m-%d")
        results = []
        for article in articles[:25]:
            repo_link = article.select_one("h2 a")
            if not repo_link:
                continue
            repo_name = repo_link.get("href", "").strip("/")
            stars = 0
            for sl in article.select("a.Link--muted"):
                if "/stargazers" in sl.get("href", ""):
                    try:
                        stars = int(sl.get_text(strip=True).replace(",", ""))
                    except ValueError:
                        stars = 0
                    break
            desc_tag = article.select_one("p")
            description = desc_tag.get_text(strip=True)[:100] if desc_tag else ""
            lang_tag = article.select_one("span[itemprop='programmingLanguage']")
            language = lang_tag.get_text(strip=True) if lang_tag else ""
            results.append({
                "source": "GitHub Trending",
                "metric": "GitHub Trending仓库",
                "date": today,
                "value": stars,
                "unit": "stars",
                "notes": f"{repo_name} | {language} | {description}",
            })
        logger.info(f"获取到 {len(results)} 条 GitHub Trending 数据")
        return results
    except Exception as e:
        logger.error(f"获取 GitHub Trending 失败: {e}")
        return []


def fetch_ai_repos_stats() -> List[Dict]:
    ai_repos = [
        ("huggingface", "transformers", "Transformers"),
        ("pytorch", "pytorch", "PyTorch"),
        ("tensorflow", "tensorflow", "TensorFlow"),
        ("ollama", "ollama", "Ollama"),
        ("langchain-ai", "langchain", "LangChain"),
        ("microsoft", "autogen", "AutoGen"),
        ("microsoft", "onnxruntime", "ONNX Runtime"),
        ("python", "cpython", "CPython"),
    ]
    today = datetime.now().strftime("%Y-%m-%d")
    results = []
    for owner, repo, display in ai_repos:
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning(f"GitHub API {owner}/{repo} 返回 {resp.status_code}")
                continue
            data = resp.json()
            results.append({
                "source": "GitHub API",
                "metric": "AI热门仓库Stars",
                "date": today,
                "value": data.get("stargazers_count", 0),
                "unit": "stars",
                "notes": f"{display}({owner}/{repo}) | forks: {data.get('forks_count', 0)}",
            })
        except Exception as e:
            logger.error(f"获取 {owner}/{repo} 失败: {e}")
    logger.info(f"获取到 {len(results)} 条 AI 仓库数据")
    return results


# ============ EIA 电力数据（保留原有） ============

def fetch_eia_electricity_data() -> Optional[Dict]:
    api_key = os.environ.get("EIA_API_KEY", "")
    if not api_key:
        logger.warning("EIA API key 未设置，跳过电力数据获取")
        return None
    try:
        url = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"
        params = {
            "frequency": "daily",
            "data[0]": "value",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 10,
            "api_key": api_key,
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"获取 EIA 电力数据失败: {e}")
        return None


# ============ EIA 电力数据增强 ============

def fetch_eia_ai_electricity() -> List[Dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    results = []
    try:
        url = "https://www.eia.gov/todayinenergy/detail.php?id=61002"
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            bs4 = _try_import("bs4")
            if bs4:
                soup = bs4.BeautifulSoup(resp.text, "lxml")
                text = soup.get_text()
                matches = re.findall(r'([\d.]+)\s*(?:billion|million)?\s*kWh', text, re.IGNORECASE)
                for m in matches[:3]:
                    results.append({
                        "source": "EIA",
                        "metric": "数据中心用电增速vs电网新增产能",
                        "date": today,
                        "value": float(m),
                        "unit": "kWh",
                        "notes": "EIA 数据中心用电量估算",
                    })
    except Exception as e:
        logger.error(f"获取 EIA AI 电力数据失败: {e}")

    if not results:
        results.append({
            "source": "EIA/IEA 估算",
            "metric": "数据中心用电增速vs电网新增产能",
            "date": today,
            "value": 2.5,
            "unit": "%",
            "notes": "估算: 数据中心占美国用电 ~2.5%",
            "is_estimated": True,
        })
    logger.info(f"获取到 {len(results)} 条 AI 电力数据")
    return results


def fetch_eia_rate_trends() -> List[Dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    results = []
    api_key = os.environ.get("EIA_API_KEY", "")
    if api_key:
        try:
            url = "https://api.eia.gov/v2/electricity/wholesale-daily/region/data/"
            params = {
                "frequency": "daily",
                "data[0]": "price",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 30,
                "api_key": api_key,
            }
            resp = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                for pt in data.get("response", {}).get("data", []):
                    results.append({
                        "source": "EIA",
                        "metric": "美国电价趋势",
                        "date": pt.get("period", today),
                        "value": pt.get("price", 0),
                        "unit": "$/MWh",
                    })
        except Exception as e:
            logger.error(f"获取 EIA 电价数据失败: {e}")

    if not results:
        results.append({
            "source": "EIA 估算",
            "metric": "美国电价趋势",
            "date": today,
            "value": 35.0,
            "unit": "$/MWh",
            "notes": "美国工商业平均电价估算",
            "is_estimated": True,
        })
    logger.info(f"获取到 {len(results)} 条电价数据")
    return results


# ============ 行业公开数据 ============

def fetch_nvidia_earnings() -> List[Dict]:
    yf = _try_import("yfinance")
    if not yf:
        logger.warning("yfinance 未安装，跳过英伟达财报")
        return []
    try:
        ticker = yf.Ticker("NVDA")
        info = ticker.info
        today = datetime.now().strftime("%Y-%m-%d")
        results = []

        revenue = info.get("totalRevenue")
        if revenue:
            results.append({
                "source": "Yahoo Finance",
                "metric": "英伟达数据中心业务收入",
                "date": today,
                "value": round(revenue / 1e8, 2),
                "unit": "亿美元",
                "notes": f"NVDA 总营收: ${revenue/1e9:.2f}B",
            })

        pe = info.get("trailingPE") or info.get("forwardPE")
        if pe:
            results.append({
                "source": "Yahoo Finance",
                "metric": "NVDA市盈率",
                "date": today,
                "value": round(pe, 2),
                "unit": "x",
                "notes": f"NVDA PE: {pe:.1f}",
            })

        logger.info(f"获取到 {len(results)} 条英伟达财报数据")
        return results
    except Exception as e:
        logger.error(f"获取英伟达财报失败: {e}")
        return []


def fetch_cloud_pricing_changes() -> List[Dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    results = []
    providers = {
        "AWS": "https://aws.amazon.com/pricing/",
        "Azure": "https://azure.microsoft.com/pricing/",
        "GCP": "https://cloud.google.com/pricing",
    }
    for provider, url in providers.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            results.append({
                "source": f"{provider} Pricing",
                "metric": "API定价变动与速度对比",
                "date": today,
                "value": None,
                "unit": "",
                "notes": f"{provider} 定价页可访问: HTTP {resp.status_code}",
            })
        except Exception as e:
            results.append({
                "source": f"{provider} Pricing",
                "metric": "API定价变动与速度对比",
                "date": today,
                "value": None,
                "unit": "",
                "notes": f"{provider} 定价页访问失败: {str(e)[:100]}",
            })
    logger.info(f"获取到 {len(results)} 条云定价检查数据")
    return results


# ============ 统一接口 ============

_FETCHER_REGISTRY = [
    ("Yahoo Finance - NVDA", fetch_nvda_stock, "NVDA股价"),
    ("Yahoo Finance - Cloud", fetch_cloud_stocks, "MSFT股价"),
    ("Yahoo Finance - NASDAQ", fetch_nasdaq_ai_index, "NASDAQ100指数"),
    ("OpenRouter 排名", fetch_openrouter_rankings, None),
    ("OpenRouter Token趋势", fetch_openrouter_timeseries, "全行业Token消耗量"),
    ("OpenRouter 定价", fetch_openrouter_model_pricing, "API定价变动与速度对比"),
    ("GitHub Trending", fetch_github_trending, "GitHub Trending仓库"),
    ("GitHub AI仓库", fetch_ai_repos_stats, "AI热门仓库Stars"),
    ("EIA AI电力", fetch_eia_ai_electricity, "数据中心用电增速vs电网新增产能"),
    ("EIA 电价", fetch_eia_rate_trends, "美国电价趋势"),
    ("英伟达财报", fetch_nvidia_earnings, "英伟达数据中心业务收入"),
    ("云定价检查", fetch_cloud_pricing_changes, "API定价变动与速度对比"),
]


def auto_fetch_all() -> Dict:
    """
    执行所有自动数据获取，将数据写入数据库。
    返回获取结果摘要（兼容 scheduler.py 旧接口）。
    """
    summary = {
        "timestamp": datetime.now().isoformat(),
        "sources": {},
        "db_writes": 0,
        "errors": [],
        "openrouter": {"status": "skipped", "model_count": 0},
        "eia": {"status": "skipped"},
    }

    for name, fetcher_fn, metric_name in _FETCHER_REGISTRY:
        try:
            raw = fetcher_fn()
            if not raw:
                summary["sources"][name] = {"status": "no_data"}
                continue

            if metric_name:
                save_fetched_to_db(metric_name, raw)
                summary["db_writes"] += len(raw)

            summary["sources"][name] = {
                "status": "success",
                "data_points": len(raw),
                "sample": raw[:2],
            }

            if name == "OpenRouter 排名":
                summary["openrouter"] = {
                    "model_count": len(raw),
                    "top_models": raw[:10],
                    "status": "success",
                }
            elif name in ("EIA AI 电力", "EIA 电价"):
                summary["eia"] = {"status": "success", "data_points": len(raw)}

        except Exception as e:
            summary["errors"].append(f"{name}: {e}")
            summary["sources"][name] = {"status": "error"}

    return summary