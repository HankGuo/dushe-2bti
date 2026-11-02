# 毒舌2BTI · Savage 2BTI

> 一个自创的 16 型人格坐标系 + 一张能直接发朋友圈的毒舌人格报告。
> 词云 + 六维雷达 + 象限定位 + 五刀毒舌 + 判决依据，一键出图。

**16 型** · 4 轴 × 2 极 · 零外部依赖 · 离线可用 · 单文件 HTML

---

## 这是什么

MBTI 给你 4 个字母，2BTI 给你 **4 个字母 + 一张能截图的图**，还顺手骂你一顿。

```
B/P  能不能造出东西      Build（真造） / Paper（纸上）
R/T  干事的姿态          Rogue（野）   / Tame（稳）
S/D  驱动力来源          Spark（外部） / Drive（内在）
L/F  对待不确定性        Lock（要结论）/ Flow（随缘）
```

四轴组合 → **16 型**，每型有名字、有人设、有毒舌金句、有专属配色。

| 代号 | 名称 | 一句话人设 |
|---|---|---|
| `BR-SL` | 莽夫 | 一句话开干，边骂边造，撞墙再绕 |
| `BR-SF` | 疯批 | 想到就烧，烧完自己都记不清 |
| `BR-DL` | 狠人 | 不需要灵感，流程跑起来就停不下来 |
| `BR-DF` | 游击队长 | 专挑硬骨头打，打完就跑不占道 |
| `BT-SL` | 军令型 | 拍完就干，干完要复盘 |
| `BT-SF` | 缝合怪 | 什么都收一点，什么都不算精通 |
| `BT-DL` | 铁匠 | 交付之王，造得出还稳 |
| `BT-DF` | 掌柜 | 系统跑着就行，别来烦我 |
| `PR-SL` | 戏精 | 空中楼阁大师，情绪比方案先到 |
| `PR-SF` | 键鼠侠 | 键盘上纵横四海，落地寸步难行 |
| `PR-DL` | 空想家 | 脑内已经上市，实际还在草稿 |
| `PR-DF` | 甩锅王 | 想法甩出去，执行不归我 |
| `PT-SL` | 军师 | 想得透就是不动手 |
| `PT-SF` | 观察员 | 看得很准，看完就散 |
| `PT-DL` | 苦行僧 | 计划完美，执行缺席 |
| `PT-DF` | 记录官 | 整理得头头是道，就是不开始 |

完整定义见 [`references/2bti-taxonomy.md`](references/2bti-taxonomy.md)。

---

## 快速开始

```bash
# 1. 跑示例（虚构人物，可直接出图）
python3 scripts/render.py assets/profile.example.json -o out.html --png out.png --mobile

# 2. 换成你自己
python3 scripts/render.py my-profile.json -o me.html --png me.png --mobile --name "你的名字"
```

**环境要求**：Python 3.9+、Chrome（仅出 PNG 时需要）。

不传 `--name` 时，目标名自动按这个顺序取：
`DUSHE_NAME` → `USER` → `USERNAME` → `LOGNAME` → `HOSTNAME` → `路人甲`

```bash
DUSHE_NAME="小王" python3 scripts/render.py p.json -o out.html
```

> ⚠️ 为什么叫 `DUSHE_NAME` 不叫 `2BTI_NAME`：**shell 变量名不能以数字开头**，
> `2BTI_NAME=x cmd` 会报"未找到命令"。

---

## 输出长什么样

```
┌─────────────────────────────────────────┐
│         毒 舌 2 B T I                    │
│         毒舌2BTI · 你的名字               │
│   一句会被人截图的第一行总结…              │
├──────────────┬──────────────────────────┤
│  PR-SF       │  键盘上纵横四海，           │
│  键鼠侠      │  落地寸步难行              │
│  THE KEYBOARD│  「人格宣言…」  ★★☆☆☆    │
├──────────────┴──────────────────────────┤
│  01 人格词云        02 六维人格雷达       │
│  ┌───────────┐      ┌───────────┐       │
│  │ 词 词 词   │      │    ◇      │       │
│  │   词 词    │      │  ◇   ◇    │       │
│  └───────────┘      └───────────┘       │
├─────────────────────────────────────────┤
│  03 象限定位（四条轴，条状图）             │
│  04 毒舌解剖（五刀）                       │
│  05 判决依据（每条毒舌对应真实证据）        │
│  06 一句话转发 + 话题标签                  │
└─────────────────────────────────────────┘
```

---

## 四族视觉语言

16 型不是同一张卡换 16 种颜色——**四个大族各有独立的视觉语言**，从背景纹理到卡片质感到雷达图填充全都不一样。

| 族 | 主题 | 背景纹理 | 卡片质感 | 雷达填充 | 徽章形状 |
|---|---|---|---|---|---|
| **BR** 能造×野 | **施工现场** | 斜向警示条纹 | 3px 粗边框 + 8px 硬阴影 | 斜纹 | 圆角方牌 |
| **BT** 能造×稳 | **工程蓝图** | 细网格 + 十字准线 | 1px 细线 + 内发光 | 渐变 | 小圆角方牌 |
| **PR** 纸上×野 | **舞台聚光** | 顶部聚光锥 | 2px 双线 + 大圆角 | 柔和径向 | 粗描边圆牌 |
| **PT** 纸上×稳 | **公文档案** | 横线稿纸 + 装订线 | 直角 + 轻投影 | 交叉斜线 | 双线方牌 |

族由 `type_code` 的**前两位**决定，后两位决定同族内的细分性格。

## 每型专属元素

除了配色，每型还有自己的**符号徽章 / 罪状条 / 印章**：

| 代号 | 名称 | 符号 | 罪状条 | 印章 |
|---|---|---|---|---|
| `BR-SL` | 莽夫 | ⚡ | 现场直击 | 说干就干 |
| `BR-SF` | 疯批 | 🔥 | 失控现场 | 想到就烧 |
| `BR-DL` | 狠人 | ⚙️ | 流水线作业 | 停不下来 |
| `BR-DF` | 游击队长 | 🎯 | 专挑硬骨头 | 打完就跑 |
| `BT-SL` | 军令型 | 🎖️ | 下达命令 | 说到做到 |
| `BT-SF` | 缝合怪 | 🧩 | 东拼西凑 | 什么都收 |
| `BT-DL` | 铁匠 | 🔨 | 交付现场 | 造得出还稳 |
| `BT-DF` | 掌柜 | 🏪 | 生意兴隆 | 系统跑着 |
| `PR-SL` | 戏精 | 🎭 | 排练现场 | 情绪先行 |
| `PR-SF` | 键鼠侠 | ⌨️ | 键盘江湖 | 纵横四海 |
| `PR-DL` | 空想家 | 💭 | 脑内上市 | 想得真美 |
| `PR-DF` | 甩锅王 | 🏳️ | 责任转移 | 执行不归我 |
| `PT-SL` | 军师 | ♟ | 沙盘推演 | 想得比谁透 |
| `PT-SF` | 观察员 | 👁 | 现场观察 | 看得很准 |
| `PT-DL` | 苦行僧 | 🕯 | 修行记录 | 计划完美 |
| `PT-DF` | 记录官 | 🗂 | 卷宗归档 | 整理得头头是道 |

> 符号一律放在**渐变底板**上渲染。原因：♟👁🕯🗂 这类深色 emoji 在深色背景上几乎不可见（实测彩色像素只有 5 个），
> 加底板 + 高光 + 内阴影后亮度占比提升到 12%~76%。

---

## 作为 Agent Skill 使用

这个仓库同时是一个 [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/skills)：
把整个目录放到 agent 的 skills 目录即可（如 `~/.hermes/skills/`、`.claude/skills/`）。

`SKILL.md` 里封装了完整的毒舌提示词工作流：
**采集证据 → 打分定象限 → 写五刀 → 渲染**，并带硬约束（不硬编码人名、先验收后开源、词云必须排第一）。

兼容 Hermes Agent / Claude Code / Codex / Cursor 等吃 `SKILL.md` 约定的框架。

---

## 设计要点

- **零外部依赖**：无 CDN、无 Chart.js、无词云库、不内嵌字体。单 HTML 约 23KB
- **四族视觉语言**：背景纹理 / 卡片质感 / 雷达填充 / 徽章形状全部按族切换，不是换色模板
- **词云用 sprite-mask 位图碰撞**：把每个词渲染到离屏 canvas 取 alpha 当掩码，逐像素比对。
  矩形包围盒对中文词形误判严重，会导致大量词放不下
- **自动测高再截图**：页面把 `scrollHeight` 写进 `<html data-pageh>`，截图前先 `--dump-dom` 读出来。
  硬编码高度在窄屏下必然裁切（实测差 1500px）
- **判型可计算**：不给 `type_code` 时按六维公式自动算，不靠人拍脑袋
- **不硬编码任何人名**：目标名走 `--name` > `DUSHE_NAME` > `USER`/`USERNAME`/`LOGNAME` > `HOSTNAME` > `路人甲`
- **隐私安全**：渲染器不联网、不读任何外部文件，只吃你给的 JSON。示例数据是虚构人物

---

## 目录结构

```
.
├── SKILL.md                        # Agent 技能定义（工作流 + 硬约束 + 提示词）
├── LICENSE                         # MIT
├── README.md
├── references/
│   └── 2bti-taxonomy.md            # 16 型全表 + 四轴定义 + 判型公式 + 视觉语言 + JSON 结构
├── scripts/
│   └── render.py                   # JSON → HTML / PNG 渲染器（零依赖）
└── assets/
    └── profile.example.json        # 虚构示例（拖延症画像）
```

---

## 自定义 / 扩展

| 想改什么 | 改哪里 |
|---|---|
| 加人格型 | `render.py` 的 `THEMES` + `TYPE_NAMES` + `TYPE_GLYPHS`，同步更新 taxonomy |
| 换配色 | `render.py` 的 `THEMES`（每型 `a`/`b` 两个主色） |
| 换符号/罪状条/印章 | `render.py` 的 `TYPE_GLYPHS` |
| 改整族视觉语言 | `render.py` 的 `FAMILIES`（背景 pattern / 雷达 radar / 边框 / 圆角 / 阴影） |
| 改判型阈值 | `render.py` 的 `classify()`（默认 B≥60 / R≥60 / S≥55 / L≥60） |
| 改六维名称 | `render.py` 的 `DIM_META` |
| 改版面顺序 | `render.py` 里 HTML 模板的区块顺序 |

### 加一个新类型的完整步骤

1. `THEMES` 里加 `"XX-XX": {"a": "#...", "b": "#..."}`
2. `TYPE_NAMES` 里加 `"XX-XX": ("中文名", "ENGLISH NAME")`
3. `TYPE_GLYPHS` 里加 `"XX-XX": {"sym": "🎯", "charge": "罪状条", "stamp": "印章"}`
4. 如果是新族，还要在 `FAMILIES` 里加一族视觉语言，并写对应的 `body.fam-XX` CSS
5. 在 `references/2bti-taxonomy.md` 补上表格行
6. 跑一遍验证：

```bash
python3 -c "
import sys, itertools; sys.path.insert(0,'scripts')
from render import THEMES, TYPE_NAMES, TYPE_GLYPHS, classify
codes=[f'{a}{b}-{c}{d}' for a,b,c,d in itertools.product('BP','RT','SD','LF')]
assert all(c in THEMES and c in TYPE_NAMES and c in TYPE_GLYPHS for c in codes)
print('OK')
"
```

---

## License

MIT — 随便用、随便改、随便商用。署名不强制，但骂得准的话记得说是 2BTI 干的。
