#!/usr/bin/env python3
"""
招聘公告爬虫 v3（云端版主爬虫）
抓取方式：requests + BeautifulSoup（服务端渲染站点）
覆盖：国航、进出口银行、中国信保官网
可选合并：crawler_js.py 输出的 js_results.json（中信/中化学等 JS 渲染站点）
输出：announcements.js（网站直接 <script> 加载）
设计：每日运行（GitHub Actions 定时 / 本地 launchd 均可），失败站点自动跳过不影响整体
"""

import json
import re
import os
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("缺少依赖，请先安装：pip3 install requests beautifulsoup4")
    sys.exit(1)

# ============ 配置 ============
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JS = os.path.join(OUTPUT_DIR, "announcements.js")
JS_RESULTS = os.path.join(OUTPUT_DIR, "js_results.json")  # crawler_js.py 的产物
TIMEOUT = 15
MAX_ITEMS_PER_SITE = 8
CURRENT_YEAR = datetime.now().year
MIN_YEAR = CURRENT_YEAR - 1  # 只保留近两年的公告

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 标题必须包含的词（像公告的标题）
POSITIVE_PAT = re.compile(r"(公告|简章|启事|通知|宣讲会|招聘|招录)")
# 标题包含即排除（导航栏、表单、栏目名）
NEGATIVE_PAT = re.compile(
    r"(首页|登录|注册|登记表|报名表|申请表|简历|更多|流程|指南|"
    r"常见问题|联系我们|网站地图|政策法规|人才理念|培训|福利待遇$|"
    r"^(飞行员|乘务员|地面人员|实习生|社会招聘|校园招聘)$)"
)

# 服务端渲染站点（可直接抓取）
SITES = [
    {
        "name": "国航招聘",
        "urls": ["https://zhaopin.airchina.com.cn/"],
        "base_url": "https://zhaopin.airchina.com.cn",
    },
    {
        "name": "进出口银行",
        "urls": ["http://www.eximbank.gov.cn/info/notice/recruit/"],
        "base_url": "http://www.eximbank.gov.cn",
    },
    {
        "name": "中国信保",
        "urls": ["https://www.sinosure.com.cn/rczp/"],
        "base_url": "https://www.sinosure.com.cn",
    },
]

# JS 动态渲染 / 反爬站点：由 crawler_js.py（浏览器渲染）尝试，或作为网站上的手动入口
MANUAL_SITES = [
    {"name": "中信集团网申", "url": "https://job.citic.com/", "reason": "职位列表每日自动抓取，网申需登录"},
    {"name": "中国信保网申", "url": "https://sinosure.zhiye.com/", "reason": "官网公告已自动抓取，网申入口"},
    {"name": "中石油", "url": "https://zhaopin.cnpc.com.cn/", "reason": "反爬拦截，需手动查看"},
    {"name": "国聘 iguopin", "url": "https://www.iguopin.com", "reason": "央企国企公告聚合平台（三桶油/两网/烟草等），JS渲染需手动查看"},
    {"name": "北大就业中心", "url": "https://scc.pku.edu.cn", "reason": "北大宣讲/经验分享/选调与国际组织专栏，列表为JS动态渲染"},
    {"name": "北大选调生专栏", "url": "https://scc.pku.edu.cn/frontpage/pku/html/xds_index.html", "reason": "各省面向北大定向选调公告入口"},
    {"name": "北大国际组织专栏", "url": "https://scc.pku.edu.cn/frontpage/pku/html/gjzz_index.html", "reason": "UNDP/JPO等国际组织推送信息"},
    {"name": "中海油", "url": "https://zhaopin.cnooc.com", "reason": "网申需登录，公告手动查看"},
]


def fetch_html(url):
    """获取页面 HTML，自动重试"""
    for attempt in range(2):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            print(f"    ✗ HTTP {code} [{url}]")
            if code == 502 and attempt == 0:
                time.sleep(2)
                continue
            return None
        except Exception as e:
            print(f"    ✗ 获取失败 [{url}]: {e}")
            return None
    return None


def is_valid_title(title):
    """判断是否为真实公告标题"""
    if len(title) < 8 or len(title) > 120:
        return False
    if not POSITIVE_PAT.search(title):
        return False
    if NEGATIVE_PAT.search(title):
        return False
    return True


def extract_date(title, element):
    """从标题或周边文本提取日期"""
    patterns = [
        r"(\d{4})-(\d{1,2})-(\d{1,2})",
        r"(\d{4})[年/](\d{1,2})[月/](\d{1,2})",
        r"(\d{4})[年/](\d{1,2})",
    ]
    for pat in patterns:
        m = re.search(pat, title)
        if m:
            g = m.groups()
            if len(g) >= 3:
                return f"{g[0]}-{int(g[1]):02d}-{int(g[2]):02d}"
            return f"{g[0]}-{int(g[1]):02d}-01"

    parent = element.find_parent()
    if parent:
        text = parent.get_text(" ", strip=True)
        m = re.search(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", text)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    return datetime.now().strftime("%Y-%m-%d")


def parse_announcements(html, site_config):
    """解析公告列表"""
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    items = []
    seen = set()

    for link in links:
        title = link.get_text(strip=True)
        href = link.get("href", "")

        if not is_valid_title(title):
            continue
        if title in seen:
            continue
        seen.add(title)

        if href and not href.startswith("http"):
            href = urljoin(site_config["base_url"], href)

        # 年份过滤：标题中明确过老的跳过；无年份的保留
        year_match = re.search(r"(20\d{2})", title)
        if year_match and int(year_match.group(1)) < MIN_YEAR:
            continue

        date_str = extract_date(title, link)
        if int(date_str[:4]) < MIN_YEAR:
            continue

        items.append({
            "title": title,
            "source": site_config["name"],
            "date": date_str,
            "url": href,
        })

        if len(items) >= MAX_ITEMS_PER_SITE:
            break

    return items


def load_js_results():
    """合并 crawler_js.py（浏览器渲染站点）的输出"""
    if not os.path.exists(JS_RESULTS):
        return []
    try:
        with open(JS_RESULTS, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
        print(f"\n🔀 合并 JS 渲染结果: {len(items)} 条")
        return items
    except Exception as e:
        print(f"⚠️ js_results.json 读取失败（忽略）: {e}")
        return []


def write_js(data):
    js_content = "// 自动生成，请勿手动修改\n// 生成时间: {}\n\nconst ANNOUNCEMENTS_DATA = {};\n".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        json.dumps(data, ensure_ascii=False, indent=2)
    )
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"\n✅ 数据已写入: {OUTPUT_JS}")
    print(f"   共 {len(data['items'])} 条公告")


def main():
    print("=" * 50)
    print("招聘公告爬虫 v3 启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    all_items = []
    site_stats = {}

    for site in SITES:
        print(f"\n📡 正在抓取: {site['name']}")
        site_items = []
        for url in site["urls"]:
            print(f"   尝试: {url}")
            html = fetch_html(url)
            if html:
                items = parse_announcements(html, site)
                print(f"     → 提取到 {len(items)} 条有效公告")
                site_items.extend(items)
                if len(site_items) >= MAX_ITEMS_PER_SITE:
                    break
            time.sleep(1)  # 礼貌性间隔

        # 站内去重
        unique = []
        seen_titles = set()
        for it in site_items:
            if it["title"] not in seen_titles:
                seen_titles.add(it["title"])
                unique.append(it)
        unique = unique[:MAX_ITEMS_PER_SITE]

        site_stats[site["name"]] = len(unique)
        all_items.extend(unique)
        print(f"   ✔ {site['name']}: 共 {len(unique)} 条")

    # 合并浏览器渲染结果（中信/中化学等）
    all_items.extend(load_js_results())

    # 全局去重 + 排序
    seen = set()
    final_items = []
    for it in sorted(all_items, key=lambda x: x["date"], reverse=True):
        key = (it["source"], it["title"])
        if key not in seen:
            seen.add(key)
            final_items.append(it)

    # 每个来源最多保留 8 条，防止单一来源（如中信职位流）刷屏挤掉其他公告
    MAX_PER_SOURCE = 8
    per_source = {}
    capped = []
    for it in final_items:  # 已按日期倒序
        c = per_source.get(it["source"], 0)
        if c >= MAX_PER_SOURCE:
            continue
        per_source[it["source"]] = c + 1
        capped.append(it)
    final_items = capped

    data = {
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(final_items),
        "items": final_items,
        "manualSites": MANUAL_SITES,
    }

    write_js(data)

    print("\n📊 各站点统计:")
    for name, n in site_stats.items():
        print(f"   {'✅' if n > 0 else '⚠️ '} {name}: {n} 条")
    print("\n🏁 爬虫运行完毕")


if __name__ == "__main__":
    main()
