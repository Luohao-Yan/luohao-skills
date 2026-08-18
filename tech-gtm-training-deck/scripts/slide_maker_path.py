#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slide_maker_path.py — 探测 slide-maker skill 的 scripts 目录(放 deckkit/anim 的地方)。

纯函数,不 import deckkit,所以可在 import deckkit 之前安全调用。
slide-maker 可能装在多处:npx skills 装 → ~/.agents + 符号链接到 ~/.claude;
或直接 git clone 到 ~/.claude;或项目级 .claude/skills。自动探测,不硬编。

build 脚本用法:
    import sys, os
    HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(HERE, "<tech-gtm-training-deck>/scripts"))  # 本 skill 的 scripts
    from slide_maker_path import find_slide_maker
    sys.path.insert(0, find_slide_maker())   # slide-maker 的 scripts
    import deckkit as dk
    from anim import Build
"""
import os

def find_slide_maker():
    """返回 deckkit.py 所在的 scripts 目录;找不到则报错并给修复提示。"""
    home = os.path.expanduser("~")
    cands = [
        os.path.join(home, ".claude", "skills", "slide-maker", "scripts"),
        os.path.join(home, ".agents", "skills", "slide-maker", "scripts"),
        os.path.join(home, ".codex", "skills", "slide-maker", "scripts"),
    ]
    for c in cands:
        if os.path.isfile(os.path.join(c, "deckkit.py")):
            return c
    raise SystemExit(
        "找不到 slide-maker skill(本 skill 的 Stage 3 依赖它的 deckkit/anim)。\n"
        "  已查: " + " | ".join(cands) + "\n"
        "  修复: npx skills add addsumtech/slides_maker -g -y\n"
        "        (或 git clone https://github.com/addsumtech/slides_maker ~/.claude/skills/slide-maker/)\n"
        "  注:Stage 1-2(调研、写培训文档)不需要 slide-maker,可照常进行。"
    )
