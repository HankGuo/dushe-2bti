---
name: dushe-2bti
description: Use when the user wants a personality roast, savage profile, 毒舌2BTI 人格报告, 人格雷达图/词云, or a shareable personality card. 16 型人格坐标系（4 轴 × 2 极）+ 六维雷达 + sprite-mask 词云 + 离线 HTML/PNG 渲染，目标名自动取环境变量，不硬编码任何人名。
---

# 毒舌2BTI — 毒舌人格生成器（16 型）

把一个人扔进自创的 **2BTI 坐标系（4 轴 × 2 极 = 16 型）**，
产出 **人格词云 → 六维雷达 → 象限定位 → 毒舌解剖 → 判决依据 → 转发文案**，
最终渲染成一张可截图传播的 HTML / PNG。

## 何时使用

- 用户要"毒舌我 / 骂我 / 锐评我 / 给我个人格报告"
- 用户要"人格雷达图 / 人格词云 / 人格卡片 / 可分享的人格海报"
- 用户提到 **2BTI** / **毒舌2BTI**

## 刚性约束（用户拍板过，不要自作主张改）

**1. 版面顺序固定：词云 → 雷达 → 象限 → 毒舌 → 证据 → 转发。**
词云必须排第一：它是唯一能"一眼截图直接发出去"的区块，传播性最强；
雷达图紧随其后承接视觉。**不要按"数据逻辑"把雷达图或人格结论提到最前面**。

**2. 先交付验收，不要主动开源。**
产物默认只落本地。不要 clone / push 到任何远端仓库，也不要主动建 GitHub 仓库。
**等用户明确说"开源 / commit and push"再发。**（发布流程见本 skill 末尾的开源前检查清单。）

**3. 人格划分由你自己设计，不要反问用户要哪几个维度。**
给出一套自洽、可计算、好传播的坐标系，用公式算象限，不要拍脑袋。

**4. 绝不硬编码任何人名。**
名字来源：`--name` > 环境变量 `DUSHE_NAME` > `USER`/`USERNAME`/`LOGNAME` > `HOSTNAME` > `路人甲`。
示例文件必须是虚构人物，不得含真实账号、路径、硬件信息。

**5. 16 型不能只是 16 张换色卡片 —— 每族必须有独立的视觉语言。**
用户原话：「不要全部做成一样的了，还是有点创意和味道，搞笑一点」。
只换配色 = 16 个模板变量，用户一眼看穿是同一张卡。**必须按「族」分配四层差异**：

| 层 | 作用 | 实现位置 |
|---|---|---|
| 背景纹理 | 纸面质感 | `body.fam-XX` 的 CSS 背景（斜纹/网格/聚光/稿纸） |
| 卡片质感 | 边框、圆角、阴影 | `--card-border` / `--card-radius` / `--card-shadow` |
| 雷达填充 | 数据区纹理 | `--radar-style` → stripe / gradient / soft / cross |
| 徽章形状 | 符号底板形状 | `.sym-badge` 的 per-family 覆盖（圆牌/方牌/双线方） |

再叠**每型专属**的：符号 emoji（`TYPE_GLYPHS`）、罪状条（`charge`）、印章（`stamp`）。
四族命名即视觉隐喻：BR=施工现场、BT=工程蓝图、PR=舞台聚光、PT=公文档案。
改动任一层后，用四族各出一张图做**像素级对比**（背景纹理饱和度、徽章主色、边框粗细），
确认差异客观存在——不能凭代码推断"应该不一样了"。

## 工作流（三步，禁止跳步）

### 第 1 步：采集证据（最重要）

**没有证据的毒舌是耍嘴皮子，有证据的毒舌才好笑。**

必须从真实来源取事实：

1. **对话历史** — 用户原话、做过的决定、推翻过的方案
2. **Hindsight 记忆库** — `hindsight_recall(query="<行为模式/偏好/纠错记录>")`
3. **人设文件** — `~/.hermes/memories/USER.md`、`~/.hermes/SOUL.md`
4. **会话搜索** — `session_search(query="...")`
5. **客观痕迹**（仅当评估对象是这台机器主人时才用，且需用户要求"看事实"）：
   ```bash
   ps -eo pid,rss,pcpu,comm --sort=-rss | head -20
   docker ps --format '{{.Names}} | {{.Status}}'
   ```

**铁律**：每条"事实型"毒舌都要能追溯到具体证据，写进 `evidence`。
没有依据的观察只能进 `subtitle` / `manifesto` 这类风格化字段。

### 第 2 步：打分与写毒舌

读 `references/2bti-taxonomy.md` 拿 **16 型全表**、六维释义、词云词池、JSON 结构。

要点：
- **六维分数要有区分度**，全 80+ 等于没测；形状要有故事（尖角 = 偏科）
- **象限用公式算，别拍脑袋**（`type_code` 留空时渲染器会自动判）：
  ```
  B/P = (落地力 + 架构脑) / 2    ≥60 → B
  R/T = (探索欲 + 构想力) / 2    ≥60 → R
  S/D = (社交电量 + 抗压值) / 2  ≥55 → S
  L/F = (抗压值 + 落地力) / 2    ≥60 → L
  ```
- **毒舌黄金五刀**：
  1. 第一刀要**好笑**，让人愿意往下看
  2. 第二刀要**准**，拿事实打脸
  3. 第三刀要**狠但不好笑**——扎到他嘴硬的地方
  4. 第四刀往死里扎
  5. 第五刀留个**能截图的结论**
- **禁忌**：骂**行为模式**，不骂人格/外貌/智商/家庭
- **词云词条要具体**：`工具收藏家` `嘴上说算了` `明天开始`（✓）；`优秀` `勤奋`（✗）

### 第 3 步：渲染

```bash
# 只出 HTML（目标名自动取环境变量）
python3 ~/.hermes/skills/dushe-2bti/scripts/render.py profile.json -o out.html

# 出 HTML + 桌面 PNG + 手机竖版 PNG（推荐，手机版适合发社交平台）
python3 ~/.hermes/skills/dushe-2bti/scripts/render.py profile.json \
  -o out.html --png out.png --mobile

# 显式指定目标名
python3 ~/.hermes/skills/dushe-2bti/scripts/render.py profile.json -o out.html --name "张三"
```

渲染器**零外部依赖**（无 CDN），离线可用，HTML 可直接开源分发。
`--png` 会自动用 Chrome `--dump-dom` 探测真实页面高度再截图，`--mobile` 额外出 750px 竖版。

## 目标名解析

优先级：`--name` > `DUSHE_NAME` > `USER` / `USERNAME` / `LOGNAME` > `HOSTNAME` > `路人甲`

> ⚠️ 用 `DUSHE_NAME` 而不是 `2BTI_NAME`——**shell 变量名不能以数字开头**，
> `2BTI_NAME=x cmd` 会报"未找到命令"。代码里仍兼容读 `2BTI_NAME`（程序设环境变量的场景）。

```bash
DUSHE_NAME="小王" python3 render.py p.json -o out.html
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `references/2bti-taxonomy.md` | **16 型全表**、四轴定义、六维释义、毒舌评级、词云词池、JSON 结构、判型公式 |
| `scripts/render.py` | JSON → 自包含 HTML（+可选 PNG）。零外部依赖 |
| `assets/profile.example.json` | **虚构示例**（拖延症画像），可直接跑通验证渲染 |

**已开源**：https://github.com/HankGuo/dushe-2bti （MIT）
安装：把整个目录放进 agent 的 skills 目录（`~/.hermes/skills/`、`.claude/skills/` 等）。

## JSON 数据结构（关键字段）

```json
{
  "subject": "留空则自动取环境变量",
  "title": "留空则自动生成「毒舌2BTI · {名字}」",
  "subtitle": "一句话毒舌总结（会被截图的第一行）",
  "type_code": "留空则按六维自动判定 16 型",
  "type_name": "留空则按 type_code 自动补",
  "type_en": "同上",
  "type_desc": "一句话人设",
  "manifesto": "人格宣言：两三句，押韵带梗，能当签名",
  "rating": "★★★★☆",
  "rating_label": "狠角色",
  "dimensions": {"ideate":94,"exec":28,"arch":71,"curio":89,"tough":33,"social":62},
  "axis_explain": [
    {"axis":"能不能造出东西","left":"Paper 纸上","right":"Build 能造","score":50,"verdict":"PAPER"},
    {"axis":"干事的姿态","left":"Tame 稳","right":"Rogue 野","score":92,"verdict":"ROGUE"},
    {"axis":"驱动力来源","left":"Drive 内在","right":"Spark 外部","score":48,"verdict":"DRIVE"},
    {"axis":"对待不确定性","left":"Flow 随缘","right":"Lock 要结论","score":31,"verdict":"FLOW"}
  ],
  "roast": ["第一刀…","第二刀…","第三刀…","第四刀…","第五刀…"],
  "evidence": [{"claim":"结论句","proof":"具体事实"}],
  "wordcloud": [{"text":"工具收藏家","weight":100}],
  "share": {"one_liner":"最狠的一句","hashtags":["#毒舌2BTI"]},
  "meta": {"generated_at":"2026-11-02","generator":"毒舌2BTI v3"}
}
```

## 16 型速查

大族由前两位决定，细分由后两位决定：

| 代号 | 名称 | 符号 | 一句话人设 |
|---|---|---|---|
| `BR-SL` | 莽夫 | ⚡ | 一句话开干，边骂边造，撞墙再绕 |
| `BR-SF` | 疯批 | 🔥 | 想到就烧，烧完自己都记不清 |
| `BR-DL` | 狠人 | ⚙️ | 不需要灵感，流程跑起来就停不下来 |
| `BR-DF` | 游击队长 | 🎯 | 专挑硬骨头打，打完就跑不占道 |
| `BT-SL` | 军令型 | 🎖️ | 拍完就干，干完要复盘 |
| `BT-SF` | 缝合怪 | 🧩 | 什么都收一点，什么都不算精通 |
| `BT-DL` | 铁匠 | 🔨 | 交付之王，造得出还稳 |
| `BT-DF` | 掌柜 | 🏪 | 系统跑着就行，别来烦我 |
| `PR-SL` | 戏精 | 🎭 | 空中楼阁大师，情绪比方案先到 |
| `PR-SF` | 键鼠侠 | ⌨️ | 键盘上纵横四海，落地寸步难行 |
| `PR-DL` | 空想家 | 💭 | 脑内已经上市，实际还在草稿 |
| `PR-DF` | 甩锅王 | 🏳️ | 想法甩出去，执行不归我 |
| `PT-SL` | 军师 | ♟ | 想得透就是不动手 |
| `PT-SF` | 观察员 | 👁 | 看得很准，看完就散 |
| `PT-DL` | 苦行僧 | 🕯 | 计划完美，执行缺席 |
| `PT-DF` | 记录官 | 🗂 | 整理得头头是道，就是不开始 |

每型有专属配色、符号、罪状条、印章，见 `render.py` 的 `THEMES` / `TYPE_GLYPHS`。

## 四族视觉语言（不可省）

**16 型不是同一张卡换 16 种颜色。** 族由 `type_code` 前两位决定，每族有独立的一整套视觉：

| 族 | 主题 | 背景纹理 | 卡片质感 | 雷达填充 | 徽章形状 |
|---|---|---|---|---|---|
| **BR** | 施工现场 | 斜向警示条纹 | 3px 粗边 + 8px 硬阴影 | 斜纹 | 圆角方牌 |
| **BT** | 工程蓝图 | 细网格 + 十字准线 | 1px 细边 + 内发光 | 渐变 | 小圆角方牌 |
| **PR** | 舞台聚光 | 顶部聚光锥 | 2px 双线 + 大圆角 | 柔和径向 | 粗描边圆牌 |
| **PT** | 公文档案 | 横线稿纸 + 装订线 | 直角 + 轻投影 | 交叉斜线 | 双线方牌 |

四层差异必须同时存在，否则用户一眼看穿是同一张卡的 16 个变量。
改族视觉语言改 `render.py` 的 `FAMILIES`。

**符号必须放在渐变底板上**——深色 emoji（♟👁🕯🗂）在深色底上等于没渲染（实测彩色像素仅 5 个）。
加底板后亮度占比提升到 12%~76%。深色符号不要带变体选择符（`♟️` → `♟`）。

## 技术实现备忘（改代码前必读）

- **词云**：`sprite-mask` 位图碰撞（每个词渲染到离屏 canvas 取 alpha 做 mask，逐像素与全局占用位图比对），**不是矩形包围盒**——中文词形差异大，包围盒会误判重叠导致大量词放不下
- **螺旋布局**：中心取 `CH*0.47`（略上移）给底部留边；步长 0.14、半径系数 1.9、最多 40000 步
- **自动测高**：页面 `reportHeight()` 把 `scrollHeight` 写进 `<html data-pageh>`，Python 端用 `--dump-dom` 读出来——**不要硬编码截图高度**，窄屏下页面会高出一大截（实测差 1500px）
- **字体**：走系统栈 `Noto Sans CJK SC / 思源黑体 / 苹方 / 雅黑`，不内嵌字体
- **对比度**：正文 ≥5.0，次要文字 ≥4.2（WCAG 参考 4.5）

### 深色 emoji 在深色背景上会消失 —— 必须加底板

♟ / 👁 / 🕯 / 🗂 这类符号在深色底上是**深色**，等于没渲染：实测徽章区彩色像素只有 5 个。
**修法（已验证）**：
1. 给符号加**渐变圆形底板**：径向高光 + 主色渐变 + 白色描边 + 内阴影 + 虚线外环
2. `font-family` 显式写 `"Noto Color Emoji","Apple Color Emoji","Segoe UI Emoji",sans-serif`
3. 去掉变体选择符（`♟️` → `♟`），只保留基础码点
4. 底板**形状随族变**（BR 方牌 / BT 小方 / PR 圆 / PT 双线方），避免 16 型在徽章处又雷同

验收看**亮像素占比**而不是"看有没有画出来"：徽章区亮像素 >25% 才算合格。

### 像素审计的坐标必须来自同一次渲染

在 CDP 浏览器里量到的 `getBoundingClientRect()` 坐标，**不能**直接套到另一视口宽度的
截图上——同一份 HTML 在 1430px 视口量到 x=215，在 1240px 视口实际是 x=128，差 87px，
套错位置会量出"全是背景色"的假阴性。
**正确做法**：让页面自己把元素坐标写进 `<html data-badge="x,y,w,h">`，
用 `--dump-dom` 读出来，再乘以截图的 devicePixelRatio。与 `data-pageh` 同一套路。
（`reportBadge()` 已实现，见 `render.py`。）

**交付前验收**：出图后不要只看退出码。底部裁切是这套流程的典型静默失败——
用 `document-output` 技能的 `scripts/audit_png_pixels.py` 跑一遍
（零依赖像素审计：底边留白 / 分区墨量 / 空区块）。
vision 不可用时，改用 DOM 几何检查（横向溢出、文字截断、卡片等高）+
计算样式对比度，并如实说明"视觉细看仍由用户拍板"。

## 开源前检查清单

**先读 `github` skill 的 `references/repo-management.md` §11**，那节是完整的
发布流程（可见性决策 → 身份扫描 → 提交 → 建仓推送 → 从公开 URL 重新 clone 验证）。

```bash
cd 技能目录

# 1) 身份/凭据扫描（文本 + 二进制一起扫）
python3 ~/.hermes/skills/software-development/github/scripts/scan_publish_tree.py . \
  --name "<真实姓名>" --handle "<github handle>" \
  --path "/home/<用户名>" --host "<主机名>" --ip "<内网IP>"
# → 退出码 0 = 干净；1 = 有泄漏，先修再发

# 2) 清 pycache（会带绝对路径，且 .gitignore 只挡未来提交）
rm -rf scripts/__pycache__

# 3) 16 型覆盖 + 可达性验证（THEMES / TYPE_NAMES / TYPE_GLYPHS 三张表都要齐）
python3 -c "
import sys, itertools, random; sys.path.insert(0,'scripts')
from render import THEMES, TYPE_NAMES, TYPE_GLYPHS, classify
codes=[f'{a}{b}-{c}{d}' for a,b,c,d in itertools.product('BP','RT','SD','LF')]
assert all(c in THEMES and c in TYPE_NAMES and c in TYPE_GLYPHS for c in codes), '有类型缺表项'
hit=set()
random.seed(42)
for _ in range(200000):
    hit.add(classify({k: random.randint(0,100) for k in ['ideate','exec','arch','curio','tough','social']}))
print('16 型覆盖 OK，随机可达', len(hit), '/16')
"
```

**推完必须从公开 URL 重新 clone 一次跑**——本地能跑 ≠ clone 下来能跑。
`.gitignore` 排掉的运行期文件、只存在于本机的示例数据、没提交的依赖，
只有这样才测得出来。

- 产物是**单个自包含 HTML**，无外部请求、无追踪、离线可看
- 词云是自研算法，非商用词云库，无版权问题
- 坐标系为本项目原创，可自由署名使用
- 示例数据**必须是虚构人物**
