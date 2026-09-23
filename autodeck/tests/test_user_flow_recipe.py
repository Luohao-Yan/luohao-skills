# -*- coding: utf-8 -*-
"""user-flow recipe 冒烟测试。

验证 diagram-types.md §user-flow-recipe 的拼装样板用的 deckkit 原语能跑通、
符号正确(diamond=决策/roundrect=起止/cylinder=数据存)、连线(elbow_connector+loop_path)
不抛、泳道(box+text)画出、lint 无 critical。这是回归保护:锁住 recipe 用的原语组合,
防 deckkit 升级改 shape 映射或 recipe 用错原语时静默退化。

本测试不驱动新代码(原语 deckkit 早有),而是锁住「recipe 真能拼出 user flow」这个事实。
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from conftest import make_test_prs, blank_slide, dk
from pptx.dml.color import RGBColor

ANCHOR = RGBColor(0xC6, 0x00, 0x00)   # 深红 disc
MUTE = RGBColor(0x80, 0x80, 0x80)

def _autoshapes(slide):
    """返回 slide 上所有 auto_shape_type 的字符串集合(用于断形状种类)。"""
    out = []
    for sh in slide.shapes:
        try:
            if sh.auto_shape_type is not None:
                out.append(str(sh.auto_shape_type))
        except Exception:
            pass
    return out

def test_decision_node_uses_diamond_shape():
    """决策点用 node(shape='diamond') -> 生成 DIAMOND auto shape。"""
    prs = make_test_prs(); s = blank_slide(prs)
    dk.node(s, 1.0, 1.0, 1.6, 0.6, "state 校验?", shape="diamond", accent=ANCHOR)
    assert any("DIAMOND" in t for t in _autoshapes(s)), "决策节点应是 DIAMOND"

def test_start_end_uses_roundrect_shape():
    """起止用 node(shape='roundrect') -> 生成 ROUNDED_RECTANGLE(deckkit 标准 crib 用圆角矩形作起止,非圆)。"""
    prs = make_test_prs(); s = blank_slide(prs)
    dk.node(s, 1.0, 1.0, 1.6, 0.45, "开始", shape="roundrect", accent=ANCHOR)
    assert any("ROUND" in t for t in _autoshapes(s)), "起止应是 ROUNDED_RECTANGLE"

def test_action_node_uses_rect_shape():
    """动作用 node(shape='rect') -> 生成 RECTANGLE。"""
    prs = make_test_prs(); s = blank_slide(prs)
    dk.node(s, 1.0, 1.0, 1.8, 0.45, "跳 UIAP 授权", shape="rect", accent=ANCHOR)
    assert any(t == "RECTANGLE (1)" or t == "RECTANGLE" for t in _autoshapes(s)), \
        "动作节点应是 RECTANGLE,实际 %s" % _autoshapes(s)

def test_data_store_uses_cylinder_shape():
    """数据存储用 node(shape='cylinder') -> 生成 CAN(圆柱)。"""
    prs = make_test_prs(); s = blank_slide(prs)
    dk.node(s, 1.0, 1.0, 1.6, 0.5, "Redis 8h", shape="cylinder", accent=ANCHOR)
    assert any("CAN" in t for t in _autoshapes(s)), "数据存储应是 CAN(圆柱)"

def test_elbow_connector_with_loop_path_does_not_raise():
    """失败分支回流用 elbow_connector(loop_path(...)) -> 不抛。这是 recipe 的回流路径。"""
    prs = make_test_prs(); s = blank_slide(prs)
    pts = dk.loop_path(8.6, 4.0, 1.8, 2.8)   # U 形回环 waypoints
    dk.elbow_connector(s, pts, style="dashed", color=RGBColor(0xC0, 0x40, 0x2A))
    assert True   # 走到这 = 不抛

def test_connect_boxes_main_spine_does_not_raise():
    """主线 spine 用 connect_boxes(node rect, node rect) -> 不抛(edge-docked 安全连线)。"""
    prs = make_test_prs(); s = blank_slide(prs)
    dk.connect_boxes(s, (1.0, 1.0, 1.6, 0.45), (4.0, 1.0, 1.8, 0.45), color=ANCHOR)
    assert True

def test_swimlane_box_and_label_drawn():
    """泳道手搓:box(浅底+细边框) 区域 + text 标题 -> 都画出。deckkit 无泳道原语,这是手搓法。"""
    prs = make_test_prs(); s = blank_slide(prs)
    dk.box(s, 0.5, 1.3, 12.3, 1.7, fill=RGBColor(0xF5, 0xF6, 0xF8),
          round=True, line=RGBColor(0xCC, 0xCC, 0xCC), line_w=0.8, r=0.04)
    dk.text(s, 0.62, 1.34, 1.4, 0.3, [[("前端", 12, MUTE, True, False, dk.EAFONT)]], wrap=False)
    has_box = any(str(sh.shape_type) == "AUTO_SHAPE (1)" for sh in s.shapes)
    has_text = any(sh.has_text_frame and "前端" in sh.text_frame.text for sh in s.shapes)
    assert has_box and has_text, "泳道应画出 box 区域 + text 标题"

def test_full_user_flow_recipe_lints_clean():
    """端到端:照 recipe 拼一个完整 user flow(泳道+起止+动作+决策+数据存+主线+回流),
    lint_layout(strict=True) 无 critical。这是 recipe 整体可用的硬验证。"""
    prs = make_test_prs(); s = blank_slide(prs)
    # 泳道(最底层背景):fill=None 只靠边框区分——deckkit lint 把有 fill 的 AUTO_SHAPE 当 block
    # (containers_z),连线端点落泳道中央区会触发 CONNECTOR_IN_BOX。泳道不 fill 则不进 containers,
    # 端点不报。视觉靠细边框 + 标题区分。
    for i, name in enumerate(["前端", "后端", "Redis"]):
        ly = 1.3 + i * 1.6
        dk.box(s, 0.5, ly, 12.3, 1.6, fill=None,
              round=True, line=RGBColor(0xCC, 0xCC, 0xCC), line_w=0.8, r=0.04)
        dk.text(s, 0.62, ly + 0.04, 1.4, 0.3,
                [[(name, 12, MUTE, True, False, dk.EAFONT)]], wrap=False)
    # 节点 rect(记坐标)
    start = (1.2, 1.45, 1.5, 0.4)
    act = (3.4, 1.45, 1.8, 0.4)
    dec = (6.0, 2.95, 1.5, 0.7)
    store = (9.0, 4.5, 1.5, 0.5)
    reject = (3.4, 4.5, 1.8, 0.4)
    # Z-ORDER: 泳道 -> 连线 -> 节点(node 盖住端点 seam,CONNECTOR_IN_BOX 不报)
    dk.connect_boxes(s, start, act, color=ANCHOR)
    dk.connect_boxes(s, act, dec, color=ANCHOR)
    dk.connect_boxes(s, dec, store, color=ANCHOR, label="通过")
    dk.connect_boxes(s, dec, reject, color=RGBColor(0xC0, 0x40, 0x2A),
                     style="dashed", label="失败")
    dk.node(s, *start, "登录", shape="roundrect", accent=ANCHOR)
    dk.node(s, *act, "跳 UIAP", shape="rect", accent=ANCHOR)
    dk.node(s, *dec, "state 校验?", shape="diamond", accent=ANCHOR)
    dk.node(s, *store, "Redis 8h", shape="cylinder", accent=ANCHOR)
    dk.node(s, *reject, "CSRF 拒绝", shape="roundrect", accent=RGBColor(0xC0, 0x40, 0x2A))
    dk.lint_layout(prs, strict=True)   # 无 critical = 走到这
    assert True
