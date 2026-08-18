# -*- coding: utf-8 -*-
"""brief.py — Stage 0 访谈产物 brief.yaml 的读写 + 默认值兜底。

Stage 0 访谈把用户答案合并进默认值,写 brief.yaml;Stage 1/2/3 读它定方向。
纯函数,无 IO 副作用(load/write 显式传路径)。字段缺失用默认兜底,不报错。
"""
import os, re
import yaml

DEFAULTS = {
    "subject": "",
    "tilt": "balanced",            # tech / vision / balanced
    "audience": "leaders",         # leaders / team / customer / mixed
    "purpose": "",                 # 自由文本,核心目的/故事线
    "pages": "15-20",              # 10-15 / 15-20 / 20+
    "animation": True,
    "template": "auto",            # 指定路径 / auto(默认池) / none
    "language": "zh",              # zh / en / bilingual
    "emphasis": "balanced",        # strategy/arch/compare/ops/data/balanced
    "fidelity": "traced",          # traced / lite / minimal
    "need_arch_diagram": False,    # bool;tilt=tech 推导 true,用户可覆盖
    "need_network_topo": False,    # bool;默认 false
    "outdir": "",                  # 产物目录
}

def slugify(t):
    """主题 -> 文件名 slug(保留字母数字-_,中文等非之字符转 -,首尾去 -)。
    DeepSeek-V4-Flash 部署与适配 -> deepseek-v4-flash"""
    s = re.sub(r"[^a-z0-9_-]+", "-", t.lower()).strip("-")
    return s or "deck"

def _derive(subject, tilt):
    """从 subject/tilt 推导 purpose/outdir/need_arch_diagram(若用户没给)。"""
    d = {}
    d["need_arch_diagram"] = (tilt == "tech")
    if not d["need_arch_diagram"]:
        # tilt 非 tech 时,默认 false(若用户显式传 True 则合并阶段保留)
        pass
    return d

def merge_with_defaults(answers):
    """访谈答案 + 默认值 -> 完整 13 字段 dict。用户显式值优先,缺失兜底。"""
    m = dict(DEFAULTS)
    m.update({k: v for k, v in (answers or {}).items() if v is not None and v != ""})
    # need_arch_diagram: 若用户没显式给,由 tilt 推导
    if "need_arch_diagram" not in (answers or {}):
        m["need_arch_diagram"] = (m.get("tilt") == "tech")
    # purpose 缺则由 subject 推导一句
    if not m.get("purpose"):
        m["purpose"] = f"把 {m.get('subject','该主题')} 讲清,支撑听众决策"
    # outdir 缺则由 subject slug 推导
    if not m.get("outdir"):
        m["outdir"] = f"output/{slugify(m.get('subject','deck'))}-deck"
    return m

def write_brief(data, path):
    """写 brief.yaml(有序,字段顺序固定便于人读)。"""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    ordered = {k: data.get(k, DEFAULTS.get(k)) for k in DEFAULTS}
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(ordered, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

def load_brief(path):
    """读 brief.yaml,缺失字段用默认兜底(Global Constraint:不报错)。"""
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return merge_with_defaults(raw)
