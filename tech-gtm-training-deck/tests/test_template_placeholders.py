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


def test_cover_from_template_strips_title():
    """用模板封面版式加页 + drop_title=True → idx0 标题占位符被删,不再残留提示。"""
    from deck_helpers import cover_from_template

    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
            # cover_from_template 调 deck.P.layout(role)(非 deck.layout),须覆盖 Profile 的
            # 测试用默认模板 layout 5(Title Only)顶替封面版式;只要它带 idx0 标题占位符即可
            self.P.layout = lambda role: 5
    prs = make_test_prs()
    s = cover_from_template(prs, FakeDeck(), "cover", drop_title=True)
    # idx0 占位符应已被删
    idxs = [ph.placeholder_format.idx for ph in s.placeholders]
    assert 0 not in idxs
    # 闸门对这页不报(占位符已删)
    check_template_placeholders(prs)  # 不 raise


def test_cover_from_template_drop_all():
    """drop_all=True → 该版式所有占位符被删。"""
    from deck_helpers import cover_from_template
    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
            # cover_from_template 调 deck.P.layout(role);覆盖 Profile 的,用 layout 1(多占位符)
            self.P.layout = lambda role: 1
    prs = make_test_prs()
    s = cover_from_template(prs, FakeDeck(), "cover", drop_all=True)
    assert len(list(s.placeholders)) == 0


def test_chap_no_sub_drops_idx10():
    """chap() 不传 sub → idx10 副标题占位符被删(而非留空渲染版式提示)。"""
    from deck_helpers import chap
    from conftest import make_section_prs

    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
            # chap 调 deck.P.layout(role)(非 deck.layout),须覆盖 Profile 的
            # 用 make_section_prs 改造过的 layout 5(idx0 TITLE + idx10 BODY)
            self.P.layout = lambda role: 5
        @property
        def anchor(self): return self.P.color("anchor_subject")

    prs = make_section_prs()
    s = chap(prs, FakeDeck(), "section", num="01", title="章节标题")  # 不传 sub
    idxs = [ph.placeholder_format.idx for ph in s.placeholders]
    assert 10 not in idxs        # idx10 被删(而非留空)
    check_template_placeholders(prs)   # 闸门不报(标题已填,idx10 已删)


def test_chap_with_sub_fills_idx10():
    """chap() 传 sub → idx10 被填充(非删除)。闸门不报。"""
    from deck_helpers import chap
    from conftest import make_section_prs

    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
            # chap 调 deck.P.layout(role);覆盖 Profile 的,用 make_section_prs 改造过的 layout 5
            self.P.layout = lambda role: 5
        @property
        def anchor(self): return self.P.color("anchor_subject")

    prs = make_section_prs()
    s = chap(prs, FakeDeck(), "section", num="02", title="章节", sub="副标题")
    idxs = [ph.placeholder_format.idx for ph in s.placeholders]
    assert 10 in idxs            # idx10 仍在(被填,非删)
    assert "副标题" in s.placeholders[10].text_frame.text
    check_template_placeholders(prs)   # 闸门不报
