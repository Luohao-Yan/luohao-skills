# -*- coding: utf-8 -*-
"""共享测试夹具:注入 slide-maker 路径 + 造一个空 deckkit-friendly Presentation。"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SKILL_SCRIPTS)
from slide_maker_path import find_slide_maker
sys.path.insert(0, find_slide_maker())
import deckkit as dk  # noqa: E402
dk.EAFONT = "Microsoft YaHei"   # 裸测试无 profile,显式设 CJK 字体避免 CJK_NO_EA
from pptx import Presentation  # noqa: E402
from pptx.util import Inches  # noqa: E402

# 一个极简模板:13.333x7.5in, 一个 content layout(只标题占位符)
def make_test_prs():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def blank_slide(prs):
    """加一张空白页(无 layout 占位符干扰),helper 直接在自绘几何上画。"""
    return prs.slides.add_slide(prs.slide_layouts[6])  # 6 = blank

def make_section_prs():
    """带章节版式(idx0 TITLE + idx10 BODY)的 prs,测 chap 的 idx10 副标题占位符。

    默认模板 idx10 是 DATE(chrome,add_slide 不克隆到 slide);改成 BODY 后 add_slide
    会克隆 idx10 到 slide,使 chap 能 s.placeholders[10] 找到并删/填它。
    已实测:type dt→body 后 add_slide(layout5) slide 含 [0, 10]。
    """
    from pptx.oxml.ns import qn
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    lay = prs.slide_layouts[5]   # Title Only: idx0 TITLE + idx10 DATE + chrome
    for ph in lay.placeholders:
        if ph.placeholder_format.idx == 10:
            phel = ph._element.find(qn('p:nvSpPr')+'/'+qn('p:nvPr')+'/'+qn('p:ph'))
            phel.set('type', 'body'); phel.set('idx', '10')
            ph.text_frame.text = '可添加副标题或英文-20号'   # 版式层提示语
    return prs
