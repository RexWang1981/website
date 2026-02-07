# -*- coding: utf-8 -*-
"""
查询股票 - 根据 chekstock.md 说明实现
1. A股大盘信息 -> 表格 + 图表
2. 微光股份 当前股价与过去一年变动 -> 表格 + 图表
"""

import os
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def task1_market_index():
    """1. 网络获取A股大盘信息，表格+图表"""
    print("=" * 50)
    print("【任务1】A股大盘指数")
    print("=" * 50)

    df = ak.stock_zh_index_spot_em()
    # 筛选常见大盘指数
    keywords = ["上证", "深证", "创业板", "科创", "沪深300", "中证500", "北证"]
    mask = df["名称"].str.contains("|".join(keywords), na=False)
    main = df[mask].head(12).copy()
    main = main[["名称", "最新价", "涨跌幅", "涨跌额", "成交量", "成交额"]]
    main.columns = ["指数名称", "最新价", "涨跌幅(%)", "涨跌额", "成交量", "成交额"]
    main["涨跌幅(%)"] = main["涨跌幅(%)"].round(2)
    main["成交额"] = (main["成交额"] / 1e8).round(2)
    main["成交额"] = main["成交额"].astype(str) + "亿"

    # 表格 -> CSV
    path_table = os.path.join(OUTPUT_DIR, "a_share_market_index.csv")
    main.to_csv(path_table, index=False, encoding="utf-8-sig")
    print(f"表格已保存: {path_table}")
    print(main.to_string(index=False))

    # 图表：主要指数最新价 + 涨跌幅
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    plot_df = main.head(8)

    ax1 = axes[0]
    bars = ax1.barh(plot_df["指数名称"], plot_df["最新价"], color="steelblue", alpha=0.8)
    ax1.set_xlabel("最新价")
    ax1.set_title("A股主要指数 - 最新价")
    ax1.invert_yaxis()

    ax2 = axes[1]
    colors = ["green" if x >= 0 else "red" for x in plot_df["涨跌幅(%)"]]
    ax2.barh(plot_df["指数名称"], plot_df["涨跌幅(%)"], color=colors, alpha=0.8)
    ax2.axvline(0, color="black", linewidth=0.5)
    ax2.set_xlabel("涨跌幅 (%)")
    ax2.set_title("A股主要指数 - 涨跌幅")
    ax2.invert_yaxis()

    plt.tight_layout()
    path_chart = os.path.join(OUTPUT_DIR, "a_share_market_index.png")
    plt.savefig(path_chart, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"图表已保存: {path_chart}\n")


def task2_weiguang():
    """2. 微光股份：当前股价 + 过去一年变动，表格+图表"""
    print("=" * 50)
    print("【任务2】微光股份 (002801)")
    print("=" * 50)

    symbol = "002801"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    hist = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_str, end_date=end_str, adjust="qfq")
    if hist is None or hist.empty:
        print("未获取到微光股份历史数据，请检查网络或代码。")
        return

    hist = hist.rename(columns={
        "日期": "日期",
        "开盘": "开盘",
        "收盘": "收盘",
        "最高": "最高",
        "最低": "最低",
        "成交量": "成交量",
        "成交额": "成交额",
        "振幅": "振幅",
        "涨跌幅": "涨跌幅",
        "涨跌额": "涨跌额",
        "换手率": "换手率",
    })
    hist["日期"] = pd.to_datetime(hist["日期"]).dt.strftime("%Y-%m-%d")

    # 当前股价：取最近交易日收盘价
    latest = hist.iloc[-1]
    current_price = latest["收盘"]
    current_date = latest["日期"]

    # 摘要表格：首日、最新、一年涨跌幅等
    first = hist.iloc[0]
    yearly_change = (current_price - first["收盘"]) / first["收盘"] * 100
    summary = pd.DataFrame([
        {"项目": "股票", "数值": "微光股份 (002801)"},
        {"项目": "数据截止日期", "数值": current_date},
        {"项目": "当前股价(元)", "数值": f"{current_price:.2f}"},
        {"项目": "一年前收盘(元)", "数值": f"{first['收盘']:.2f}"},
        {"项目": "过去一年涨跌幅(%)", "数值": f"{yearly_change:.2f}"},
    ])

    path_summary = os.path.join(OUTPUT_DIR, "weiguang_summary.csv")
    summary.to_csv(path_summary, index=False, encoding="utf-8-sig")
    print(f"摘要表格已保存: {path_summary}")
    print(summary.to_string(index=False))

    # 历史明细表（最近60个交易日 + 关键节点）
    recent = hist.tail(60)[["日期", "开盘", "收盘", "最高", "最低", "成交量", "涨跌幅"]].copy()
    recent["涨跌幅"] = recent["涨跌幅"].round(2)
    path_hist = os.path.join(OUTPUT_DIR, "weiguang_hist.csv")
    recent.to_csv(path_hist, index=False, encoding="utf-8-sig")
    print(f"历史明细表(最近60日)已保存: {path_hist}")

    # 图表1：过去一年收盘价走势
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    hist_plot = hist.copy()
    hist_plot["日期"] = pd.to_datetime(hist_plot["日期"])

    ax1 = axes[0]
    ax1.plot(hist_plot["日期"], hist_plot["收盘"], color="steelblue", linewidth=1.5, label="收盘价")
    ax1.fill_between(hist_plot["日期"], hist_plot["最低"], hist_plot["最高"], alpha=0.2, color="steelblue")
    ax1.set_ylabel("价格 (元)")
    ax1.set_title("微光股份 (002801) 过去一年股价走势")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # 图表2：涨跌幅分布
    ax2 = axes[1]
    ax2.bar(hist_plot["日期"], hist_plot["涨跌幅"], color=["green" if x >= 0 else "red" for x in hist_plot["涨跌幅"]], alpha=0.7, width=1)
    ax2.axhline(0, color="black", linewidth=0.5)
    ax2.set_xlabel("日期")
    ax2.set_ylabel("涨跌幅 (%)")
    ax2.set_title("微光股份 (002801) 过去一年日涨跌幅")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path_chart = os.path.join(OUTPUT_DIR, "weiguang_chart.png")
    plt.savefig(path_chart, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"图表已保存: {path_chart}\n")


if __name__ == "__main__":
    task1_market_index()
    task2_weiguang()
    print("全部完成。结果见 check_srock/output/ 目录。")
