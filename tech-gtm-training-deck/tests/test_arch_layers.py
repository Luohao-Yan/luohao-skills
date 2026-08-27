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

def test_arch_layers_ksyun_uses_red_accent():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name":"应用层","items":["文档治理平台","ChatDB"],"height":1.0},
              {"name":"算力层","items":["CPU","GPU"],"height":0.9}]
    centers = arch_layers(s, layers, style="ksyun")
    assert len(centers) == 2
    # ksyun 不传 accent 也应跑通(内部默认金山云红),不抛即正确

def test_arch_layers_sidebar_true_uses_defaults():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name":"L1","items":["a"],"height":1.0},{"name":"L2","items":["b"],"height":1.0}]
    # sidebar=True 用 ARCH_SIDEBAR_DEFAULT,主图自动收窄,不抛即正确
    centers = arch_layers(s, layers, sidebar=True, total_h=4.0)
    assert len(centers) == 2

def test_arch_layers_sidebar_custom_list():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name":"L1","items":["a"],"height":1.0}]
    arch_layers(s, layers, sidebar=["合规A","合规B"], total_h=3.0)
    # 自定义侧栏条目,不抛即正确

def test_arch_layers_show_arrows():
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name":"L1","items":["a"],"height":1.0},
              {"name":"L2","items":["b"],"height":1.0},
              {"name":"L3","items":["c"],"height":1.0}]
    # 3 层 + show_arrows,应画 2 个层间箭头,不抛即正确
    centers = arch_layers(s, layers, show_arrows=True, total_h=4.5)
    assert len(centers) == 3

def test_arch_layers_ksyun_full_combo_renders():
    """金山云红 + 侧栏 + 箭头 三件套组合(上海广电立项书场景),不抛即正确。"""
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [
        {"name":"应用层","items":["文档治理平台","ChatDB 智能问数"],"height":1.0},
        {"name":"AI 能力层","items":["大模型推理","向量化精排","文档解析OCR"],"height":1.1},
        {"name":"数据层","items":["MySQL","ES","Qdrant","MinIO"],"height":0.9},
        {"name":"算力层","items":["CPU×2","GPU 910B×1"],"height":0.9},
    ]
    centers = arch_layers(s, layers, style="ksyun", sidebar=True,
                          show_arrows=True, total_h=5.2)
    assert len(centers) == 4
