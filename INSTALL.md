# 安装与使用

## 一句话安装

**复制这句给你的 agent（Claude Code / Codex / Cursor / Gemini CLI / Hermes / OpenCode… 都行）：**

```
帮我安装 https://github.com/HankGuo/dushe-2bti 这个 skill
```

agent 会自己读仓库 README、挑一个能用的安装方式、装完跑一次验证。

**你什么都不用装。** 不需要 Node.js，不需要 gh CLI，不需要 pip。

---

## 自己装

```bash
# 首选（Vercel Labs skills CLI，生态事实标准）
npx skills add HankGuo/dushe-2bti

# 纯 Python 安装器（零依赖，适合没 Node.js 的机器）
python3 install.py

# GitHub CLI 官方（需要 gh ≥ 2.90.0）
gh skill install HankGuo/dushe-2bti dushe-2bti --agent claude-code --scope user

# 手动
git clone https://github.com/HankGuo/dushe-2bti.git ~/.agents/skills/dushe-2bti
```

`install.py` 会自动探测本机 agent 目录、自动下载、自己跑渲染验证。
参数：`--list`（看本机有哪些 agent）/ `--target <dir>`（装到指定目录）/ `--uninstall`（卸载）。

---

## 装到哪了

| Agent | 目录 | 调用方式 |
|---|---|---|
| **Hermes Agent** | `~/.hermes/skills/` | 自动触发 |
| **Claude Code** | `~/.claude/skills/` | `/dushe-2bti` |
| **Codex CLI** | `~/.agents/skills/` | `$dushe-2bti` 或 `/skills` |
| **Cursor** | `~/.cursor/skills/` 或 `~/.agents/skills/` | `/` 唤出 |
| **Gemini CLI** | `~/.gemini/skills/` 或 `~/.agents/skills/` | 模型自动 `activate_skill` |
| **GitHub Copilot** | `~/.copilot/skills/` 或 `~/.agents/skills/` | 自动 + `/` |
| **OpenCode** | `~/.config/opencode/skills/` | 自动 + skill 工具 |
| **OpenClaw** | `~/.openclaw/skills/` | 自动 |
| **Goose / Amp / Windsurf / Roo / Cline / Zed / Warp / Kilo / Crush…** | 各自目录，多数也读 `.agents/skills/` | 自动 |
| **裸 LLM API** | — | 把 `SKILL.md` 内容贴进 system prompt |

**装多个 agent 最省事**：装到 `.agents/skills/`，再给 Claude Code 软链一个。

```bash
git clone https://github.com/HankGuo/dushe-2bti.git ~/.agents/skills/dushe-2bti
ln -s ~/.agents/skills/dushe-2bti ~/.claude/skills/dushe-2bti
```

**Claude Code 要单独装一次**（它不读 `.agents/`）：

```bash
python3 install.py --target ~/.claude/skills
```

---

## 怎么用

装完之后**不用记命令**，跟 agent 说人话：

```
毒舌我一下
给我出个人格报告
锐评一下我的人格
```

agent 会自动加载这个 skill，走完整流程：
**采集证据 → 打分定 16 型 → 写五刀毒舌 → 渲染出图**。

### 三种触发方式

| 方式 | 例子 | 说明 |
|---|---|---|
| **自然语言**（推荐） | 「毒舌我一下」 | agent 读 description 自动匹配 |
| **斜杠命令** | `/dushe-2bti` | Claude Code / Cursor 显式调用 |
| **命令行直跑** | `python3 skills/dushe-2bti/scripts/render.py p.json -o out.html` | 不经过 agent，自己填 JSON |

### 自己填数据跑

`scripts/render.py` 零依赖，拿到 JSON 就能出图：

```bash
cd skills/dushe-2bti
python3 scripts/render.py assets/profile.example.json -o out.html --png out.png --mobile
```

**目标名不写死**，优先级：`--name` > 环境变量 `DUSHE_NAME` > `USER`/`USERNAME`/`LOGNAME` > `HOSTNAME` > `路人甲`

```bash
DUSHE_NAME="小王" python3 scripts/render.py my.json -o out.html
```

**给 agent 用的时候你不用填 JSON**——它会自己按六维打分、按四轴公式判型。

### JSON 字段速查

| 字段 | 留空会怎样 |
|---|---|
| `subject` / `title` | 自动取环境变量 / 自动生成「毒舌2BTI · {名字}」 |
| `type_code` | 按六维公式自动判定 16 型 |
| `type_name` / `type_en` | 按 `type_code` 自动补 |
| `dimensions` | **必填**，六维 0-100 |
| `roast` | 五刀毒舌正文 |
| `evidence` | 每条毒舌的依据（要真实） |
| `wordcloud` | 词云词条 + 权重 |
| `share` | 一句话转发文案 + 话题标签 |

完整结构见 [`skills/dushe-2bti/references/2bti-taxonomy.md`](skills/dushe-2bti/references/2bti-taxonomy.md) 第九节。

---

## 更新

```bash
cd ~/.agents/skills/dushe-2bti && git pull
# 或者
gh skill update dushe-2bti
```

## 卸载

```bash
python3 install.py --uninstall
```
