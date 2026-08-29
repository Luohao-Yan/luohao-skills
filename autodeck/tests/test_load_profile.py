# -*- coding: utf-8 -*-
"""load_profile.Profile 语义角色兜底测试。

修的坑:inspect_and_profile 生成的 profile.yaml 里 semantic_contract 是空 {},
build 第一页取 D.anchor(=P.color("anchor_subject"))会 KeyError——skill 的纲领是
"missing -> default, never error"(见 brief.py),Profile.color 应同样兜底,不崩。
"""
import os, sys
import pytest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from load_profile import Profile

# 一个最小 profile 数据,只有 accent1..6,无 semantic_contract(模拟 inspect 直出、人没填)
RAW_NO_SEM = {
    "canvas": {"w_in": 13.333, "h_in": 7.5},
    "colors": {
        "accent1": "#E6002D", "accent2": "#F76727", "accent3": "#3F5469",
        "accent4": "#FFC000", "accent5": "#074DB5", "accent6": "#05D8F6",
    },
    "fonts": {"latin": "Arial", "ea": "微软雅黑"},
    "layouts": {"content": 0, "dark": 2, "red_conclusion": 4, "chapter": 16, "blank": 8, "cover": 11},
    "semantic_contract": {},   # 空——这正是 inspect_and_profile 直出的状态
}


def test_color_semantic_role_with_empty_contract_falls_back():
    """空 semantic_contract 时,语义角色(anchor_subject)应回退到 accent1,而非 KeyError。
    这是 Bug2 的核心复现:agent 跑完 inspect 不填 semantic_contract 就 build,第一页 D.anchor 崩。"""
    P = Profile(RAW_NO_SEM, None)
    c = P.color("anchor_subject")        # 不应 raise
    assert c == (0xE6, 0x00, 0x2D)        # = accent1 #E6002D


def test_color_all_four_roles_fall_back_when_empty():
    """空契约时四个语义角色都该有兜底映射,全不崩。"""
    P = Profile(RAW_NO_SEM, None)
    assert P.color("anchor_subject") == (0xE6, 0x00, 0x2D)   # accent1
    assert P.color("comparator") == (0xF7, 0x67, 0x27)      # accent2
    assert P.color("neutral") == (0x3F, 0x54, 0x69)         # accent3
    assert P.color("emphasis") == (0xFF, 0xC0, 0x00)       # accent4


def test_color_explicit_contract_still_wins():
    """填了 semantic_contract 时,显式绑定优先于兜底(回归保护)。"""
    data = dict(RAW_NO_SEM)
    data["semantic_contract"] = {"anchor_subject": "accent4", "comparator": "accent1"}
    P = Profile(data, None)
    assert P.color("anchor_subject") == (0xFF, 0xC0, 0x00)   # = accent4(显式)
    assert P.color("comparator") == (0xE6, 0x00, 0x2D)      # = accent1(显式)
    # 没显式绑的 neutral/emphasis 仍走兜底
    assert P.color("neutral") == (0x3F, 0x54, 0x69)        # accent3 兜底
    assert P.color("emphasis") == (0xFF, 0xC0, 0x00)       # accent4 兜底


def test_color_raw_accent_name_still_works():
    """直接传 accent 名(accent1)取色不受影响(既有用法)。"""
    P = Profile(RAW_NO_SEM, None)
    assert P.color("accent1") == (0xE6, 0x00, 0x2D)
    assert P.color("accent2") == (0xF7, 0x67, 0x27)


def test_color_unknown_role_with_no_accent1_raises():
    """真正取不到色(既非已知角色、又无 accent1 兜底)仍要明确报错——兜底不是吞所有错误。"""
    data = dict(RAW_NO_SEM)
    data["colors"] = {"accent2": "#F76727"}   # 故意没 accent1,角色兜底也救不了
    P = Profile(data, None)
    with pytest.raises(KeyError):
        P.color("anchor_subject")   # anchor_subject -> accent1 兜底 -> 但 accent1 也没有 -> 仍 KeyError


def test_deck_anchor_runs_on_empty_contract():
    """端到端:空 semantic_contract 的 profile 能建 Deck 并取 anchor(模拟 build 第一页)。
    Bug2 的真实触发点就是 Deck(P).__init__ 后第一页 set_title(..., D.anchor)。"""
    from deck_helpers import Deck
    P = Profile(RAW_NO_SEM, None)
    D = Deck(P)
    assert D.anchor == (0xE6, 0x00, 0x2D)     # 不崩
    assert D.comparator == (0xF7, 0x67, 0x27)
