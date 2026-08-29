#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""new_deck.py — 给定 profile.yaml + 页数大纲,生成一个 build 脚手架脚本是 Stage 3 的起点:同事跑完 inspect_and_profile 拿到 profile.yaml 后,
用它生成一个可编辑的 build_<topic>.py(已配好:deckkit import、profile 加载、
deck_helpers、叙事弧页序的占位结构、lint 门禁、save)。
同事只需把每页的占位文字换成自己的内容。

叙事合同:生成的占位页不再叫「内容页N」,而是固定的叙事角色页序
(封面→目录→钩子·纠偏→关键发现→定位→深入·机制→战略→追问→应对→结论→附录),
且每页 notes 强制含【承上】【本页】【启下】三段,让从脚手架填出来的 deck 天生带承接。
storyline 的角色槽位与 --pages 语义:内容页在 6 个叙事槽(hook/na_insight/position/deep/
strategy/追问/应对)之间铺排,超出部分均匀分配到各内容槽。

用法:
    python new_deck.py --profile profile.yaml --topic "我的技术主题" --pages 8 \\
        --out build_my-topic.py
    python build_my-topic.py    # 生成 deck;需先有用户 .pptx 模板路径
"""
import argparse, os, textwrap
import pathguard

SKELETON = '''# -*- coding: utf-8 -*-
"""build_{slug}.py — {topic}(给领导培训 deck)
模板分支:从 profile.yaml 读品牌色/字体,不硬编。
Source of truth for the deck; re-run to rebuild identically.
依赖 slide-maker skill 的 deckkit/anim(import 路径见下)。
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
# === 改成你机器上 tech-gtm-training-deck skill 的 scripts 目录 ===
# (装了本 skill后,通常是 ~/.claude/skills/tech-gtm-training-deck/scripts 或 ~/.agents/skills/tech-gtm-training-deck/scripts)
SKILL_SCRIPTS = r"<改成 tech-gtm-training-deck skill 的 scripts 目录>"
sys.path.insert(0, SKILL_SCRIPTS)
from slide_maker_path import find_slide_maker
sys.path.insert(0, find_slide_maker())   # slide-maker 的 scripts(deckkit/anim,自动探测)
import deckkit as dk
from anim import Build
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from load_profile import load
from deck_helpers import Deck, set_title, num_circle, chap, card, para, notes, arch_layers, network_topo, check_template_placeholders

# --- 路径:你的模板与输出 ---
TPL = r"<改为你自己的.pptx模板路径>"
OUT = os.path.join(HERE, "{slug}.pptx")

P = load(os.path.join(HERE, "profile.yaml"))
D = Deck(P)          # 设好 deckkit 全局字体 + 语义色快捷

def build():
    prs = dk.open_template(TPL)
    # TODO: 按 --pages 大纲逐页实现。每页节奏:
    #   s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")])
    #   set_title(s, "断言式标题", D.anchor)
    #   cols = dk.columns(n, slide=s, top=1.4, bottom=0.95, margin=0.5, gap=0.3)
    #   for ...: card(...); dk.text(...); num_circle(...)
    #   notes(s, "讲者话术...")
    # 详见 examples/deepseek-harness/build.py 的完整范例。
{PAGE_STUBS}
    dk.lint_layout(prs, strict=True)
    check_template_placeholders(prs)   # 闸门:空占位符渲染版式提示语→硬失败(勿用 .text='' 清占位符)
    prs.save(OUT)
    print("saved:", OUT, "slides:", len(prs.slides._sldIdLst))

if __name__ == "__main__":
    build()
'''

PAGE_STUB = '''
    # -------- {n}. {label} ({role_tag}) --------
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("{role}")])
    set_title(s, "{title}", D.anchor)   # 断言式标题(一句话),别写"第N页"
    notes(s, "{title} \\n\\n"
             "【承上】{carried_from} \\n"
             "【本页】{beat} \\n"
             "【启下】{leads_to} \\n"
             "把详细内容放这里,幻灯片只留短语。")
'''

def slugify(t):
    import re
    return re.sub(r"[^a-z0-9_-]+", "-", t.lower()).strip("-") or "deck"

def build_scaffold(topic, pages=8):
    """生成叙事弧版 build 脚手架源码(纯字符串,不写盘)。给 main() 与测试复用。"""
    slug = slugify(topic)
    # 叙事弧页序(storyline 的固定角色槽位,与 deck-reference-layout.md 的叙事弧一致)。
    # 每页除了标题占位,还预填【承上】【本页】【启下】三段讲者话术骨架,让 deck 天生带承接。
    # 固定页:封面(1)、目录(2)、结论(倒数第2)、附录(最后1页)。
    n_content = max(1, pages - 4)          # 可自由铺排的内容槽数
    arc = [
        # label,             title占位,             role,     role_tag
        ("钩子·先纠偏",       "先放下一个常见误解",    "content", "hook"),
        ("关键发现",          "最能汇报的一条发现",    "dark",    "highlight"),
        ("定位·进入主题",     "这个概念用一句话说清",  "content", "position"),
        ("深入·机制/比喻",    "它到底怎么运作(signature move 峰值)", "content", "deep"),
        ("战略·我们能做什么", "对我们的价值/取舍",    "content", "strategy"),
        ("追问·存疑",         "先把异议摆上台面",      "content", "question"),
        ("应对·落地路径",     "下一步具体怎么做",      "content", "action"),
        ("总结·回顾主线",     "回到最初那个承诺",      "content", "wrap"),
    ]
    stubs = []
    stubs.append(PAGE_STUB.format(
        n=1, label="封面", role="cover", role_tag="storyline: 断言+故事线",
        title="<封面副标题/purpose 的故事线>",
        carried_from="(开场)抛出一个领导者会在意的判断",
        beat="用一句话立住整份 deck 的主张",
        leads_to="用目录把「领导关心的 N 问」摊开",
    ))
    stubs.append(PAGE_STUB.format(
        n=2, label="目录", role="content", role_tag="agenda",
        title="今天要回答的领导关心的 N 问",
        carried_from="承接封面承诺的 statement",
        beat="把叙事弧压缩成 3~5 个问题",
        leads_to="进入第 1 个误区/纠偏",
    ))
    # 内容槽:动态铺排到 8 个叙事角色槽位(页数多于角色数则循环复用末尾角色,少于则截断)。
    # 绝不出现「内容页N」这种裸编号页。
    order = []
    for i in range(n_content):
        if i < len(arc):
            order.append(arc[i])
        else:
            order.append(arc[i % len(arc)])
    for i, (label, tpl, role, role_tag) in enumerate(order):
        stubs.append(PAGE_STUB.format(
            n=3 + i, label=label, role=role, role_tag=f"role={role_tag}",
            title=tpl,
            carried_from="承上一页:" + ("<上一页讲了什么,一句话>" if i else "封面承诺"),
            beat="本页讲:" + label + "的核心论断",
            leads_to="引出下一页:" + (order[i + 1][0] if i + 1 < len(order) else "结论"),
        ))
    conc_idx = 3 + len(order)
    app_idx = conc_idx + 1
    stubs.append(PAGE_STUB.format(
        n=conc_idx, label="结论·三段式收尾", role="red_conclusion", role_tag="close",
        title="回到最初那句话:主张 + 证据 + 行动",
        carried_from=f"承接上一页(第 {conc_idx-1} 页)",
        beat="三段式:重申主张 → 给最硬证据 → 落到一个行动",
        leads_to="(结束)附录是证据出处,听众可自行核验",
    ))
    stubs.append(PAGE_STUB.format(
        n=app_idx, label="附录·证据出处", role="content", role_tag="appendix",
        title="证据出处/延伸阅读",
        carried_from=f"承接上一页结论(第 {conc_idx} 页)",
        beat="列数据/引用/出处,不含新论点",
        leads_to="(无,收尾)",
    ))
    return SKELETON.format(slug=slug, topic=topic, PAGE_STUBS="".join(stubs))

def main():
    ap = argparse.ArgumentParser(description="生成 build 脚手架")
    ap.add_argument("--profile", default="profile.yaml")
    ap.add_argument("--topic", required=True, help="主题名(中文OK)")
    ap.add_argument("--pages", type=int, default=8, help="页数(含封面/目录/附录)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or f"build_{slugify(args.topic)}.py"
    code = build_scaffold(args.topic, args.pages)
    pathguard.write_guarded(out, code)   # CWE-22:护栏内写盘,拒绝 ../ 越界
    print(f"-> {out}")
    print("next: 改 TPL 路径为你的 .pptx,逐页填内容,然后 python {out}".replace("{out}", out))

if __name__ == "__main__":
    main()
