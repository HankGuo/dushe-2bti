#!/usr/bin/env bash
# 毒舌2BTI · 一键安装
# 探测本机已装的 agent，装到对应目录；也支持手动指定。
#
#   ./install.sh                 # 自动探测
#   ./install.sh claude-code     # 指定 agent
#   ./install.sh --list          # 列出支持的 agent 和本机检测结果
#   ./install.sh --uninstall     # 卸载

set -euo pipefail

SKILL_NAME="dushe-2bti"
REPO="HankGuo/dushe-2bti"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/skills/$SKILL_NAME"

# agent slug : 个人级目录 : 项目级目录
# slug 跟 gh skill install --agent 的取值对齐
AGENTS=(
  "claude-code|$HOME/.claude/skills"
  "codex|$HOME/.agents/skills"
  "cursor|$HOME/.cursor/skills"
  "gemini-cli|$HOME/.gemini/skills"
  "github-copilot|$HOME/.copilot/skills"
  "opencode|$HOME/.config/opencode/skills"
  "openclaw|$HOME/.openclaw/skills"
  "hermes|$HOME/.hermes/skills"
  "universal|$HOME/.agents/skills"
  "agents|$HOME/.agents/skills"
)

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

list_agents() {
  echo "支持的 agent："
  echo
  printf "  %-12s %-38s %s\n" "SLUG" "个人级目录" "本机检测"
  printf "  %-12s %-38s %s\n" "----" "--------" "--------"
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r slug home <<< "$entry"
    if [ -d "$home" ]; then
      mark="✅ 已安装目录"
    elif [ -d "$(dirname "$home")" ]; then
      mark="⚠️  上级目录存在"
    else
      mark="—  未检测到"
    fi
    printf "  %-12s %-38s %s\n" "$slug" "$home" "$mark"
  done
  echo
  echo "  说明：.agents/skills/ 是 Agent Skills 开放标准的通用目录，"
  echo "        除 Claude Code 外几乎所有 agent 都读它。"
}

detect_agents() {
  local found=()
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r slug home <<< "$entry"
    [ -d "$home" ] && found+=("$slug")
  done
  printf '%s\n' "${found[@]}" | sort -u
}

install_one() {
  local slug="$1" home="$2"
  local dest="$home/$SKILL_NAME"
  mkdir -p "$home"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "  ⚠️  已存在，先移除：$dest"
    rm -rf "$dest"
  fi
  # 用符号链接（仓库更新即同步）；不支持时退回复制
  if ln -s "$SRC" "$dest" 2>/dev/null; then
    echo "  ✅ $slug → $dest  (symlink)"
  else
    cp -r "$SRC" "$dest"
    echo "  ✅ $slug → $dest  (copy)"
  fi
}

uninstall_all() {
  local n=0
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r slug home <<< "$entry"
    local dest="$home/$SKILL_NAME"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      rm -rf "$dest"; echo "  🗑  已移除 $dest"; n=$((n+1))
    fi
  done
  [ "$n" -eq 0 ] && echo "  没有找到已安装的 $SKILL_NAME"
}

# ---------- 参数处理 ----------
case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  --list) list_agents; exit 0 ;;
  --uninstall) uninstall_all; exit 0 ;;
esac

echo "毒舌2BTI 安装器"
echo "═══════════════"
echo

if [ -n "${1:-}" ]; then
  TARGET="$1"
  FOUND=""
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r slug home <<< "$entry"
    [ "$slug" = "$TARGET" ] && FOUND="$entry"
  done
  if [ -z "$FOUND" ]; then
    echo "❌ 不支持的 agent: $TARGET"; echo; list_agents; exit 1
  fi
  IFS='|' read -r slug home _ <<< "$FOUND"
  install_one "$slug" "$home"
  echo
  echo "完成。重启你的 agent 会话即可使用。"
  exit 0
fi

# 自动探测
DETECTED="$(detect_agents)"
if [ -z "$DETECTED" ]; then
  echo "❌ 没检测到任何已安装的 agent。"
  echo
  list_agents
  echo "手动指定：./install.sh claude-code"
  exit 1
fi

echo "检测到 agent：$(echo "$DETECTED" | tr '\n' ' ')"
echo
for slug in $DETECTED; do
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r s home _ <<< "$entry"
    if [ "$s" = "$slug" ]; then install_one "$slug" "$home"; fi
  done
done

echo
echo "完成。重启你的 agent 会话即可使用。"
echo "用法：让 agent「毒舌我一下」或「给我出个人格报告」。"
