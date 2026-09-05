# 校招中控台（云端版）

一个**纯静态**的校招信息中枢网站：不需要服务器、不需要数据库、不需要写代码就能长期维护。

组成：

| 文件 | 作用 |
|---|---|
| `index.html` | 网站本体（岗位库/投递追踪/日程冲突预警/经验贴/随手记/最新公告/数据导出导入） |
| `data.js` | 你专属的岗位数据库（26 个岗位，每年手动小更新） |
| `crawler.py` | 主爬虫：国航、进出口银行、中国信保官网（服务端渲染站点） |
| `crawler_js.py` | 浏览器渲染爬虫：中信集团、中化学（国聘）的校招职位列表 |
| `.github/workflows/daily-update.yml` | GitHub Actions：**每天早上 8:30（北京时间）自动抓取**并更新公告 |
| `announcements.js` | 爬虫产物，网站自动读取最新公告 |

---

## 一、一次部署（约 10 分钟，全程网页操作）

1. 注册/登录 [github.com](https://github.com)。
2. 右上角 **+** → **New repository**：
   - 名称随意（如 `campus-hub`），选 **Public**（Public 才能免费用 GitHub Pages + Actions）；
   - 勾选 "Add a README file" → **Create repository**。
3. 仓库页 **Add file → Upload files**，把本文件夹里的这几样全部拖进去：
   `index.html`、`data.js`、`crawler.py`、`crawler_js.py`、`announcements.js`，
   以及 `.github` 文件夹（macOS 里 `.github` 是隐藏文件夹，按 `Cmd+Shift+.` 显示隐藏文件）。
   → **Commit changes**。
4. 开启定时抓取：仓库顶部 **Actions** 标签 → 左侧「每日更新招聘公告」→ 黄色横幅点 **Enable workflows**（如果有的话）→ 右侧 **Run workflow** 手动跑一次验证。
5. 开启网站：**Settings → Pages** → Source 选 `Deploy from a branch`，Branch 选 `main` / `(root)` → **Save**。一分钟后，`https://你的用户名.github.io/campus-hub/` 就是你的云端网站。

以后**每天早上 Actions 自动抓公告 → 网站自动展示最新信息**，你什么都不用做。

## 二、日常维护（三件事，都很轻）

### 1. 你的投递/日程/笔记数据
存在浏览器 localStorage，跟着浏览器走。换电脑时用网站里自带的
**「导出数据」按钮**（总览页右上角）下载备份文件，再到新设备的网站上点**「导入数据」**即可，不用碰任何代码。

### 2. 岗位库截止日期（每年约 30 分钟）
`data.js` 就是一张"表格"，直接在 GitHub 网页上改：打开文件 → 铅笔图标 → 把
`dl: '2026-11-23'` 这类日期改成今年的 → Commit。或者在手机上让 AI（如 CatPaw）
帮你生成新的 data.js，整段替换。

### 3. 想加新公司/新来源
- 在 `crawler.py` 的 `SITES` 里加一个网址（照葫芦画瓢）；
- 或者直接问 AI："帮我在 crawler.py 加上 XXX 公司的招聘页抓取"。

## 三、常见问题

- **Actions 跑了但没提交**：正常，当天没有新公告就不会产生提交；点进 Actions 里看运行日志确认各站点抓到几条。
- **某个站点连续多天 0 条**：对方改版了，把运行日志发给 AI 帮你修对应函数即可。
- **免费额度**：Public 仓库的 Actions 与 Pages 对个人免费，每日一次爬虫远在免费额度内。
- **想彻底私有**：Private 仓库每月也有 2000 分钟免费 Actions 额度（每天一次爬虫约用 2 分钟），但 Pages 在 Free 账户下需要 Public，按需取舍。

## 四、本地运行（可选）

```bash
pip3 install requests beautifulsoup4
python3 crawler.py          # 仅 SSR 站点

pip3 install playwright && playwright install chromium
python3 crawler_js.py       # 浏览器渲染站点（中信/中化学）
python3 crawler.py          # 再跑一次，自动合并 js_results.json
```

本地定时（macOS launchd）见上一级目录的 `com.shejiaxin.soe-crawler.plist`；部署到 GitHub 后其实已经不需要它了。
