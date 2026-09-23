# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from conftest import make_test_prs, blank_slide, dk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from deck_helpers import network_topo
from pptx.dml.color import RGBColor

def test_network_topo_draws_nodes_and_links():
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [
        {"id":"internet","kind":"cloud","x":0.5,"y":0.1,"label":"Internet"},
        {"id":"fw","kind":"firewall","x":0.5,"y":0.4,"label":"防火墙"},
        {"id":"sw","kind":"switch","x":0.5,"y":0.65,"label":"核心交换机"},
        {"id":"srv1","kind":"server","x":0.2,"y":0.9,"label":"应用服务器"},
        {"id":"srv2","kind":"server","x":0.8,"y":0.9,"label":"DB 服务器"},
    ]
    links = [
        {"from":"internet","to":"fw","label":"专线"},
        {"from":"fw","to":"sw"},
        {"from":"sw","to":"srv1","label":"千兆"},
        {"from":"sw","to":"srv2","label":"千兆"},
    ]
    network_topo(s, nodes, links, accent=RGBColor(0x3F,0x54,0x69))
    # 不抛 + lint 无 critical
    dk.lint_layout(prs, strict=True)
    assert True

def test_network_topo_works_without_icons_degrades_to_shapes():
    """图标缺失(占位场景)时降级为形状节点,仍能跑、无 CONNECTOR_IN_BOX。"""
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [{"id":"a","kind":"nonexistent","x":0.3,"y":0.3,"label":"A"},
             {"id":"b","kind":"server","x":0.7,"y":0.6,"label":"B"}]
    links = [{"from":"a","to":"b"}]
    network_topo(s, nodes, links)   # 不传图标目录->用默认;nonexistent 图标缺失应降级
    dk.lint_layout(prs, strict=True)
    assert True

def test_network_topo_relative_coords_map_into_bounds():
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [{"id":"a","kind":"server","x":0.0,"y":0.0,"label":"A"},
             {"id":"b","kind":"server","x":1.0,"y":1.0,"label":"B"}]
    network_topo(s, nodes, [{"from":"a","to":"b"}], x=0.5, y=1.4, w=12.3, h=5.3)
    dk.lint_layout(prs, strict=True)
    assert True


# ---- Bug 修复:连线被大节点框盖住 + 图标颜色不对比 ----
_IN = 914400
def _shape_types(slide):
    from collections import Counter
    return Counter(str(sh.shape_type) for sh in slide.shapes)

def _pics(slide):
    """返回 [(filename, top, left, w, h)] for picture shapes."""
    out = []
    for sh in slide.shapes:
        if str(sh.shape_type) == "PICTURE (13)":
            try:
                fn = sh.image.filename if hasattr(sh.image,'filename') else sh.image.blobname
            except Exception:
                fn = ""
            out.append((os.path.basename(fn or ""), sh.top/_IN, sh.left/_IN,
                        sh.width/_IN, sh.height/_IN))
    return out

def test_network_topo_links_drawn_as_lines_not_zero():
    """Bug2:连线不能消失。6 条 link 应画出 6 条 LINE shape(不是被盖成 0)。
    复现 P7 主干 4 节点垂直紧排(y 间距小)场景——之前大节点框重叠把线盖死。"""
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [{"id":f"n{i}","kind":"server","x":0.5,"y":0.02+i*0.20,"label":f"N{i}"}
             for i in range(4)]
    links = [{"from":f"n{i}","to":f"n{i+1}"} for i in range(3)]
    network_topo(s, nodes, links, x=0.5, y=1.3, w=8.5, h=5.5)
    types = _shape_types(s)
    n_line = types.get("LINE (9)", 0)
    assert n_line >= 3, "3 条连线应画出 >=3 条 LINE,实际 %d" % n_line

def test_network_topo_link_connects_disc_edges_not_giant_rect():
    """Bug2 真根因:network_topo 之前用 nw=1.1/nh=1.0 大概念框算连线端点,但只画 0.5 disc,
    连线连到「不存在的大框」边→端点落进相邻 disc 区被盖、线段极短(h≈0.1)。
    修后连线应连到 disc 真实 rect(0.5×0.5)边:相邻 disc 间距 0.90-0.50=0.40,连线长度应 >=0.30。"""
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [{"id":f"n{i}","kind":"server","x":0.5,"y":0.02+i*0.20,"label":f"N{i}"}
             for i in range(4)]
    network_topo(s, nodes, [{"from":f"n{i}","to":f"n{i+1}"} for i in range(3)],
                 x=0.5, y=1.3, w=8.5, h=5.5, accent=RGBColor(0xC6,0x00,0x00))
    # 取竖向连线(L 在主干列、高度>宽度的 LINE),断其长度 >= 0.30
    lines = [(sh.width/_IN, sh.height/_IN) for sh in s.shapes
             if str(sh.shape_type) == "LINE (9)"]
    vert = [h for w, h in lines if h > w]   # 竖线
    assert vert, "应有竖向连线"
    assert max(vert) >= 0.30, "连线连到 disc 边应 >=0.30 长,实际最大 %.2f(连到大框被盖)" % max(vert)

def test_network_topo_dark_disc_uses_white_icon():
    """Bug1:深色 disc 底应用白色图标(对比强)。accent 深红 -> 图标文件名含 _white。"""
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [{"id":"a","kind":"cloud","x":0.3,"y":0.3,"label":"A"},
             {"id":"b","kind":"server","x":0.7,"y":0.6,"label":"B"}]
    network_topo(s, nodes, [{"from":"a","to":"b"}],
                 accent=RGBColor(0xC6,0x00,0x00))   # 深红 disc
    pics = _pics(s)
    white_used = any("_white" in fn for fn, *_ in pics)
    assert white_used, "深红 disc 应使用白色图标(_white.png),实际 pics: %s" % [p[0] for p in pics]

def test_network_topo_light_disc_uses_dark_icon():
    """Bug1:浅色 disc 底应用深色图标(原版)。accent 浅色 -> 图标文件名不含 _white。"""
    prs = make_test_prs(); s = blank_slide(prs)
    nodes = [{"id":"a","kind":"cloud","x":0.3,"y":0.3,"label":"A"},
             {"id":"b","kind":"server","x":0.7,"y":0.6,"label":"B"}]
    network_topo(s, nodes, [{"from":"a","to":"b"}],
                 accent=RGBColor(0xFF,0xFF,0xFF))   # 白色 disc(浅)
    pics = _pics(s)
    dark_used = any("_white" not in fn and fn for fn, *_ in pics)
    assert dark_used, "白色 disc 应使用深色图标(原版),实际 pics: %s" % [p[0] for p in pics]

def test_network_topo_labels_present():
    """重构后标签仍要画(disc 下方独立 textbox)。"""
    prs = make_test_prs(); s = blank_slide(prs)
    network_topo(s, [{"id":"a","kind":"server","x":0.3,"y":0.3,"label":"我的标签"}],
                 [{"from":"a","to":"a"}] if False else [], x=0.5, y=1.4, w=8, h=5)
    texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
    assert any("我的标签" in t for t in texts), "标签丢失"

def test_icon_for_disc_picks_white_for_dark_disc():
    """函数层锁死选色:深 disc -> _white.png,浅 disc -> 原 .png。不依赖 deckkit part 命名。"""
    from deck_helpers import _icon_for_disc, _luminance
    dark = RGBColor(0xC6,0x00,0x00)     # 金山红,亮度 ~0.23
    light = RGBColor(0xFF,0xFF,0xFF)
    mid_dark = RGBColor(0x3F,0x54,0x69) # 深藏青,亮度 ~0.36
    assert _luminance(dark) < 0.5 and _luminance(mid_dark) < 0.5
    assert _luminance(light) > 0.5
    for kind in ["cloud","server","database","firewall"]:
        assert "_white" in os.path.basename(_icon_for_disc(kind, dark)), kind
        assert "_white" in os.path.basename(_icon_for_disc(kind, mid_dark)), kind
        assert "_white" not in os.path.basename(_icon_for_disc(kind, light)), kind
