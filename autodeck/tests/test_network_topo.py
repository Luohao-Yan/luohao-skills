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
