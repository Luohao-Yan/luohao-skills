#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deck_helpers.py — 在模板上构建 deck 的通用积木,颜色/字体从 profile 来(非硬编)。

build 脚本:
    import sys, os
    sys.path.insert(0, find_slide_maker())          # deckkit/anim 在这(自动探测)
    sys.path.insert(0, "<tech-gtm-training-deck>/scripts")
    import deckkit as dk
    from deck_helpers import Deck, set_title, num_circle, chap, card, para, notes

这些 helper 把"在用户模板上画一页"的重复动作封装好:填标题占位符并打 CJK 字体
tag、画模板语汇的渐变编号圆、画带半透明衬底的章节页(修深暖背景白字对比坑)、
画卡片、写讲者备注。颜色都从传入的 Profile 来,不硬编 hex。
"""
import os, sys
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import deckkit as dk

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GOLD_FALLBACK = RGBColor(0xFF, 0xC0, 0x00)

def bottom_callout_at(slide, x, w, bottom_y, label, body, **kw):
    """锚定到指定 bottom_y(向上长)的 callout,精确控制贴底位置——比 bottom_callout 的
    footer 锚更可控(后者受 FOOTER_BAND=0.5 限制,底到 6.85 留白偏大)。
    先量高度,再放 y=bottom_y-h。返回 top y(供上方内容避让)。
    用法: top = bottom_callout_at(s, 0.5, W-1.0, 7.07, "一句话", "...");
          上方内容 bottom 应 < top - 0.28(留 0.28in 视觉间距)。"""
    ch = dk.measure_callout(label, body, w)
    y = bottom_y - ch
    dk.callout(slide, x, y, w, ch, label, body, **kw)
    return y

class Deck:
    """持有 profile + deckkit 全局字体,build 脚本从这取颜色/字体/layout。"""
    def __init__(self, profile):
        self.P = profile
        latin, ea = profile.fonts()
        dk.FONT = latin; dk.EAFONT = ea; dk.DISPLAY = latin
        self.W, self.H = profile.canvas()
    # 语义色快捷(走 profile 的 semantic_contract)
    @property
    def anchor(self): return self.P.color("anchor_subject")
    @property
    def comparator(self): return self.P.color("comparator")
    @property
    def neutral(self): return self.P.color("neutral")
    @property
    def emphasis(self): return self.P.color("emphasis")

def set_title(slide, text, color, size=26, bold=True, font=None, ea=None):
    """填 idx=0 标题占位符 + 设字号/粗/色 + 打 CJK ea 字体 tag(kinsoku/渲染才正确)。
    每个内容页都要做;颜色由调用方从 profile 传(通常是 anchor 主色)。"""
    ph = slide.placeholders[0]
    ph.text = text
    latin, eaf = (font or dk.FONT), (ea or dk.EAFONT)
    for p in ph.text_frame.paragraphs:
        p.alignment = PP_ALIGN.LEFT
        for r in p.runs:
            r.font.size = Pt(size); r.font.bold = bold
            r.font.color.rgb = color; r.font.name = latin
            dk._apply_ea(r, eaf)
    return ph

def num_circle(slide, cx, cy, d, num, color_a, color_b, tcolor=WHITE, size=16, font=None):
    """渐变编号圆(模板语汇):color_a→color_b 径向渐变 + 白字居中。
    color_a/b 通常用 deck.anchor / deck.comparator。"""
    dk.box(slide, cx, cy, d, d, fill=None, round=True, r=d/2,
           grad=[(0.0, color_a, 1.0), (1.0, color_b, 1.0)], grad_radial=True)
    dk.text(slide, cx, cy, d, d, [[(str(num), size, tcolor, True, False, font or dk.FONT)]],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False)

def chap(prs, deck, layout_role, num, title, sub="", accent=None):
    """章节页:用模板的章节页占位符(标题 idx0 + 副标题 idx10),字号/位置/背景由版式保证。
    不自绘衬底——沿用模板设计语言(模板的占位符已在合适位置,背景图标题区是暗的,白字可读)。
    若某模板章节页白字确不可读,再说;默认信任模板设计。"""
    accent = accent or deck.anchor
    s = prs.slides.add_slide(prs.slide_layouts[deck.P.layout(layout_role)])
    # idx0 标题占位符:编号 + 标题
    ph = s.placeholders[0]
    ph.text = f"{num}  {title}"
    for p in ph.text_frame.paragraphs:
        for r in p.runs:
            r.font.bold = True; r.font.name = dk.FONT
            dk._apply_ea(r, dk.EAFONT)
    # idx10 副标题占位符(模板自带 24 号样式)
    if sub:
        try:
            ph2 = s.placeholders[10]; ph2.text = sub
            for p in ph2.text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = dk.EAFONT; dk._apply_ea(r, dk.EAFONT)
        except (KeyError, IndexError):
            pass
    return s

def card(slide, x, y, w, h, fill=None, line=None, line_w=1.5, r=0.12, corners='all'):
    """圆角卡片(dk.box 的语义别名,'card' 比 'box' 好读)。"""
    return dk.box(slide, x, y, w, h, fill=fill, line=line, line_w=line_w, round=True, corners=corners, r=r)

def para(txt, size=14, color=None, bold=False, font=None, ea=None):
    """run 元组工厂:(txt, size, color, bold, italic, font)。省记忆。"""
    return [(txt, size, color, bold, False, font or (ea or dk.EAFONT))]

def notes(slide, txt):
    """写讲者备注(讲稿)。不在幻灯片上渲染,只在演示视图显示。"""
    dk.speaker_notes(slide, txt)
