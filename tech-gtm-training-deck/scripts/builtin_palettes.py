# -*- coding: utf-8 -*-
"""builtin_palettes.py — 无品牌内置配色方案(template=none / builtin:<名> 时用)。

当用户不想用任何 .pptx 模板(要无 logo、无品牌、换个配色)时,Stage 3 不 inspect
.pptx,而用这里的配色直接造一份 profile 数据(等价 profile.yaml 的内容),
load_profile.Profile 可直接吃。slide-maker 从零设计封面/内页,颜色用这套 palette。

每套 palette 定义:
  canvas        画布(默认 13.333x7.5)
  colors        accent1..6 的 hex(无品牌通用设计色,非某企业色)
  fonts         latin/ea
  semantic_contract  把 accent 绑到语义角色(anchor_subject/comparator/neutral/emphasis)
  layouts       无模板时的默认 layout idx 映射(slide-maker 从零设计用 blank=0 起手)

配色取自 deck-reference-layout.md「配色语义契约」给的通用选色指引,非硬编某企业。
"""
from pptx.enum.shapes import MSO_SHAPE_TYPE  # noqa (仅供类型提示,运行不需要)

# 两套无品牌配色(藏青商务 / 深墨数据)。加新配色:在这字典里加一项即可。
PALETTES = {
    "slate-business": {
        "label": "藏青商务(无品牌)",
        "canvas": {"w_in": 13.333, "h_in": 7.5},
        "colors": {
            "accent1": "#1F3A5F",   # 深藏青 = 主锚
            "accent2": "#C97A2B",   # 暖琥珀 = 对比
            "accent3": "#33415C",   # 深石板 = 中性
            "accent4": "#E8B84B",   # 金 = 强调
            "accent5": "#4A6FA5",
            "accent6": "#9DB4D4",
            "dk1": "#1A1A2E", "dk2": "#16213E", "lt2": "#E5E9F0",
        },
        "fonts": {"latin": "Arial", "ea": "微软雅黑"},
        "semantic_contract": {
            "anchor_subject": "accent1",   # 深藏青 = 主主题/核心结论
            "comparator": "accent2",       # 琥珀 = 备选/对比
            "neutral": "accent3",           # 深石板 = 表头/结构线
            "emphasis": "accent4",          # 金 = 关键发现/take-away
        },
        "layouts": {  # 无模板:slide-maker 从零设计,用 blank 起手
            "content": 0, "dark": 0, "red_conclusion": 0, "blank": 0, "cover": 0, "chapter": 0,
        },
    },
    "ink-data": {
        "label": "深墨数据(无品牌)",
        "canvas": {"w_in": 13.333, "h_in": 7.5},
        "colors": {
            "accent1": "#0F2A44",   # 深墨蓝 = 主锚
            "accent2": "#2EC4B6",   # 青 = 对比
            "accent3": "#3A4A5A",   # 蓝灰 = 中性
            "accent4": "#F4A259",   # 橙 = 强调
            "accent5": "#843B62",
            "accent6": "#5B8FB9",
            "dk1": "#0B132B", "dk2": "#1C2541", "lt2": "#E0E6ED",
        },
        "fonts": {"latin": "Arial", "ea": "微软雅黑"},
        "semantic_contract": {
            "anchor_subject": "accent1",   # 深墨蓝 = 主主题
            "comparator": "accent2",       # 青 = 备选
            "neutral": "accent3",           # 蓝灰 = 表头/结构线
            "emphasis": "accent4",          # 橙 = 关键发现
        },
        "layouts": {"content": 0, "dark": 0, "red_conclusion": 0, "blank": 0, "cover": 0, "chapter": 0},
    },
}

def list_palettes():
    """返回 [(name, label), ...],供 Stage 0 展示可选内置配色。"""
    return [(n, p["label"]) for n, p in PALETTES.items()]

def get(palette_name):
    """取某套 palette 的 profile 数据(dict,等价 profile.yaml 内容)。无则 KeyError。"""
    if palette_name not in PALETTES:
        raise KeyError(f"无此内置配色: {palette_name} (已知: {list(PALETTES)})")
    return PALETTES[palette_name]

def has(palette_name):
    return palette_name in PALETTES
