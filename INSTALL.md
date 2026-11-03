# 一句话安装

## 复制下面这段，发给你的 agent（Claude Code / Codex / Cursor / Gemini CLI / Hermes / OpenCode… 都可以）

```
帮我安装 https://github.com/HankGuo/dushe-2bti 这个 agent skill。

做法（不要问我，你自己做完，全程不要让我装任何东西）：

第 1 步：把安装器弄到手 —— 挑一个你这台机器能用的方式，都试不通再问我：
   A（推荐，有 git，最稳）:
     git clone --depth 1 https://github.com/HankGuo/dushe-2bti.git /tmp/dushe-2bti
   B（没有 git，用 Python 标准库）:
     python3 -c "import urllib.request;urllib.request.urlretrieve('https://raw.githubusercontent.com/HankGuo/dushe-2bti/main/install.py','/tmp/dushe-2bti-install.py')"
   C（有 gh CLI）:
     gh repo clone HankGuo/dushe-2bti /tmp/dushe-2bti

第 2 步：运行安装器，它会自己探测你的 agent 目录、自己装、自己跑渲染验证：
   - 用了 A 或 C：python3 /tmp/dushe-2bti/install.py
   - 用了 B：python3 /tmp/dushe-2bti-install.py

第 3 步：把验证结果和安装路径告诉我。

装好后这个 skill 的用法是：对 agent 说「毒舌我一下」或「给我出个人格报告」。
```

---

## 为什么是这段话

**用户侧零依赖**：只要有 Python 3.9+（macOS/Linux/Windows 都自带）就能装。
不需要 `npx`、不需要 `gh`、不需要 `pip install`、不需要装任何第三方包。
用户只需要复制粘贴一句话，剩下的 agent 全包。

**agent 侧全自动**：安装器自己探测 agent 目录、自己下载、自己解压、自己跑验证。

**给 agent 三个下载途径**是有原因的——`raw.githubusercontent.com` 在部分网络下不通，
`git clone` 更稳。三个方式都失败才需要问人。


## 装到哪了

| Agent | 目录 |
|---|---|
| Claude Code | `~/.claude/skills/dushe-2bti/` |
| Codex CLI | `~/.agents/skills/dushe-2bti/` |
| Cursor | `~/.cursor/skills/dushe-2bti/` |
| Gemini CLI | `~/.gemini/skills/dushe-2bti/` |
| GitHub Copilot | `~/.copilot/skills/dushe-2bti/` |
| OpenCode | `~/.config/opencode/skills/dushe-2bti/` |
| OpenClaw | `~/.openclaw/skills/dushe-2bti/` |
| Hermes Agent | `~/.hermes/skills/dushe-2bti/` |

**检测不到时**默认装到 `~/.agents/skills/`——Agent Skills 开放标准的通用目录，
除 Claude Code 外几乎所有 agent 都读它。

**Claude Code 要单独装一次**（它不读 `.agents/`）：

```
帮我把 https://github.com/HankGuo/dushe-2bti 也装到 ~/.claude/skills/：
python3 -c "import urllib.request;urllib.request.urlretrieve('https://raw.githubusercontent.com/HankGuo/dushe-2bti/main/install.py','/tmp/dushe_install.py')" && python3 /tmp/dushe_install.py --target ~/.claude/skills
```

---

## 进阶：批量部署 / CI 用命令行

如果你要给一堆机器装，或者在 CI 里跑，用这些：

```bash
# 通用（纯标准库，零依赖）
python3 install.py                    # 自动探测
python3 install.py --list             # 看看本机有哪些 agent
python3 install.py --target ~/.claude/skills
python3 install.py --uninstall

# 行业主流 CLI（可选，不是必需的）
npx skills add HankGuo/dushe-2bti
gh skill install HankGuo/dushe-2bti dushe-2bti --agent claude-code --scope user
```

---

## 卸载

```
帮我卸载 dushe-2bti：
python3 -c "import urllib.request;urllib.request.urlretrieve('https://raw.githubusercontent.com/HankGuo/dushe-2bti/main/install.py','/tmp/dushe_install.py')" && python3 /tmp/dushe_install.py --uninstall
```
