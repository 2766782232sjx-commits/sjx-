# 我的未来式我做主 · 2027届（校招中控台）

线上地址：https://2766782232sjx-commits.github.io/sjx-/

纯静态 SPA：`index.html`（全部逻辑内联）+ `data.js`（岗位库614条）+ `announcements.js`（公告）+ `backup.json`（云端备份）。无后端、无依赖，GitHub Pages 直接托管。

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
- 2026-09-06 大版本：BBS找工作版爬取30页筛出289条真实offer/避坑帖建成 CASE_LIB（总览「上岸实证」卡分组折叠、点标题直达原帖）；新增简历画像卡、考查流程卡、最值得去岗位卡；行测题型方法表、申论板块、错题集（新键 `hub-gk-wrong`，已同步备份/恢复/档案室）；选调时间线按2027届最新公告核实更新（上海/黑龙江9月初已启动）；站名改为「SJX的校招准备网站」
- 2026-09-06 增量：总览新增「人生经验贴」卡（小红书真实转折案例4组带搜索直达链接+BBS前辈经验贴12篇+行业稳定性长期账·日美中对照）；「我的底牌」并入简历画像卡为「行业匹配速查」区块，标签改为白底描边样式提升可读性
- 2026-09-06 岗位库大扩容：512→614条（+102）。事业单位/国际组织 st 40→76（+国务院发展研究中心/中央党史文献研究院/上国研/外交学会/博鳌秘书处/上合秘书处/新开发银行/UNICEF等驻华机构/中外合办大学/思政课教师/深圳教师编等）；外企 wq 40→71（+谷歌/英伟达政府事务岗、空客波音、日本五大商社、外资投行、优衣库UMC/历峰/耐克/星巴克/麦当劳/百胜等管培）；快消 kj 26→61（+蒙牛伊利青啤/嘉吉路易达孚大宗贸易/珀莱雅/老铺黄金/元气东鹰库迪出海线等）
- `a26b08f` BBS 部委问答楼2025-26新鲜情报（爬取2638楼筛选211条）
- `6bc5667` BBS 省烟草vs省属国资PE
- 爬虫固定能力建立后首战：2026-09秋招新鲜四帖（央企调岗/被裁出路/国企副业/文科薪资）

## 四、BBS爬虫固定能力（任何AI助手照此可爬）

前提：需要已登录的浏览器（北大未名BBS需校园网/VPN+账号登录态）。以下JS在任一已登录的 bbs.pku.edu.cn 页面控制台或 browser-action evaluate 中执行。

### 1. 拉取版面主题帖列表

```js
(async () => {
  const bid = 99; // 版面号：99=找工作啦Job，其他版面号从版面URL取
  const r = await fetch(`https://bbs.pku.edu.cn/v2/thread.php?bid=${bid}&mode=topic&page=1`, {credentials: 'include'});
  const html = await r.text();
  const re = /threadid=(\d+)">\s*<\/a>[\s\S]*?<div class="title l limit"[^>]*>([\s\S]*?)<\/div>/g;
  let m; const items = []; const seen = {};
  while ((m = re.exec(html)) !== null) {
    let title = m[2].replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').trim();
    if (title.length > 4 && !seen[m[1]]) { seen[m[1]] = 1; items.push(title + ' [' + m[1] + ']'); }
  }
  return items.join('\n'); // 每页20条，page=N翻页
})();
```

### 2. 抓取单帖全文（含多页）

```js
(async () => {
  const id = 18389715, bid = 99; // 帖子号、版面号
  let full = '';
  for (let p = 1; p <= 132; p++) { // 上限按总页数改
    const r = await fetch(`https://bbs.pku.edu.cn/v2/post-read.php?bid=${bid}&threadid=${id}&page=${p}`, {credentials: 'include'});
    const html = await r.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    doc.querySelectorAll('script,style').forEach(n => n.remove());
    const t = doc.body ? (doc.body.innerText || doc.body.textContent || '') : '';
    if (t.length < 200) break;
    full += '\n===== 第' + p + '页 =====\n' + t;
    if (t.indexOf('下一页') < 0) break;
  }
  return full.length; // 存入 window.__posts[id] 供后续提取
})();
```

### 3. 提取「作者+楼号+正文」结构化楼层

```js
(function () {
  const t = window.__posts['帖子号']; // 或上一步的 full 文本
  const re = /\n\s*([A-Za-z0-9_\u4e00-\u9fa5]{2,20})\s*\n\s*\[(离线|在线)\][\s\S]*?\n\s*(\d{1,4})楼\s*\n\s*([\s\S]*?)\n\s*赞\s*\((\d+)\)/g;
  let m; const out = [];
  while ((m = re.exec(t)) !== null) {
    const body = m[4].replace(/\s+/g, ' ').trim();
    if (body.length > 50) out.push(`【${m[3]}楼·${m[1]}·赞${m[5]}】${body}`);
  }
  return out.join('\n\n');
})();
```

### 经验与限制

- `post-read.php` 直接带 `page=N` 参数有效；`board.php` 的帖子列表是JS动态加载的，静态fetch拿不到，必须用 `thread.php`
- 超长帖（如2638楼部委楼）全量约7秒/页，先全部抓完存 `window.__pg`，再按楼号/日期/点赞数分批提取，避免一次性输出
- 大输出会被 browser-action 落盘成文件（tool-results目录），直接 read_file 读取
- 长文本里楼与楼之间有大量空白行，提取正则容错性已调好，别改窄了
- shell转义坑：browser-action 的 JS 里避免 `!`（zsh历史扩展破坏JSON）、避免反引号；复杂脚本先写到文件再 `catdesk browser-action "$(cat /tmp/_cmd.json)"`（用python json.dumps中转）
- 树洞（独立App）不在BBS体系内，爬不了；BBS内无匿名版

## 五、无隐私顾虑说明

`backup.json` 会随仓库公开。内容仅含求职记录（公司/岗位/状态/笔记），如某天不想公开，可将仓库转为 Private（GitHub Pages 免费版对私有仓库有限制，需改用其他静态托管或保持公开但减少备份频率）。
