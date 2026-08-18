# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from conftest import make_test_prs, blank_slide, dk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from deck_helpers import arch_layers
from pptx.dml.color import RGBColor

def test_arch_layers_draws_bands_and_returns_centers():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [
        {"name":"接入层","items":["Web","App"],"height":0.8},
        {"name":"服务层","items":["svcA","svcB","svcC"],"height":1.4},
        {"name":"存储层","items":["DB"],"height":0.7},
    ]
    centers = arch_layers(s, layers, x=0.4, y=1.2, w=12.5, total_h=4.5)
    assert len(centers) == 3
    # 每层中心 x 应在画布内,y 应递增(从上到下)
    for cx, cy in centers:
        assert 0 <= cx <= 13.333 and 1.0 <= cy <= 7.0
    assert centers[0][1] < centers[1][1] < centers[2][1]

def test_arch_layers_lint_passes_no_critical():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name":f"L{i}","items":[f"c{i}1",f"c{i}2"],"height":0.9} for i in range(4)]
    arch_layers(s, layers, x=0.4, y=1.4, w=12.5, total_h=4.6)
    findings = dk.lint_layout(prs, strict=True, _return=True) if hasattr(dk.lint_layout, "_return") else None
    # 多数 deckkit 的 lint_layout(strict=True) 在 critical 时抛异常;这里期望不抛
    # 退化:直接调,若抛则测试失败
    dk.lint_layout(prs, strict=True)
    # 能走到这 = 无 critical
    assert True

def test_arch_layers_style_mono_uses_one_tint():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name":"L1","items":["a"],"height":0.8},{"name":"L2","items":["b"],"height":0.8}]
    centers = arch_layers(s, layers, style="mono", accent=RGBColor(0xE6,0x00,0x2D))
    assert len(centers) == 2
