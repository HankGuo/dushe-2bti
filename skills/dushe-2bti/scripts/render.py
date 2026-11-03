#!/usr/bin/env python3
"""毒舌2BTI 渲染器 v3：JSON → 自包含 HTML（词云 + 雷达 + 象限 + 毒舌 + 传播区）。

用法:
    python3 render.py profile.json -o out.html
    python3 render.py profile.json -o out.html --png out.png --mobile
    python3 render.py profile.json -o out.html --name "张三"

设计:
    - 零外部依赖（无 CDN），离线可用，可直接开源分发
    - 词云: Canvas + sprite-mask 位图碰撞（真实字形轮廓，非矩形包围盒）
    - 雷达: Canvas 手绘六边形
    - 象限: CSS/HTML 绘制
    - 16 型人格坐标系（4 轴 × 2 极）
    - 目标名不硬编码：--name > DUSHE_NAME > USER/USERNAME/LOGNAME > HOSTNAME > 兜底
"""
import json
import sys
import html
import argparse
import subprocess
import os
import shutil
import tempfile

# ---- 16 型配色表（与 references/2bti-taxonomy.md 保持一致）----
THEMES = {
    # 大族 A：B（能造）× R（野）
    "BR-SL": {"a": "#ff4d6d", "b": "#ff9f1c"},
    "BR-SF": {"a": "#ff2e63", "b": "#ff6b6b"},
    "BR-DL": {"a": "#e8590c", "b": "#f59f00"},
    "BR-DF": {"a": "#d6336c", "b": "#f06595"},
    # 大族 B：B（能造）× T（稳）
    "BT-SL": {"a": "#2ec4b6", "b": "#4361ee"},
    "BT-SF": {"a": "#20c997", "b": "#0ca678"},
    "BT-DL": {"a": "#1098ad", "b": "#0b7285"},
    "BT-DF": {"a": "#495057", "b": "#868e96"},
    # 大族 C：P（纸上）× R（野）
    "PR-SL": {"a": "#f72585", "b": "#7209b7"},
    "PR-SF": {"a": "#c2255c", "b": "#9c36b5"},
    "PR-DL": {"a": "#5f3dc4", "b": "#7048e8"},
    "PR-DF": {"a": "#862e9c", "b": "#ae3ec9"},
    # 大族 D：P（纸上）× T（稳）
    "PT-SL": {"a": "#9d4edd", "b": "#4cc9f0"},
    "PT-SF": {"a": "#7048e8", "b": "#3bc9db"},
    "PT-DL": {"a": "#4263eb", "b": "#3b5bdb"},
    "PT-DF": {"a": "#364fc7", "b": "#4263eb"},
}

# ---- 16 型名称表 ----
TYPE_NAMES = {
    "BR-SL": ("莽夫", "THE BULL"),        "BR-SF": ("疯批", "THE WILDFIRE"),
    "BR-DL": ("狠人", "THE MACHINE"),     "BR-DF": ("游击队长", "THE MAVERICK"),
    "BT-SL": ("军令型", "THE COMMANDER"),  "BT-SF": ("缝合怪", "THE COLLECTOR"),
    "BT-DL": ("铁匠", "THE SMITH"),        "BT-DF": ("掌柜", "THE OPERATOR"),
    "PR-SL": ("戏精", "THE PERFORMER"),    "PR-SF": ("键鼠侠", "THE KEYBOARD"),
    "PR-DL": ("空想家", "THE DREAMER"),    "PR-DF": ("甩锅王", "THE DIVIDER"),
    "PT-SL": ("军师", "THE STRATEGIST"),   "PT-SF": ("观察员", "THE OBSERVER"),
    "PT-DL": ("苦行僧", "THE ASCETIC"),    "PT-DF": ("记录官", "THE SCRIBE"),
}

# ---- 每型的专属视觉元素：符号 / 罪状条 / 水印 / 印章 ----
# symbol 用彩色 emoji（系统有 Noto Color Emoji）
TYPE_GLYPHS = {
    "BR-SL": {"sym": "⚡", "charge": "现场直击",   "stamp": "说干就干"},
    "BR-SF": {"sym": "🔥", "charge": "失控现场",   "stamp": "想到就烧"},
    "BR-DL": {"sym": "⚙️", "charge": "流水线作业", "stamp": "停不下来"},
    "BR-DF": {"sym": "🎯", "charge": "专挑硬骨头", "stamp": "打完就跑"},
    "BT-SL": {"sym": "🎖️", "charge": "下达命令",   "stamp": "说到做到"},
    "BT-SF": {"sym": "🧩", "charge": "东拼西凑",   "stamp": "什么都收"},
    "BT-DL": {"sym": "🔨", "charge": "交付现场",   "stamp": "造得出还稳"},
    "BT-DF": {"sym": "🏪", "charge": "生意兴隆",   "stamp": "系统跑着"},
    "PR-SL": {"sym": "🎭", "charge": "排练现场",   "stamp": "情绪先行"},
    "PR-SF": {"sym": "⌨️", "charge": "键盘江湖",   "stamp": "纵横四海"},
    "PR-DL": {"sym": "💭", "charge": "脑内上市",   "stamp": "想得真美"},
    "PR-DF": {"sym": "🏳️", "charge": "责任转移",   "stamp": "执行不归我"},
    "PT-SL": {"sym": "♟", "charge": "沙盘推演",   "stamp": "想得比谁透"},
    "PT-SF": {"sym": "👁", "charge": "现场观察",   "stamp": "看得很准"},
    "PT-DL": {"sym": "🕯", "charge": "修行记录",   "stamp": "计划完美"},
    "PT-DF": {"sym": "🗂", "charge": "卷宗归档",   "stamp": "整理得头头是道"},
}

# ---- 四族视觉语言（背景纹理 / 雷达填充样式 / 卡片质感）----
# family 由 type_code 前两位决定
FAMILIES = {
    "BR": {
        "label": "施工现场",
        "pattern": "hazard",     # 斜向警示条纹
        "radar": "stripe",       # 雷达图斜纹填充
        "border": "3px solid",   # 粗边框
        "radius": "6px",         # 硬朗直角
        "shadow": "8px 8px 0",   # 硬阴影偏移
    },
    "BT": {
        "label": "工程蓝图",
        "pattern": "blueprint",  # 细网格 + 十字准线
        "radar": "gradient",
        "border": "1px solid",
        "radius": "18px",
        "shadow": "0 0 0 1px, 0 14px 40px",
    },
    "PR": {
        "label": "舞台聚光",
        "pattern": "spotlight",   # 顶部聚光锥
        "radar": "soft",
        "border": "2px double",
        "radius": "26px",
        "shadow": "0 18px 50px",
    },
    "PT": {
        "label": "公文档案",
        "pattern": "ledger",      # 横线稿纸 + 装订线
        "radar": "cross",
        "border": "1px solid",
        "radius": "3px",
        "shadow": "0 10px 30px",
    },
}


DIM_META = [
    ("ideate", "构想力"),
    ("exec",   "落地力"),
    ("arch",   "架构脑"),
    ("curio",  "探索欲"),
    ("tough",  "抗压值"),
    ("social", "社交电量"),
]


def resolve_subject(explicit: str = "") -> str:
    """解析目标名：--name > DUSHE_NAME > USER/USERNAME/LOGNAME > HOSTNAME > 兜底。

    DUSHE_NAME 用合法 shell 变量名（不能以数字开头，所以不用 2BTI_NAME）。
    为兼容某些用程序设环境变量的场景，仍读 2BTI_NAME 作为次选。
    绝不硬编码任何人名。
    """
    if explicit:
        return explicit.strip()
    for key in ("DUSHE_NAME", "2BTI_NAME", "USER", "USERNAME", "LOGNAME", "HOSTNAME"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return "路人甲"


def classify(dims: dict) -> str:
    """按四轴规则算出 16 型代号。"""
    g = lambda *ks: sum(float(dims.get(k, 50)) for k in ks) / len(ks)
    bp = g("exec", "arch")
    rt = g("curio", "ideate")
    sd = g("social", "tough")
    lf = g("tough", "exec")
    return (f"{'B' if bp >= 60 else 'P'}{'R' if rt >= 60 else 'T'}"
            f"-{'S' if sd >= 55 else 'D'}{'L' if lf >= 60 else 'F'}")


def esc(s):
    return html.escape(str(s), quote=True)


def build_html(p: dict, subject: str = "") -> str:
    dims = p.get("dimensions", {})
    code = p.get("type_code") or classify(dims)
    th = THEMES.get(code, THEMES["BR-SL"])
    default_name, default_en = TYPE_NAMES.get(code, ("神秘人", "THE UNKNOWN"))
    name = p.get("type_name") or default_name
    en = p.get("type_en") or default_en
    subject = subject or p.get("subject") or resolve_subject()
    title = p.get("title") or f"毒舌2BTI · {subject}"
    dim_data = [{"key": k, "label": lbl, "value": int(dims.get(k, 50))} for k, lbl in DIM_META]
    wc = p.get("wordcloud", [])
    share = p.get("share", {})

    roast_html = "\n".join(
        f'      <li class="roast-item"><span class="roast-idx">{i+1:02d}</span>'
        f'<span class="roast-text">{esc(r)}</span></li>'
        for i, r in enumerate(p.get("roast", []))
    )
    ev_html = "\n".join(
        f'      <li><span class="ev-claim">{esc(e.get("claim",""))}</span>'
        f'<span class="ev-proof">{esc(e.get("proof",""))}</span></li>'
        for e in p.get("evidence", [])
    )

    # 象限轴
    axis_html = ""
    for a in p.get("axis_explain", []):
        left = esc(a.get("left", ""))
        right = esc(a.get("right", ""))
        score = int(a.get("score", 50))
        verdict = esc(a.get("verdict", ""))
        axis_html += f"""
    <div class="axis">
      <div class="axis-head">
        <span class="axis-name">{esc(a.get('axis',''))}</span>
        <span class="axis-verdict">{verdict}</span>
      </div>
      <div class="axis-track">
        <span class="axis-side">{left}</span>
        <div class="axis-bar"><div class="axis-fill" style="width:{score}%"></div></div>
        <span class="axis-side axis-right">{right}</span>
      </div>
      <div class="axis-score">{score} / 100</div>
    </div>"""

    hashtags = "".join(f'<span class="tag">{esc(t)}</span>' for t in share.get("hashtags", []))
    rating = p.get("rating", "★☆☆☆☆")
    rating_label = p.get("rating_label", "")
    ev_block = ""
    if p.get("evidence"):
        ev_block = (
            '<div class="card" style="margin-bottom:20px;">\n'
            '    <div class="card-title"><span class="n">05</span> 判决依据</div>\n'
            '    <ul class="ev-list">\n' + ev_html + '\n    </ul>\n  </div>'
        )

    # ---- 视觉语言：族 + 型 ----
    family_key = code[:2]
    fam = FAMILIES.get(family_key, FAMILIES["BT"])
    gl = TYPE_GLYPHS.get(code, {"sym": "🧿", "charge": "综合症状", "stamp": "未确诊"})

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>
  :root {{
    --a: {th['a']}; --b: {th['b']};
    --ink:#0a0a11; --txt:#f4f4f8; --dim:#b6b6c8; --dim2:#8e8ea2;
    --line:#26263a;
    --pat: {fam['pattern']}; --radar-style: {fam['radar']};
    --card-border: {fam['border']}; --card-radius: {fam['radius']};
    --card-shadow: {fam['shadow']};
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}

  /* ============ 四族背景纹理 ============ */
  body.fam-BR {{
    background:
      repeating-linear-gradient(45deg, rgba(255,255,255,.020) 0 22px, transparent 22px 44px),
      radial-gradient(900px 600px at 12% -8%, color-mix(in srgb,var(--a) 26%,transparent), transparent 62%),
      radial-gradient(700px 500px at 88% 4%, color-mix(in srgb,var(--b) 18%,transparent), transparent 58%),
      var(--ink);
  }}
  body.fam-BT {{
    background:
      repeating-linear-gradient(0deg, rgba(120,180,255,.045) 0 1px, transparent 1px 34px),
      repeating-linear-gradient(90deg, rgba(120,180,255,.045) 0 1px, transparent 1px 34px),
      radial-gradient(1100px 700px at 18% -10%, color-mix(in srgb,var(--a) 24%,transparent), transparent 62%),
      radial-gradient(800px 600px at 90% 8%, color-mix(in srgb,var(--b) 18%,transparent), transparent 58%),
      #070b14;
  }}
  body.fam-PR {{
    background:
      radial-gradient(760px 900px at 50% -18%, rgba(255,255,255,.16), transparent 62%),
      radial-gradient(1000px 620px at 12% 2%, color-mix(in srgb,var(--a) 26%,transparent), transparent 60%),
      radial-gradient(900px 600px at 90% 6%, color-mix(in srgb,var(--b) 22%,transparent), transparent 58%),
      #0d0714;
  }}
  body.fam-PT {{
    background:
      repeating-linear-gradient(0deg, rgba(255,255,255,.032) 0 1px, transparent 1px 30px),
      linear-gradient(90deg, rgba(255,255,255,.05) 0 34px, transparent 34px),
      radial-gradient(1000px 680px at 14% -6%, color-mix(in srgb,var(--a) 18%,transparent), transparent 60%),
      #0c0c12;
  }}

  body {{
    color:var(--txt);
    font-family:"Noto Sans CJK SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
    min-height:100vh; padding:44px 22px 64px; -webkit-font-smoothing:antialiased;
  }}
  .wrap {{ max-width:1120px; margin:0 auto; }}

  /* ---------- 头部 ---------- */
  .head {{ text-align:center; margin-bottom:26px; }}
  .kicker {{
    display:inline-block; font-size:12px; letter-spacing:.44em; color:var(--dim);
    border:1px solid #32324a; border-radius:99px; padding:6px 20px; margin-bottom:18px;
  }}
  .title {{
    font-size:clamp(36px,6vw,68px); font-weight:900; line-height:1.06; letter-spacing:-.02em;
    background:linear-gradient(100deg,var(--a),var(--b) 58%,var(--a));
    -webkit-background-clip:text; background-clip:text; color:transparent;
    filter:drop-shadow(0 6px 24px color-mix(in srgb,var(--a) 40%,transparent));
  }}
  .subtitle {{
    margin-top:14px; font-size:clamp(14px,1.7vw,19px); color:#d2d2e0;
    max-width:820px; margin-left:auto; margin-right:auto; line-height:1.7;
  }}

  /* ---------- 人格结论卡 ---------- */
  .verdict {{
    display:grid; grid-template-columns:auto 1fr; gap:0; align-items:stretch;
    border:1px solid color-mix(in srgb,var(--a) 40%,transparent); border-radius:22px; overflow:hidden;
    margin:26px 0 22px; background:linear-gradient(120deg,color-mix(in srgb,var(--a) 14%,transparent),transparent 55%);
  }}
  .verdict-left {{
    padding:26px 30px; display:flex; flex-direction:column; justify-content:center; align-items:center;
    background:linear-gradient(140deg,color-mix(in srgb,var(--a) 32%,transparent),color-mix(in srgb,var(--b) 24%,transparent));
    border-right:1px solid color-mix(in srgb,var(--a) 30%,transparent); min-width:210px;
  }}
  .v-code {{ font-size:46px; font-weight:900; letter-spacing:.04em; color:#fff; line-height:1; }}
  .v-name {{ font-size:21px; font-weight:800; margin-top:8px; }}
  .v-en {{ font-size:12px; color:#dcdce8; letter-spacing:.16em; margin-top:3px; }}
  .verdict-right {{ padding:24px 28px; display:flex; flex-direction:column; gap:16px; justify-content:center; }}
  .v-desc {{ font-size:16.5px; color:#eaeaf2; line-height:1.6; }}
  .manifesto {{
    font-size:15.5px; line-height:1.85; color:#dcdce8; padding-left:16px;
    border-left:3px solid var(--b); font-style:italic;
  }}
  .v-meta {{ display:flex; gap:22px; flex-wrap:wrap; align-items:center; margin-top:2px; }}
  .stars {{ font-size:26px; color:var(--b); letter-spacing:.1em; line-height:1; }}
  .stars-lbl {{ font-size:13.5px; color:#c2c2d2; }}
  .stars-lbl b {{ color:var(--b); font-size:15px; }}

  /* ---------- 卡片（质感随族变化） ---------- */
  .card {{
    background:linear-gradient(160deg,rgba(255,255,255,.055),rgba(255,255,255,.018));
    border:var(--card-border) color-mix(in srgb,var(--a) 34%,var(--line));
    border-radius:var(--card-radius);
    padding:22px 24px; box-shadow:var(--card-shadow);
  }}
  body.fam-BR .card {{ border-color:color-mix(in srgb,var(--a) 55%,transparent); }}
  body.fam-BT .card {{ border-color:rgba(120,180,255,.22); }}
  body.fam-PR .card {{ border-color:color-mix(in srgb,var(--a) 46%,transparent); }}
  body.fam-PT .card {{ border-color:rgba(255,255,255,.14); }}

  /* ---------- 类型符号徽章（每型专属 emoji，带底板保证深色 emoji 也可见） ---------- */
  .sym-badge {{
    width:76px; height:76px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:38px; line-height:1; margin-bottom:12px; position:relative;
    background:
      radial-gradient(circle at 32% 26%, rgba(255,255,255,.32), transparent 58%),
      linear-gradient(145deg, var(--a), var(--b));
    border:2px solid rgba(255,255,255,.42);
    box-shadow:0 8px 22px color-mix(in srgb,var(--a) 42%,transparent), inset 0 -3px 10px rgba(0,0,0,.30);
    font-family:"Noto Color Emoji","Apple Color Emoji","Segoe UI Emoji",sans-serif;
  }}
  .sym-badge::after {{
    content:""; position:absolute; inset:-6px; border-radius:50%;
    border:1px dashed color-mix(in srgb,var(--b) 45%,transparent);
  }}
  body.fam-BR .sym-badge {{ border-radius:12px; }}
  body.fam-BT .sym-badge {{ border-radius:6px; }}
  body.fam-PR .sym-badge {{ border-radius:50%; border-width:3px; }}
  body.fam-PT .sym-badge {{ border-radius:4px; border-style:double; border-width:4px; }}
  .charge {{
    display:inline-block; font-size:11px; letter-spacing:.24em; font-weight:800;
    color:#fff; background:linear-gradient(90deg,var(--a),var(--b));
    padding:5px 15px; border-radius:99px; margin-bottom:12px;
  }}
  .stamp {{
    margin-top:12px; display:inline-block; font-size:14px; font-weight:900; letter-spacing:.16em;
    color:var(--b); border:2px solid color-mix(in srgb,var(--b) 60%,transparent);
    padding:4px 14px; border-radius:6px; transform:rotate(-4deg);
  }}
  body.fam-PT .stamp {{ border-radius:2px; transform:rotate(-2deg); border-style:double; border-width:3px; }}
  body.fam-BR .stamp {{ transform:rotate(-6deg); border-radius:4px; }}

  .card-title {{
    font-size:12.5px; letter-spacing:.3em; color:var(--dim); margin-bottom:14px;
    display:flex; align-items:center; gap:10px; font-weight:700;
  }}
  .card-title::after {{ content:""; flex:1; height:1px; background:linear-gradient(90deg,#32324a,transparent); }}
  .card-title .n {{ color:var(--a); }}

  /* ---------- 词云在前的第一屏 ---------- */
  .hero {{ display:grid; grid-template-columns:1.12fr .88fr; gap:20px; align-items:stretch; margin-bottom:20px; }}
  @media (max-width:880px) {{ .hero {{ grid-template-columns:1fr; }} }}
  .hero .card {{ display:flex; flex-direction:column; }}
  .hero canvas {{ width:100%; flex:1; }}
  #cloud {{ aspect-ratio:1.12/1; min-height:340px; }}
  #radar {{ aspect-ratio:1/1; }}

  /* ---------- 象限轴 ---------- */
  .axis-wrap {{ display:grid; grid-template-columns:1fr 1fr; gap:26px; }}
  @media (max-width:760px) {{ .axis-wrap {{ grid-template-columns:1fr; gap:20px; }} }}
  .axis-head {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:9px; }}
  .axis-name {{ font-size:14.5px; font-weight:700; color:#e4e4ee; }}
  .axis-verdict {{ font-size:12px; font-weight:800; letter-spacing:.14em; color:var(--a); }}
  .axis-track {{ display:flex; align-items:center; gap:11px; }}
  .axis-side {{ font-size:12px; color:var(--dim); white-space:nowrap; }}
  .axis-right {{ text-align:right; }}
  .axis-bar {{ flex:1; height:9px; background:#1e1e2c; border-radius:99px; overflow:hidden; }}
  .axis-fill {{ height:100%; background:linear-gradient(90deg,var(--b),var(--a)); border-radius:99px; box-shadow:0 0 12px color-mix(in srgb,var(--a) 55%,transparent); }}
  .axis-score {{ font-size:11.5px; color:var(--dim2); margin-top:6px; text-align:right; }}

  /* ---------- 毒舌 ---------- */
  .roast-list {{ list-style:none; display:flex; flex-direction:column; gap:13px; }}
  .roast-item {{
    display:flex; gap:14px; align-items:flex-start; padding:15px 16px; border-radius:14px;
    background:rgba(255,255,255,.035); border:1px solid #25253a; border-left:3px solid var(--a);
    font-size:15px; line-height:1.78; color:#ececf4;
  }}
  .roast-item:nth-child(even) {{ border-left-color:var(--b); }}
  .roast-idx {{
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; font-weight:700;
    color:var(--dim); background:#1d1d2c; border-radius:7px; padding:3px 7px; flex:none; margin-top:4px;
  }}

  /* ---------- 证据 ---------- */
  .ev-list {{ list-style:none; display:flex; flex-direction:column; gap:11px; }}
  .ev-list li {{ display:flex; flex-direction:column; gap:5px; padding:12px 15px;
    border-radius:12px; background:rgba(255,255,255,.03); border:1px solid #232336; }}
  .ev-claim {{ font-size:14px; font-weight:700; color:var(--b); }}
  .ev-proof {{ font-size:13px; color:#b6b6c8; line-height:1.66; }}

  /* ---------- 传播区 ---------- */
  .share {{
    margin-top:22px; border-radius:20px; padding:26px 28px; text-align:center;
    background:linear-gradient(135deg,color-mix(in srgb,var(--a) 18%,transparent),color-mix(in srgb,var(--b) 14%,transparent));
    border:1px solid color-mix(in srgb,var(--a) 32%,transparent);
  }}
  .share-lbl {{ font-size:11.5px; letter-spacing:.34em; color:var(--dim); margin-bottom:12px; }}
  .share-line {{ font-size:clamp(16px,2.3vw,23px); font-weight:800; line-height:1.6; color:#fff; max-width:820px; margin:0 auto 18px; }}
  .share-tags {{ display:flex; gap:9px; justify-content:center; flex-wrap:wrap; }}
  .tag {{ font-size:13px; color:#dcdce8; background:rgba(255,255,255,.07);
    border:1px solid #3a3a52; border-radius:99px; padding:5px 14px; }}

  .foot {{ margin-top:28px; text-align:center; font-size:12px; color:#8e8ea2; letter-spacing:.07em; line-height:1.9; }}
  .foot .brand {{ color:var(--a); font-weight:700; letter-spacing:.22em; }}

  canvas {{ display:block; }}
</style>
</head>
<body class="fam-{family_key}">
<div class="wrap">

  <div class="head">
    <div class="kicker">毒 舌 2 B T I · 算 力 白 肉 · {esc(fam['label'])}</div>
    <h1 class="title">{esc(title)}</h1>
    <div class="subtitle">{esc(p.get('subtitle',''))}</div>
  </div>

  <div class="verdict">
    <div class="verdict-left">
      <span class="sym-badge">{gl['sym']}</span>
      <div class="charge">{esc(gl['charge'])}</div>
      <div class="v-code">{esc(code)}</div>
      <div class="v-name">{esc(name)}</div>
      <div class="v-en">{esc(en)}</div>
    </div>
    <div class="verdict-right">
      <div class="v-desc">{esc(p.get('type_desc',''))}</div>
      <div class="manifesto">{esc(p.get('manifesto',''))}</div>
      <div class="v-meta">
        <span class="stars">{esc(rating)}</span>
        <span class="stars-lbl">毒舌评级 · <b>{esc(rating_label)}</b></span>
        <span class="stamp">{esc(gl['stamp'])}</span>
      </div>
    </div>
  </div>

  <div class="hero">
    <div class="card">
      <div class="card-title"><span class="n">01</span> 人格词云</div>
      <canvas id="cloud"></canvas>
    </div>
    <div class="card">
      <div class="card-title"><span class="n">02</span> 六维人格雷达</div>
      <canvas id="radar"></canvas>
    </div>
  </div>

  <div class="card" style="margin-bottom:20px;">
    <div class="card-title"><span class="n">03</span> 象限定位</div>
    <div class="axis-wrap">{axis_html}
    </div>
  </div>

  <div class="card" style="margin-bottom:20px;">
    <div class="card-title"><span class="n">04</span> 毒舌解剖</div>
    <ul class="roast-list">
{roast_html}
    </ul>
  </div>

  {ev_block}

  <div class="share">
    <div class="share-lbl">一 句 话 转 发</div>
    <div class="share-line">{esc(share.get('one_liner', p.get('subtitle','')))}</div>
    <div class="share-tags">{hashtags}</div>
  </div>

  <div class="foot">
    <span class="brand">毒舌2BTI</span> · 算力白肉 · 16型人格坐标系<br>
    生成于 {esc(p.get('meta',{}).get('generated_at',''))} · 本报告 100% 属实，0% 温柔
  </div>
</div>

<script>
const DIM = {json.dumps(dim_data, ensure_ascii=False)};
const WC  = {json.dumps(wc, ensure_ascii=False)};
const THEME = {{a:"{th['a']}", b:"{th['b']}"}};
const RADAR_STYLE = "{fam['radar']}";

function dpr(){{ return Math.min(window.devicePixelRatio||1, 2); }}
function setupCanvas(el){{
  const r = el.getBoundingClientRect();
  const d = dpr();
  el.width = Math.round(r.width*d); el.height = Math.round(r.height*d);
  const ctx = el.getContext('2d');
  ctx.setTransform(d,0,0,d,0,0);
  return {{ctx, w:r.width, h:r.height}};
}}

/* ================= 雷达图 ================= */
function drawRadar(){{
  const el = document.getElementById('radar');
  const {{ctx,w,h}} = setupCanvas(el);
  const cx = w/2, cy = h/2 + 4;
  const R = Math.min(w,h)*0.32;
  const N = DIM.length;
  const ang = i => -Math.PI/2 + i*2*Math.PI/N;

  for (let ring=1; ring<=5; ring++){{
    const r = R*ring/5;
    ctx.beginPath();
    for (let i=0;i<=N;i++){{
      const a = ang(i%N), x = cx+Math.cos(a)*r, y = cy+Math.sin(a)*r;
      i? ctx.lineTo(x,y) : ctx.moveTo(x,y);
    }}
    ctx.closePath();
    ctx.strokeStyle = ring===5 ? 'rgba(255,255,255,.20)' : 'rgba(255,255,255,.075)';
    ctx.lineWidth = 1; ctx.stroke();
    if (ring===5){{
      ctx.fillStyle='rgba(255,255,255,.30)'; ctx.font='10px sans-serif';
      ctx.textAlign='left'; ctx.fillText(String(ring*20), cx+3, cy-r+9);
    }}
  }}
  for (let i=0;i<N;i++){{
    const a = ang(i);
    ctx.beginPath(); ctx.moveTo(cx,cy);
    ctx.lineTo(cx+Math.cos(a)*R, cy+Math.sin(a)*R);
    ctx.strokeStyle='rgba(255,255,255,.09)'; ctx.stroke();
  }}

  const pts = DIM.map(d=>{{
    const a=ang(DIM.indexOf(d)), r=R*d.value/100;
    return [cx+Math.cos(a)*r, cy+Math.sin(a)*r];
  }});
  const g = ctx.createRadialGradient(cx,cy,0,cx,cy,R);
  g.addColorStop(0,'rgba(255,255,255,.34)'); g.addColorStop(1,'rgba(255,255,255,.05)');
  ctx.beginPath();
  pts.forEach((p,i)=> i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));
  ctx.closePath();

  // 按族切换填充质感：stripe / gradient / soft / cross
  const RS = (typeof RADAR_STYLE !== 'undefined') ? RADAR_STYLE : 'gradient';
  if (RS === 'stripe') {{
    // 斜纹：BR 施工现场
    ctx.save(); ctx.clip();
    ctx.fillStyle = 'rgba(255,255,255,.10)'; ctx.fillRect(0,0,w,h);
    ctx.strokeStyle = 'rgba(255,255,255,.13)'; ctx.lineWidth = 2.2;
    for (let k=-h; k<w; k+=9) {{ ctx.beginPath(); ctx.moveTo(k,0); ctx.lineTo(k+h,h); ctx.stroke(); }}
    ctx.restore();
  }} else if (RS === 'cross') {{
    // 交叉斜线：PT 公文档案
    ctx.save(); ctx.clip();
    ctx.fillStyle = 'rgba(255,255,255,.09)'; ctx.fillRect(0,0,w,h);
    ctx.strokeStyle = 'rgba(255,255,255,.11)'; ctx.lineWidth = 1;
    for (let k=-h; k<w; k+=10) {{ ctx.beginPath(); ctx.moveTo(k,0); ctx.lineTo(k+h,h); ctx.stroke();
                                   ctx.beginPath(); ctx.moveTo(k,0); ctx.lineTo(k-h,h); ctx.stroke(); }}
    ctx.restore();
  }} else if (RS === 'soft') {{
    // 柔和径向：PR 舞台聚光
    const sg = ctx.createRadialGradient(cx,cy*0.72,0,cx,cy*0.72,R*1.15);
    sg.addColorStop(0,'rgba(255,255,255,.42)'); sg.addColorStop(1,'rgba(255,255,255,.03)');
    ctx.fillStyle = sg; ctx.fill();
  }} else {{
    ctx.fillStyle = g; ctx.fill();
  }}
  ctx.strokeStyle=THEME.a; ctx.lineWidth=2.8;
  ctx.shadowColor=THEME.a; ctx.shadowBlur=18; ctx.stroke(); ctx.shadowBlur=0;

  DIM.forEach((d,i)=>{{
    const [x,y] = pts[i];
    ctx.beginPath(); ctx.arc(x,y,4.8,0,7);
    ctx.fillStyle='#fff'; ctx.fill();
    ctx.strokeStyle=THEME.b; ctx.lineWidth=2; ctx.stroke();
    const a=ang(i), lx=cx+Math.cos(a)*(R+31), ly=cy+Math.sin(a)*(R+31);
    ctx.font='700 13px "Noto Sans CJK SC",sans-serif';
    ctx.fillStyle='#eaeaF2'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(d.label, lx, ly-9);
    ctx.font='800 15.5px "Noto Sans CJK SC",sans-serif';
    ctx.fillStyle=THEME.b;
    ctx.fillText(d.value, lx, ly+9);
  }});
}}

/* ================= 词云（sprite-mask 位图碰撞）================= */
function drawCloud(){{
  const el = document.getElementById('cloud');
  const {{ctx,w,h}} = setupCanvas(el);
  if (!WC.length) return;

  const maxW = WC[0].weight, minW = WC[WC.length-1].weight;
  // 画布短边决定基准；字号下限保证可读
  const base = Math.min(w, h);
  const scale = Math.max(0.78, Math.min(base / 400, 1.25));

  // 预渲染每个词到离屏 canvas，取 alpha 作为 sprite
  const items = WC.map((d,i)=>{{
    const t = maxW===minW ? .5 : (d.weight-minW)/(maxW-minW);
    const size = Math.round((17 + t*42) * scale);
    const font = `900 ${{size}}px "Noto Sans CJK SC","Source Han Sans SC",sans-serif`;
    const m = document.createElement('canvas').getContext('2d');
    m.font = font;
    const tw = Math.ceil(m.measureText(d.text).width) + 6;
    const th = Math.ceil(size*1.18);
    const c = document.createElement('canvas');
    c.width = tw; c.height = th;
    const cc = c.getContext('2d');
    cc.font = font; cc.textBaseline='top';
    cc.fillStyle='#fff';
    cc.fillText(d.text, 3, Math.round(th*0.08));
    const img = cc.getImageData(0,0,tw,th).data;
    // 提取 alpha 位图（1=占用）
    const mask = new Uint8Array(tw*th);
    for (let p=0;p<tw*th;p++) mask[p] = img[p*4+3] > 40 ? 1 : 0;
    return {{...d, size, tw, th, mask}};
  }}).sort((a,b)=>b.weight-a.weight);

  // 画布占用位图
  const CW = Math.ceil(w), CH = Math.ceil(h);
  const occupied = new Uint8Array(CW*CH);

  // 配色梯度
  const palette = [THEME.a, THEME.b, '#ffffff', THEME.a, THEME.b, '#ffd166'];

  let placed = 0;
  for (const d of items){{
    // 从中心螺旋向外找位置（中心略上移，给底部留边）
    let done = false;
    const cx0 = CW/2, cy0 = CH*0.47;
    for (let step=0; step<40000 && !done; step++) {{
      const t = step * 0.14;
      const ang = t;
      const rad = 1.9 * t;
      const ox = Math.round(cx0 + Math.cos(ang)*rad - d.tw/2);
      const oy = Math.round(cy0 + Math.sin(ang)*rad*0.80 - d.th/2);
      if (ox < 1 || oy < 1 || ox+d.tw >= CW-1 || oy+d.th >= CH-2) continue;
      // 碰撞检测
      let hit = false;
      for (let y=0; y<d.th && !hit; y++) {{
        const rowBase = (oy+y)*CW + ox;
        const mrow = y*d.tw;
        for (let x=0; x<d.tw; x++) {{
          if (d.mask[mrow+x] && occupied[rowBase+x]) {{ hit=true; break; }}
        }}
      }}
      if (hit) continue;
      // 写入占用
      for (let y=0; y<d.th; y++){{
        const rowBase = (oy+y)*CW + ox;
        const mrow = y*d.tw;
        for (let x=0; x<d.tw; x++) if (d.mask[mrow+x]) occupied[rowBase+x]=1;
      }}
      d.x = ox; d.y = oy;
      done = true; placed++;
    }}
    if (!done) continue;

    ctx.save();
    ctx.shadowColor = d.color || (placed % 3 === 0 ? THEME.a : (placed % 3 === 1 ? THEME.b : '#fff'));
    ctx.shadowBlur = 14;
    ctx.fillStyle = ctx.shadowColor;
    ctx.textBaseline='top';
    ctx.font = `900 ${{d.size}}px "Noto Sans CJK SC","Source Han Sans SC",sans-serif`;
    ctx.fillText(d.text, d.x+3, d.y + Math.round(d.th*0.08));
    ctx.restore();
  }}
}}

// 自动测高：把真实页面高度写到 <html data-pageh>，供截图工具探测
function reportHeight(){{
  document.documentElement.setAttribute('data-pageh', String(Math.ceil(document.body.scrollHeight)));
}}
// 记录徽章中心坐标，便于外部像素审计定位
function reportBadge(){{
  var b = document.querySelector('.sym-badge');
  if (!b) return;
  var r = b.getBoundingClientRect();
  document.documentElement.setAttribute('data-badge',
    Math.round(r.x)+','+Math.round(r.y)+','+Math.round(r.width)+','+Math.round(r.height));
}}
window.addEventListener('load', ()=>setTimeout(()=>{{reportHeight();reportBadge();}}, 350));
setTimeout(()=>{{reportHeight();reportBadge();}}, 1200);
setTimeout(()=>{{reportHeight();reportBadge();}}, 2500);

function drawAll(){{ drawCloud(); drawRadar(); setTimeout(()=>{{reportHeight();reportBadge();}}, 200); }}
if (document.fonts && document.fonts.ready) {{
  document.fonts.ready.then(()=>setTimeout(drawAll,80));
}} else {{ setTimeout(drawAll,150); }}
window.addEventListener('resize', ()=>setTimeout(drawAll,100));
</script>
</body>
</html>"""


def find_chrome():
    """跨平台探测 Chrome / Chromium / Edge / Arc / Brave 等浏览器路径。"""
    env_c = os.environ.get("CHROME_BIN") or os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if env_c and os.path.exists(env_c):
        return env_c

    candidates = [
        "google-chrome", "google-chrome-stable", "google-chrome-unstable",
        "chromium", "chromium-browser",
        "microsoft-edge", "microsoft-edge-stable", "msedge",
        "brave-browser", "brave", "chrome"
    ]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p

    if sys.platform == "darwin":
        mac_candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Arc.app/Contents/MacOS/Arc",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
            "/Applications/Opera.app/Contents/MacOS/Opera",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            os.path.expanduser("~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            os.path.expanduser("~/Applications/Arc.app/Contents/MacOS/Arc"),
            os.path.expanduser("~/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        ]
        for p in mac_candidates:
            if os.path.exists(p):
                return p
    elif sys.platform == "win32":
        win_candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
        for p in win_candidates:
            if os.path.exists(p):
                return p
    elif sys.platform.startswith("linux"):
        linux_candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable",
            "/usr/bin/brave-browser",
        ]
        for p in linux_candidates:
            if os.path.exists(p):
                return p

    return None


def probe_height(html_path: str, width: int, probe_width_pad: int = 400, chrome_bin: str = "google-chrome") -> int:
    """用 Chrome --dump-dom 探测页面真实高度（读取 <html data-pageh>）。"""
    import re
    temp_dir = tempfile.mkdtemp(prefix="dushe_probe_")
    try:
        cmd = [
            chrome_bin,
            f"--user-data-dir={temp_dir}",
            "--headless", "--disable-gpu", "--no-sandbox",
            "--no-first-run", "--no-default-browser-check",
            "--hide-scrollbars", "--virtual-time-budget=6000",
            f"--window-size={width},{probe_width_pad}",
            "--dump-dom", f"file://{html_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, errors="ignore", timeout=30)
        m = re.findall(r'data-pageh="(\d+)"', r.stdout or "")
        if not m:
            return 0
        return max(int(x) for x in m) + 60  # 底部留白
    except Exception:
        return 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def shoot_playwright(html_path, w, h, target):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": w, "height": h or 2800}, device_scale_factor=2)
            page.goto(f"file://{html_path}")
            page.wait_for_timeout(1000)
            page.screenshot(path=target, full_page=True)
            browser.close()
            return os.path.exists(target)
    except Exception:
        return False

def main():
    ap = argparse.ArgumentParser(description="毒舌2BTI 渲染器 v3（16 型）")
    ap.add_argument("profile", nargs="?", default="", help="JSON 文件路径或 -（标准输入）")
    ap.add_argument("--json", "--data", dest="json_str", default="", help="直接传入 JSON 字符串")
    ap.add_argument("-o", "--out", default="2bti.html", help="HTML 输出路径")
    ap.add_argument("--png", nargs="?", const="2bti.png", default="2bti.png",
                    help="PNG 输出路径（默认 2bti.png）")
    ap.add_argument("--no-png", action="store_true", help="显式关闭 PNG 导出")
    ap.add_argument("--width", type=int, default=1240)
    ap.add_argument("--height", type=int, default=0, help="0=自动探测")
    ap.add_argument("--mobile", action="store_true", default=True, help="同时导出 750px 手机竖版（默认开启）")
    ap.add_argument("--no-mobile", action="store_false", dest="mobile", help="关闭手机竖版导出")
    ap.add_argument("--name", default="",
                    help="目标名；不传则依次读 DUSHE_NAME / USER / USERNAME / LOGNAME / HOSTNAME")
    a = ap.parse_args()

    if a.json_str:
        p = json.loads(a.json_str)
    elif a.profile == "-" or (not a.profile and not sys.stdin.isatty()):
        p = json.load(sys.stdin)
    elif a.profile:
        with open(a.profile, encoding="utf-8") as f:
            p = json.load(f)
    else:
        ap.error("请提供 profile.json 文件路径、标准输入或 --json 参数")

    subject = resolve_subject(a.name)
    # 若 JSON 未给 type_code，则按四轴规则自动判定
    dims = p.get("dimensions", {})
    auto_code = classify(dims) if dims else ""
    if not p.get("type_code") and auto_code:
        p["type_code"] = auto_code
    code = p.get("type_code", "BR-SL")
    if code in TYPE_NAMES:
        p.setdefault("type_name", TYPE_NAMES[code][0])
        p.setdefault("type_en", TYPE_NAMES[code][1])

    out = os.path.abspath(a.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(p, subject=subject))
    print(f"目标: {subject}  |  判定: {code} {TYPE_NAMES.get(code,('',''))[0]}")
    print(f"HTML -> {out}  ({os.path.getsize(out)//1024} KB)")

    if a.png and not a.no_png:
        chrome_bin = find_chrome()
        png = os.path.abspath(a.png)

        if not chrome_bin:
            # 尝试回退到 playwright
            pw_ok = shoot_playwright(out, a.width, a.height or 3200, png)
            if pw_ok:
                print(f"PNG (Playwright) -> {png}")
                if a.mobile:
                    mtarget = png.replace(".png", "_mobile.png")
                    shoot_playwright(out, 750, 3800, mtarget)
                    print(f"PNG Mobile -> {mtarget}")
                return
            print("⚠️ 未找到可用的 Chrome / Edge / Chromium 浏览器或 Playwright，跳过自动截图。")
            print(f"  ✅ 但 HTML 处决卡已生成: file://{out}")
            print("  💡 提示: 可直接在浏览器中打开该 HTML 查看或手动截图。")
            return

        png = os.path.abspath(a.png)

        def shoot(w, h, target):
            temp_dir = tempfile.mkdtemp(prefix="dushe_shoot_")
            try:
                cmd = [
                    chrome_bin,
                    f"--user-data-dir={temp_dir}",
                    "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-first-run", "--no-default-browser-check",
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--screenshot={target}", f"--window-size={w},{h}",
                    "--virtual-time-budget=9000", f"file://{out}",
                ]
                subprocess.run(cmd, capture_output=True, timeout=60)
                if os.path.exists(target):
                    print(f"PNG  -> {target}  ({os.path.getsize(target)//1024} KB)")
                    return True
                return False
            except Exception as e:
                print(f"截图异常: {e}")
                return False
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        h = a.height or probe_height(out, a.width, chrome_bin=chrome_bin)
        if not h:
            h = 3200
            print(f"高度探测失败，回退 {h}px")
        else:
            print(f"探测页面高度: {h}px")
        shoot(a.width, h, png)

        if a.mobile:
            mh = probe_height(out, 750, chrome_bin=chrome_bin) or 3800
            print(f"手机版高度: {mh}px")
            mtarget = png.replace(".png", "_mobile.png")
            shoot(750, mh, mtarget)


if __name__ == "__main__":
    main()
