# 安装与使用指南

## 一句话安装

**复制这句给你的 Agent（WorkBuddy / Trae / Cursor / Claude Code / Codex / Antigravity / Gemini CLI 等均支持）：**

```
帮我安装 https://github.com/HankGuo/dushe-2bti 这个 skill
```

> 🇨🇳 **国内网络环境推荐给 Agent 发：**
> ```
> 帮我安装 https://gitee.com/hank_guo/dushe-2bti 这个 skill
> ```

Agent 会自动识别、拉取技能目录、并完成一次离线渲染自检。你什么都不需要手动安装，无需额外依赖。

---

## 快速安装方式

### 方式 1：Agent Skills 规范安装（推荐）

```bash
npx skills add HankGuo/dushe-2bti
```

### 方式 2：国内极速克隆（Gitee 镜像）

国内直连 GitHub 偶尔较慢时，使用 Gitee 极速镜像：

```bash
# 以通用的 .agents 目录为例：
git clone https://gitee.com/hank_guo/dushe-2bti.git ~/.agents/skills/dushe-2bti

# 或安装至 WorkBuddy：
git clone https://gitee.com/hank_guo/dushe-2bti.git ~/.workbuddy/skills/dushe-2bti

# 或安装至 Trae：
git clone https://gitee.com/hank_guo/dushe-2bti.git ~/.trae/skills/dushe-2bti
```

### 方式 3：纯 Python 自动安装器（零依赖）

仓库内置跨平台纯 Python 安装脚本，自动探测所有已知 Agent 目录、自动软链或复制、并自动运行渲染自检：

```bash
python3 install.py
```
> 参数支持：`--list`（查看检测到的 Agent）/ `--target <dir>`（指定安装目录）/ `--uninstall`（一键卸载）。

### 方式 4：GitHub CLI（gh ≥ 2.90.0）

```bash
gh skill install HankGuo/dushe-2bti dushe-2bti --agent claude-code --scope user
```

---

## 各 Agent 支持与安装目录

| Agent | 安装目录 | 唤出 / 触发方式 |
|---|---|---|
| **WorkBuddy** | `~/.workbuddy/skills/` | 自然语言自动触发 / 菜单选择 |
| **Trae** | `~/.trae/skills/` | 自然语言自动触发 |
| **Cursor** | `~/.cursor/skills/` 或 `~/.agents/skills/` | 输入 `/` 唤出或自然语言 |
| **Claude Code** | `~/.claude/skills/` | 输入 `/dushe-2bti` |
| **Codex CLI** | `~/.agents/skills/` | 输入 `$dushe-2bti` 或自然语言 |
| **Antigravity / Gemini CLI** | `~/.gemini/skills/` 或 `~/.agents/skills/` | 模型自动 `activate_skill` |
| **GitHub Copilot** | `~/.copilot/skills/` 或 `~/.agents/skills/` | 自动识别 + `/` |
| **Hermes Agent** | `~/.hermes/skills/` | 自动匹配激活 |
| **OpenCode / OpenClaw** | `~/.config/opencode/skills/` | 自动加载 |
| **裸 LLM / API 调用** | — | 直接将 `SKILL.md` 注入至 System Prompt |

> 💡 **提示**：Claude Code 默认不读取 `~/.agents/`，推荐单独安装一次：
> `python3 install.py --target ~/.claude/skills`

---

## 怎么使用

安装完成后，**无需记忆任何复杂命令**，直接对你的 Agent 讲人话：

```
毒舌我一下
帮我出个 2BTI 深度人格报告
根据我和你的对话，做一张毒舌人格长图
```

Agent 会自动加载该 Skill，严格执行四步标准流水线：
1. **搜集证据**：抓取对话风格、提问方式、代码习惯、拖延线索；
2. **六维打分**：计算维度得分并根据公式推导 16 型；
3. **毒舌裁决**：撰写 5 刀致命解剖与判决依据；
4. **生成图像**：调用渲染器离线输出单文件 HTML 与高清 PNG（手机/长图双规格）。

---

## 开发者与离线命令行调用

`render.py` 没有任何第三方 Python 库依赖（仅使用标准库）：

```bash
# 运行示例数据并生成 HTML + PNG（长图 + 750px 手机版）
python3 skills/dushe-2bti/scripts/render.py \
  skills/dushe-2bti/assets/profile.example.json \
  -o out.html --png out.png --mobile

# 指定报告人姓名（优先级最高）：
python3 skills/dushe-2bti/scripts/render.py \
  profile.json -o out.html --png out.png --name "张三"
```

名字解析优先级：
`--name` > 环境变量 `DUSHE_NAME` > 系统环境变量 `USER`/`USERNAME`/`LOGNAME` > `路人甲`

---

## 检查与更新

```bash
# 检查更新
cd ~/.agents/skills/dushe-2bti && git pull

# 卸载
python3 install.py --uninstall
```
