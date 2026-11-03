#!/usr/bin/env python3
"""毒舌2BTI · 零依赖安装器（纯 Python 标准库，不需要 git / node / gh）

用法（agent 执行这一行就完事）:
    python3 install.py                     # 自动探测 agent 目录并安装
    python3 install.py --target DIR        # 装到指定目录
    python3 install.py --list              # 列出支持的 agent 与本机检测结果
    python3 install.py --uninstall         # 卸载

行为:
    1. 探测本机已装的 agent（Claude Code / Codex / Cursor / Gemini CLI / Hermes / ...）
    2. 从 GitHub 下载仓库 zip，把 skills/dushe-2bti/ 解压到对应目录
    3. 装完自动跑一次渲染验证
    4. 打印后续用法

不依赖: git / node / npm / gh / pip / 任何第三方包
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

REPO = "HankGuo/dushe-2bti"
SKILL = "dushe-2bti"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main"
ZIP_URL = f"https://github.com/{REPO}/archive/refs/heads/main.zip"

# slug : 个人级 skills 目录
AGENTS = {
    "workbuddy":     "~/.workbuddy/skills",
    "trae":          "~/.trae/skills",
    "claude-code":   "~/.claude/skills",
    "codex":         "~/.agents/skills",
    "cursor":        "~/.cursor/skills",
    "gemini-cli":    "~/.gemini/skills",
    "github-copilot": "~/.copilot/skills",
    "opencode":      "~/.config/opencode/skills",
    "openclaw":      "~/.openclaw/skills",
    "hermes":        "~/.hermes/skills",
    "antigravity":   "~/.gemini/skills",
}

# 这些 agent 共用通用目录，装一次全中
SHARED = ("codex", "github-copilot", "cursor", "gemini-cli", "opencode", "openclaw")


def die(msg, code=1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "dushe-2bti-installer"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download_skill_zip():
    """从 GitHub 下载仓库 zip，返回 bytes。"""
    for url in (ZIP_URL,
                f"https://codeload.github.com/{REPO}/zip/refs/heads/main",
                f"https://github.com/{REPO}/archive/main.zip"):
        try:
            return fetch(url)
        except Exception as e:
            last = e
    die(f"下载仓库失败（网络问题？）: {last}")


def local_skill_dir():
    """如果本脚本就在仓库里，直接用本地副本（免下载）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    cand = os.path.join(here, "skills", SKILL)
    if os.path.isfile(os.path.join(cand, "SKILL.md")):
        return cand
    return None


def extract_skill(zip_bytes, dest):
    """把 zip 里的 skills/<name>/ 抽出来放到 dest。"""
    os.makedirs(dest, exist_ok=True)
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    prefix = f"{REPO.split('/')[1]}-main/skills/{SKILL}/"
    n = 0
    for name in z.namelist():
        if not name.startswith(prefix) or name.endswith("/"):
            continue
        rel = name[len(prefix):]
        target = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with z.open(name) as src, open(target, "wb") as out:
            shutil.copyfileobj(src, out)
        n += 1
    if n == 0:
        die(f"仓库结构异常，没找到 skills/{SKILL}/（已下载 {len(z.namelist())} 个条目）")
    return n


def copy_skill(src, dest):
    os.makedirs(dest, exist_ok=True)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            s = os.path.join(root, f)
            rel = os.path.relpath(s, src)
            d = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    return sum(len(fs) for _, _, fs in os.walk(dest))


def detect():
    """返回已安装 agent 的 slug 列表。"""
    found = []
    for slug, path in AGENTS.items():
        p = os.path.expanduser(path)
        if os.path.isdir(p):
            found.append(slug)
    return found


def agent_of_process():
    """猜当前跑的是哪个 agent（看环境变量/进程）。"""
    env = os.environ
    for slug, keys in {
        "hermes": ("HERMES_AGENT", "HERMES_SESSION_ID"),
        "claude-code": ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"),
        "codex": ("CODEX_HOME",),
        "cursor": ("CURSOR_TRACE_ID",),
        "opencode": ("OPENCODE",),
    }.items():
        if any(env.get(k) for k in keys):
            return slug
    return None


def cmd_list():
    print("支持的 agent 与本机检测：\n")
    print(f"  {'SLUG':<17}{'个人级目录':<42}状态")
    print(f"  {'----':<17}{'--------':<42}----")
    for slug, path in AGENTS.items():
        p = os.path.expanduser(path)
        if os.path.isdir(p):
            st = "✅ 目录存在"
        elif os.path.isdir(os.path.dirname(p)):
            st = "⚠️  上级目录存在"
        else:
            st = "—  未检测到"
        print(f"  {slug:<17}{p:<42}{st}")
    print("\n  通用目录 ~/.agents/skills/ 被多数 agent 共用，装那里最省事。")
    cur = agent_of_process()
    if cur:
        print(f"  当前进程看起来是: {cur}")


def cmd_uninstall():
    n = 0
    for slug, path in AGENTS.items():
        dest = os.path.join(os.path.expanduser(path), SKILL)
        if os.path.isdir(dest) or os.path.islink(dest):
            shutil.rmtree(dest, ignore_errors=True)
            print(f"  🗑  已移除 {dest}")
            n += 1
    if n == 0:
        print("  没找到已安装的 dushe-2bti")


def verify(dest):
    """装完跑一次真实渲染，确认能用。"""
    script = os.path.join(dest, "scripts", "render.py")
    sample = os.path.join(dest, "assets", "profile.example.json")
    if not os.path.isfile(script) or not os.path.isfile(sample):
        print("  ⚠️  文件不完整，跳过验证")
        return False
    out = os.path.join(tempfile.gettempdir(), "dushe-2bti-verify.html")
    try:
        r = subprocess.run([sys.executable, script, sample, "-o", out],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"  ⚠️  验证失败: {e}")
        return False
    if r.returncode == 0 and os.path.isfile(out):
        print(f"  ✅ 渲染验证通过（{os.path.getsize(out)//1024} KB）")
        return True
    print(f"  ⚠️  验证未通过:\n{(r.stderr or '')[-400:]}")
    return False


def install(target=None):
    src_local = local_skill_dir()
    zip_bytes = None
    if src_local:
        print(f"来源：本地仓库 {src_local}")
    else:
        print("来源：GitHub 下载中…")
        zip_bytes = download_skill_zip()

    if target:
        targets = [("custom", os.path.expanduser(target))]
    else:
        found = detect()
        if not found:
            print("\n没检测到任何已装的 agent。默认装到通用目录 ~/.agents/skills/")
            print("（Claude Code 除外——它读 ~/.claude/skills/，请手动再装一次）\n")
            targets = [("universal", os.path.expanduser(AGENTS["codex"]))]
        else:
            cur = agent_of_process()
            if cur and cur in found:
                found = [cur] + [x for x in found if x != cur]
            dirs, seen = [], set()
            for slug in found:
                d = os.path.expanduser(AGENTS[slug])
                if d not in seen:
                    seen.add(d)
                    dirs.append((slug, d))
            targets = dirs

    ok = True
    for slug, base in targets:
        dest = os.path.join(base, SKILL)
        if os.path.isdir(dest) or os.path.islink(dest):
            print(f"\n[{slug}] 已存在，先移除: {dest}")
            shutil.rmtree(dest, ignore_errors=True)
        os.makedirs(base, exist_ok=True)
        if src_local:
            n = copy_skill(src_local, dest)
        else:
            n = extract_skill(zip_bytes, dest)
        print(f"[{slug}] 已安装 {n} 个文件 → {dest}")
        if not verify(dest):
            ok = False

    print("\n" + "=" * 52)
    if ok:
        print("✅ 安装完成。")
        print("\n下一步：")
        print('  跟你的 agent 说一句「毒舌我一下」或「给我出个人格报告」')
        print("  （新开一个会话让它重新扫描 skill 目录）")
    else:
        print("⚠️  安装完成但验证未通过，请检查上面的错误。")
    print("=" * 52)


def main():
    ap = argparse.ArgumentParser(description="毒舌2BTI 零依赖安装器")
    ap.add_argument("--target", help="装到指定目录（默认自动探测）")
    ap.add_argument("--list", action="store_true", help="列出支持的 agent")
    ap.add_argument("--uninstall", action="store_true", help="卸载")
    a = ap.parse_args()

    if a.list:
        cmd_list()
    elif a.uninstall:
        cmd_uninstall()
    else:
        install(a.target)


if __name__ == "__main__":
    main()
