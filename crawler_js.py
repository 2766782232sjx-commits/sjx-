#!/usr/bin/env python3
"""
JS 渲染站点爬虫（Playwright 浏览器渲染）
覆盖：中信集团校招职位列表、中化学（国聘）校招职位列表
输出：js_results.json —— 由 crawler.py 合并进 announcements.js

运行前提：pip3 install playwright && playwright install chromium
在 GitHub Actions 中由 daily-update.yml 自动安装并运行；
单个站点失败不会中断整体（继续抓下一个）。
"""

import json
import re
import os
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("缺少 playwright，请先安装：pip3 install playwright && playwright install chromium")
    raise SystemExit(0)

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "js_results.json")
TODAY = datetime.now().strftime("%Y-%m-%d")


def crawl_citic(page):
    """中信集团校招职位：job.citic.com（Angular SPA）
    流程：打开 → 同意声明 → hover 校园招聘 → 点「应届生」→ 提取职位名第一列"""
    page.goto("https://job.citic.com/recruit", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)

    # 关闭「温馨提示」声明弹窗
    try:
        page.get_by_text("我已阅读并同意", exact=True).first.click(timeout=8000)
        page.wait_for_timeout(2000)
    except Exception:
        pass

    # 校园招聘 → 应届生（需先 hover 展开下拉）
    try:
        page.get_by_text("校园招聘", exact=True).first.hover(timeout=8000)
        page.wait_for_timeout(1200)
        page.get_by_text("应届生", exact=True).first.click(timeout=8000)
        page.wait_for_timeout(6000)
    except Exception:
        pass

    items = []
    try:
        cells = page.locator('.virtual-scroll-container .table-cell[col-key="name"] .cell-content')
        n = min(cells.count(), 15)
        titles = []
        for i in range(n):
            t = cells.nth(i).inner_text().strip()
            if t and len(t) >= 4:
                titles.append(t)
        total_m = re.search(r"新的机会\s*\((\d+)\)", page.inner_text("body"))
        total = total_m.group(1) if total_m else str(len(titles))
        for t in titles:
            items.append({
                "title": f"中信校招在招职位（共{total}个）· {t}",
                "source": "中信集团",
                "date": TODAY,
                "url": "https://job.citic.com/recruit#/index",
            })
        print(f"   ✔ 中信集团: {len(items)} 条（总职位数 {total}）")
    except Exception as e:
        print(f"   ⚠️ 中信提取失败: {e}")
    return items


def crawl_cncec(page):
    """中化学（国聘子站）校招职位：cncec.iguopin.com/job（React + antd）
    职位卡片 class=.jobCard，首行为岗位名"""
    page.goto("https://cncec.iguopin.com/job", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)

    items = []
    try:
        cards = page.locator(".jobCard")
        n = min(cards.count(), 15)
        for i in range(n):
            txt = cards.nth(i).inner_text().strip()
            first = txt.split("\n")[0].strip() if txt else ""
            if first and len(first) >= 3:
                items.append({
                    "title": f"中化学校招在招岗位 · {first}",
                    "source": "中化学国际",
                    "date": TODAY,
                    "url": "https://cncec.iguopin.com/job",
                })
        print(f"   ✔ 中化学国际: {len(items)} 条")
    except Exception as e:
        print(f"   ⚠️ 中化学提取失败: {e}")
    return items


def main():
    print("=" * 50)
    print("JS 渲染站点爬虫启动（Playwright）")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    all_items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN",
            viewport={"width": 1470, "height": 956},
        )
        page = ctx.new_page()

        for name, fn in [("中信集团", crawl_citic), ("中化学国际", crawl_cncec)]:
            print(f"\n📡 正在抓取: {name}")
            try:
                all_items.extend(fn(page))
            except Exception as e:
                print(f"   ⚠️ {name} 整体失败（跳过）: {type(e).__name__} {e}")
            page.wait_for_timeout(2000)

        browser.close()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"date": TODAY, "items": all_items}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 写入 {OUTPUT}（{len(all_items)} 条）")


if __name__ == "__main__":
    main()
