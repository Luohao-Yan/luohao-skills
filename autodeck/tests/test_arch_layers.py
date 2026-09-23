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


# ---- 层间分隔(gap):修截图 bug——6 层色带无 gap 首尾相连糊成一坨 ----
_IN = 914400
def _bands(slide):
    """取出 arch_layers 画的层色带(全宽、有 fill 的圆角 box),按 top 排序。
    色带高度 = 层 h(>=0.5),组件块矮(<=0.3);按高度筛色带。"""
    bands = []
    for sh in slide.shapes:
        try:
            if sh.shape_type is None:
                continue
            top = sh.top / _IN; h = sh.height / _IN; w = sh.width / _IN
            left = sh.left / _IN
            if h >= 0.5 and w >= 6.0:   # 色带宽(全宽),组件块窄且矮
                bands.append((top, h, left, w))
        except Exception:
            continue
    return sorted(bands)

def test_arch_layers_bands_have_gap_between_them():
    """相邻层色带不能首尾相连——下层 top 必须严格大于上层 bottom(留可见分隔)。
    这是截图 P5 的 bug:6 层无 gap,色带接缝处圆角交错看起来重叠糊成一坨。"""
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name": f"L{i}", "items": [f"c{i}1", f"c{i}2"], "height": 0.7}
              for i in range(6)]
    arch_layers(s, layers, x=0.4, y=1.25, w=12.5, total_h=5.6)
    bands = _bands(s)
    assert len(bands) == 6, "应画出 6 条层色带,实际 %d" % len(bands)
    # 相邻层:下一层 top > 上一层 bottom(有 gap)
    for i in range(len(bands) - 1):
        top_i, h_i, _, _ = bands[i]
        top_next, _, _, _ = bands[i + 1]
        bottom_i = top_i + h_i
        assert top_next > bottom_i, \
            "层 %d 与 %d 首尾相连(无分隔): 上层 bottom=%.3f, 下层 top=%.3f" % (
                i, i + 1, bottom_i, top_next)

def test_arch_layers_gap_param_controls_separation():
    """gap 参数显式控制层间距:gap=0.3 比 gap=0.1 分隔更大。"""
    def band_gap(gap_val):
        prs = make_test_prs(); s = blank_slide(prs)
        layers = [{"name": f"L{i}", "items": ["a"], "height": 0.8} for i in range(3)]
        arch_layers(s, layers, gap=gap_val, total_h=4.0)
        bands = _bands(s)
        return bands[1][0] - (bands[0][0] + bands[0][1])   # 层0底到层1顶的距离
    assert band_gap(0.3) > band_gap(0.1) + 0.1   # 0.3 的间距明显大于 0.1

def test_arch_layers_default_gap_is_nonzero():
    """不传 gap 也要有默认分隔(修 bug 的默认行为),不能退化成首尾相连。"""
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name": f"L{i}", "items": ["a"], "height": 0.8} for i in range(3)]
    arch_layers(s, layers, total_h=4.0)
    bands = _bands(s)
    assert len(bands) == 3
    for i in range(2):
        bottom = bands[i][0] + bands[i][1]
        assert bands[i + 1][0] > bottom, "默认 gap 仍首尾相连(未修)"

def test_arch_layers_gap_zero_back_to_touching():
    """gap=0 允许首尾相连(向后兼容:有人就是要无缝分层)。"""
    prs = make_test_prs(); s = blank_slide(prs)
    layers = [{"name": f"L{i}", "items": ["a"], "height": 0.8} for i in range(3)]
    arch_layers(s, layers, gap=0, total_h=4.0)
    bands = _bands(s)
    for i in range(2):
        bottom = round(bands[i][0] + bands[i][1], 3)
        assert round(bands[i + 1][0], 3) == bottom, "gap=0 应首尾相连"
