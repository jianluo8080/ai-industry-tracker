"""
定时数据同步调度器：周期性获取数据并检测信号。

用法:
    python scheduler.py                  # 每小时同步一次（默认60分钟）
    python scheduler.py --interval 30    # 每30分钟同步一次
    python scheduler.py --once           # 只运行一次
"""

import sys
import os
import time
import signal
import logging
import argparse
from datetime import datetime

import fetchers
import analysis

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "scheduler.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("scheduler")
logger.setLevel(logging.DEBUG)

log_fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(log_fmt)
logger.addHandler(fh)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(log_fmt)
logger.addHandler(ch)


def run_once():
    logger.info("=" * 50)
    logger.info("开始执行数据同步任务")
    logger.info("=" * 50)

    step = 1
    total_steps = 2

    # ---- Step 1: 数据获取 ----
    logger.info("[%d/%d] 正在获取数据 (fetchers.auto_fetch_all) ...", step, total_steps)
    print(f"\n[{_now_str()}] Step {step}/{total_steps}: 正在从 OpenRouter 等来源获取数据...")
    try:
        fetch_result = fetchers.auto_fetch_all()
        or_info = fetch_result.get("openrouter", {})
        eia_info = fetch_result.get("eia", {})
        errors = fetch_result.get("errors", [])

        model_count = or_info.get("model_count", 0) if or_info else 0
        or_status = or_info.get("status", "unknown") if or_info else "unknown"
        eia_status = eia_info.get("status", "unknown") if eia_info else "unknown"

        logger.info("数据获取完成: OpenRouter=%s (模型数=%d), EIA=%s, 错误=%d",
                    or_status, model_count, eia_status, len(errors))
        print(f"    ✓ OpenRouter: {or_status} ({model_count} 个模型)")
        print(f"    ✓ EIA: {eia_status}")
        if errors:
            for err in errors:
                print(f"    ⚠ 错误: {err}")
                logger.warning("数据获取错误: %s", err)
        print(f"    数据获取完成 ✓")
    except Exception as e:
        logger.error("数据获取异常: %s", e)
        print(f"    ✗ 数据获取异常: {e}")
        fetch_result = {"errors": [str(e)]}

    step += 1

    # ---- Step 2: 信号检测 ----
    logger.info("[%d/%d] 正在检测信号 (analysis.check_all_signals) ...", step, total_steps)
    print(f"\n[{_now_str()}] Step {step}/{total_steps}: 正在执行信号检测...")
    try:
        triggered = analysis.check_all_signals()
        if triggered:
            logger.warning("检测到 %d 个触发信号", len(triggered))
            print(f"    ⚠ 检测到 {len(triggered)} 个触发信号:")
            for sig in triggered:
                level = sig.get("level", "-")
                name = sig.get("rule_name", "-")
                ind_name = sig.get("indicator_name", "-")
                val = sig.get("trigger_value", "-")
                threshold = sig.get("threshold", "-")
                print(f"      [{level}] {name}: {ind_name} = {val} (阈值: {threshold})")
                logger.warning("触发信号: [%s] %s - %s = %s (阈值: %s)",
                               level, name, ind_name, val, threshold)
        else:
            logger.info("未检测到新触发信号")
            print(f"    ✓ 未检测到新触发信号")
    except Exception as e:
        logger.error("信号检测异常: %s", e)
        print(f"    ✗ 信号检测异常: {e}")
        triggered = []

    # ---- Summary ----
    health = None
    try:
        health = analysis.compute_health_score()
        logger.info("健康度评分: %d/100 (%s)", health["score"], health["status"])
        print(f"\n[{_now_str()}] 健康度: {health['score']}/100 ({health['status']}) {health['emoji']}")
        print(f"    领先信号: {health['leading_signals']} | 同步: {health['sync_signals']} | 滞后: {health['lagging_signals']}")
        print(f"    建议: {health['recommendation']}")
    except Exception as e:
        logger.error("健康度计算异常: %s", e)

    logger.info("本次同步任务完成\n")
    print(f"\n[{_now_str()}] 本次同步任务完成 ✓\n")

    return {
        "fetch": fetch_result,
        "signals": triggered,
        "health": health,
        "timestamp": datetime.now().isoformat(),
    }


def run_scheduler(interval_minutes: int):
    logger.info("调度器启动，同步间隔: %d 分钟", interval_minutes)
    print(f"╔══════════════════════════════════════════════╗")
    print(f"║   AI 产业数据同步调度器                      ║")
    print(f"║   同步间隔: 每 {interval_minutes} 分钟        ║")
    print(f"║   日志文件: {LOG_FILE}")
    print(f"║   按 Ctrl+C 停止                             ║")
    print(f"╚══════════════════════════════════════════════╝")
    print()

    run_count = 0
    next_run = datetime.now()

    while True:
        try:
            now = datetime.now()
            if now >= next_run:
                run_count += 1
                print(f"--- 第 {run_count} 次同步 (共运行 {_elapsed_str()}) ---")
                try:
                    run_once()
                except Exception as e:
                    logger.error("同步任务异常: %s", e)
                    print(f"  ✗ 同步任务异常: {e}")

                next_run = datetime.now() + _minutes_delta(interval_minutes)

            remaining = (next_run - datetime.now()).total_seconds()
            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                if mins > 0:
                    time.sleep(min(remaining, 60))
                else:
                    time.sleep(max(remaining, 1))
            else:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("调度器被用户中断")
            print(f"\n\n[{_now_str()}] 调度器已停止 (共运行 {run_count} 次同步)")
            print(f"    总运行时长: {_elapsed_str()}")
            print(f"    再见 👋\n")
            break
        except Exception as e:
            logger.error("调度器异常: %s", e)
            print(f"    调度器异常: {e}")
            time.sleep(10)


def _now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _minutes_delta(minutes: int):
    from datetime import timedelta
    return timedelta(minutes=minutes)


_start_time = datetime.now()


def _elapsed_str():
    delta = datetime.now() - _start_time
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    parts.append(f"{seconds}秒")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="AI 产业数据同步调度器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scheduler.py                    # 每60分钟同步一次
  python scheduler.py --interval 30      # 每30分钟同步一次
  python scheduler.py --once             # 立即执行一次后退出
        """,
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="同步间隔（分钟），默认60分钟",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        default=False,
        help="只运行一次后退出",
    )
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval 必须为正整数")

    if args.once:
        _start_time = datetime.now()
        run_once()
    else:
        run_scheduler(args.interval)


if __name__ == "__main__":
    main()