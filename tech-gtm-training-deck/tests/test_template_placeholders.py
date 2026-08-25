# -*- coding: utf-8 -*-
"""check_template_placeholders / cover_from_template / chap 占位符残留闸门测试。"""
import os, sys
import pytest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
sys.path.insert(0, HERE)
from deck_helpers import check_template_placeholders
from conftest import make_test_prs, blank_slide


def test_flags_cleared_title_placeholder():
    """清空 idx0 标题占位符(像 LoopEngineering build.py 那样)→ 闸门报该 finding 并 raise。"""
    prs = make_test_prs()
    # layout 5 = Title Only, idx0 TITLE prompt='Click to edit Master title style'
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.placeholders[0].text = ""   # 清空未删 —— 残留根因
    findings = check_template_placeholders(prs, fail_on_prompt=False)
    assert len(findings) == 1
    assert findings[0]["slide"] == 1
    assert findings[0]["idx"] == 0
    assert "Master title" in findings[0]["layout_prompt"]


def test_cleared_placeholder_raises_when_fail_on():
    """fail_on_prompt=True(默认)时,清空占位符 → raise RuntimeError。"""
    prs = make_test_prs()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.placeholders[0].text = ""
    with pytest.raises(RuntimeError):
        check_template_placeholders(prs)


def test_filled_placeholder_passes():
    """填充占位符 → 无 finding 不 raise。"""
    prs = make_test_prs()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.placeholders[0].text = "真标题"
    assert check_template_placeholders(prs) == []


def test_dropped_placeholder_passes():
    """删除占位符元素 → 无 finding 不 raise。"""
    prs = make_test_prs()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    ph = s.placeholders[0]
    ph._element.getparent().remove(ph._element)
    assert check_template_placeholders(prs) == []
