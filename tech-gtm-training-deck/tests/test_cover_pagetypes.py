# -*- coding: utf-8 -*-
"""cover / strip_branding / 页型 helper 冒烟测试。"""
import os, sys
import pytest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from deck_helpers import cover, strip_branding, quad_grid, steps3, code_card, text_right_card, Deck
from load_profile import Profile
import builtin_palettes as bp

class FakeDeck:
    """裸测试无 profile.yaml,用内置 palette 造 Deck。"""
    def __init__(self):
        P = Profile(bp.get("slate-business"), None)
        self.P = P
        self.W, self.H = P.canvas()
    @property
    def anchor(self): return self.P.color("anchor_subject")
    @property
    def comparator(self): return self.P.color("comparator")
    @property
    def neutral(self): return self.P.color("neutral")
    @property
    def emphasis(self): return self.P.color("emphasis")

D = FakeDeck()

def test_cover_band_makes_one_slide_no_logo():
    from conftest import make_test_prs
    prs = make_test_prs()
    s = cover(prs, D, subject="测试主题", subtitle="故事线", meta="团队 · 2026/08", style="band")
    assert len(prs.slides._sldIdLst) == 1
    # 封面应含主标题文字
    texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
    assert any("测试主题" in t for t in texts)

def test_cover_hero_style():
    from conftest import make_test_prs
    prs = make_test_prs()
    s = cover(prs, D, subject="H", subtitle="S", meta="M", style="hero")
    assert len(prs.slides._sldIdLst) == 1

def test_quad_grid_four_cards():
    from conftest import make_test_prs, blank_slide
    prs = make_test_prs()
    s = blank_slide(prs)
    rects = quad_grid(s, D, [{"tab":"a","head":"A","body":"aa"},{"tab":"b","head":"B","body":"bb"},
                             {"tab":"c","head":"C","body":"cc"},{"tab":"d","head":"D","body":"dd"}])
    assert len(rects) == 4

def test_steps3_three_cols():
    from conftest import make_test_prs, blank_slide
    prs = make_test_prs()
    s = blank_slide(prs)
    rects = steps3(s, D, [{"tag":"Step1","head":"a","body":"x"},{"tag":"Step2","head":"b","body":"y"},{"tag":"Step3","head":"c","body":"z"}])
    assert len(rects) == 3

def test_code_card_runs():
    from conftest import make_test_prs, blank_slide
    prs = make_test_prs()
    s = blank_slide(prs)
    code_card(s, D, left_title="原理", left_body="讲机制", code_title="示例", code_lines=["import x","x()"])
    assert len(prs.slides._sldIdLst) == 1

def test_text_right_card_runs():
    from conftest import make_test_prs, blank_slide
    prs = make_test_prs()
    s = blank_slide(prs)
    text_right_card(s, D, left_title="场景", left_body="诉求", right_title="方案", right_body="架构")
    assert len(prs.slides._sldIdLst) == 1

def test_strip_branding_noop_on_clean_prs():
    from conftest import make_test_prs
    prs = make_test_prs()
    r = strip_branding(prs)
    assert r == {"pics": 0, "texts": 0}   # 干净模板,无 logo 可删

def test_strip_branding_keep_logo_skips():
    from conftest import make_test_prs
    prs = make_test_prs()
    r = strip_branding(prs, keep_logo=True)
    assert r == {"pics": 0, "texts": 0}

def test_builtin_palettes_has_two():
    assert "slate-business" in bp.PALETTES
    assert "ink-data" in bp.PALETTES
    assert len(bp.list_palettes()) >= 2
