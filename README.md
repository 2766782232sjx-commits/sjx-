# 我的未来式我做主 · 2027届（校招中控台）

线上地址：https://2766782232sjx-commits.github.io/sjx-/

纯静态 SPA：`index.html`（全部逻辑内联）+ `data.js`（岗位库约512条）+ `announcements.js`（公告）+ `backup.json`（云端备份）。无后端、无依赖，GitHub Pages 直接托管。

## 一、你的数据存在哪（换电脑前必读）

投递状态、经验贴收藏、随手记、模拟考成绩、手动加的岗位等，全部存在**浏览器 localStorage**（键名 `hub-*`），不在仓库里。换电脑/换浏览器/清缓存后，新浏览器里是空的。

## 二、云端备份与恢复（backup.json）

**备份（建议每1-2周一次）：**

1. 打开网站 → 档案室 → 点「☁️ 复制备份JSON」（数据已进剪贴板）
2. 浏览器打开 GitHub 仓库根目录的 `backup.json` → 点铅笔图标编辑
3. 全选删掉旧内容 → 粘贴刚复制的内容 → Commit changes
4. 完成后 GitHub Pages 约一分钟内更新

**恢复（自动）：** 任何新电脑/新浏览器首次打开网站时，会自动拉取 `backup.json`，本地没有的键会自动写入并刷新页面——无需任何手动操作。注意：只补空缺、不覆盖，本地已有记录时以本地为准（所以换电脑后第一次打开别急着记新东西，先确认旧数据回来了）。

**应急导入：** 也可以用网站顶栏「⬇ 导出」下载 JSON 文件，再通过顶栏「导入」按钮选文件恢复（此方式会整体覆盖）。

## 三、给 AI 助手的收录规范（换 AI 工具后把本节给它看）

用户会粘贴 BBS/论坛长文，按以下既定格式「收录+提炼」：

### 收录（SEED_XPS，index.html 顶部 `const SEED_XPS = [...]` 数组末尾追加）

- 按末尾已有条目同构追加：`{t:'标题', src:'校园BBS', time:'发帖YYYY-MM-DD(至MM-DD)', url:'bbs://job/2026-xxx-slug', note:'摘要', g:'分组', saved:'YYYY-MM-DD记录'}`
- 原帖无链接时 `url` 用 `bbs://` 伪链接（SEED_XPS 按 url 去重，伪链接安全）
- `g` 取值参考已有条目：综合/国央企/选调/国考/外企·国际组织/北大内部/女生视角 等

### 提炼（岗位库视图的情报卡）

在 index.html `vJobs` 视图中，现有卡片顺序：🔥竞争激烈程度 → 🧭体制内性价比情报（#5D4037）→ 🧯国企/京户/选调避坑情报（#00695C）→ 💰央国企定价与生存FAQ（#4A148C）→ `${catStrategyHtml()}` → ➕手动加岗位表单 → `#joblist`。

新情报可追加为新的 `<details class="card" style="border-left:4px solid 颜色">` 卡（放在 💰 卡之后、`${catStrategyHtml()}` 之前），或并入最相关的现有卡。条目格式：`<div style="border-bottom:1px dashed var(--line);padding:7px 0"><b>emoji 标题：</b>正文（关键处用 <b> 加粗）</div>`，最后一条去掉 border-bottom。卡片默认折叠。

### 验证与发布流程

1. `python3 -c "import re;html=open('index.html',encoding='utf-8').read();open('/tmp/_c.js','w',encoding='utf-8').write(''.join(re.findall(r'<script>(.*?)</script>',html,re.S)))"` 然后 `node --check /tmp/_c.js`
2. `python3 -m http.server 8773` 本地起服，浏览器点进各视图（nav 的 `data-v` 键：dash/jobs/apps/sched/xp/notes/gk/ann/arch）实测，details 卡需 `.open=true` 后再读 textContent
3. `git add index.html && git commit -m "..."`
4. 用户用 GitHub Desktop push（终端无凭据），浏览器 Cmd+Shift+R 强刷

### 已完成的收录批次

- `4ee9033` 俱新《泛文科择业杂谈十七》（知乎长文）
- `f5fe3ae` BBS「央国企 or 逼自己大厂算法」（2026-08-20~25）
- `abe6bae` BBS 体制内五帖合集（京户/萝卜坑/维权/生存法则/选调回家乡）
- `d00c396` BBS 第三批大合集（找工七关方法论 + 体制内问答12帖）

## 四、本项目无隐私顾虑说明

`backup.json` 会随仓库公开。内容仅含求职记录（公司/岗位/状态/笔记），如某天不想公开，可将仓库转为 Private（GitHub Pages 免费版对私有仓库有限制，需改用其他静态托管或保持公开但减少备份频率）。
