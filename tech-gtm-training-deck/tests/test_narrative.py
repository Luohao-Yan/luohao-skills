# -*- coding: utf-8 -*-
"""叙事合同(narrative contract)测试:
验证 new_deck 脚手架按叙事弧页序产出(无「内容页N」裸编号页),每页 notes 强制带
【承上】【本页】【启下】;并验证 deck_helpers.beat() 把承接写进讲稿。
这些是让 deck 天生带上下承接(故事感)的结构保证。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from new_deck import build_scaffold  # noqa: E402


def _roles(code):
    return [ln for ln in code.splitlines() if "########" in ln and "封面" not in ln and "目录" not in ln]


def _page_count(code):
    # 只数「真页面」:排除 SKELETON 里的注释示例行(add_slide 前面带 #)
    return sum(1 for ln in code.splitlines()
               if ln.strip().startswith("s = prs.slides.add_slide"))


def test_scaffold_has_no_bare_content_page_numbering():
    code = build_scaffold("测试主题", 8)
    assert "内容页" not in code, "不应出现「内容页N」这种裸编号页"
    assert "内容页1" not in code and "内容页2" not in code


def test_scaffold_8_pages_has_narrative_roles():
    code = build_scaffold("测试主题", 8)
    # 固定页:封面/目录 + n_content=4 的内容角色槽 + 结论 + 附录
    for role in ["钩子·先纠偏", "关键发现", "定位·进入主题", "深入·机制/比喻", "结论·三段式收尾", "附录·证据出处"]:
        assert role in code, f"缺叙事角色页:{role}"


def test_scaffold_every_notes_opens_carry_beat_lead():
    code = build_scaffold("测试主题", 8)
    # 每页 PAGE_STUB 的 notes 都带【承上】【本页】【启下】三段
    assert code.count("【承上】") == _page_count(code), "每页都该有【承上】"
    assert code.count("【本页】") == _page_count(code)
    assert code.count("【启下】") == _page_count(code)


def test_scaffold_uses_dark_layout_for_key_finding():
    code = build_scaffold("测试主题", 8)
    # 关键发现(最能汇报的一条)用 dark 深色页,意见上应该是 highlight
    assert 'layout("dark")' in code


def test_scaffold_projects_content_slots_across_roles():
    # 页少时截断角色,页多时循坏复用,但永远从钩子开始
    code8 = build_scaffold("测试主题", 8)
    code12 = build_scaffold("测试主题", 12)
    assert "深入·机制/比喻" in code8
    assert _page_count(code8) == 8
    assert _page_count(code12) == 12


def test_beat_writes_carry_beat_lead_into_notes():
    from deck_helpers import beat

    frame = type("Frame", (), {"text": ""})()
    notes_slide = type("Notes", (), {"notes_text_frame": frame})
    fake = type("Fake", (), {"notes_slide": notes_slide})()

    beat(fake, "本页要点", carried_from="上一页结论", leads_to="下一页行动")
    text = frame.text
    assert "【承上】上一页结论" in text
    assert "【本页】本页要点" in text
    assert "【启下】下一页行动" in text
