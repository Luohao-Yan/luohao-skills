# -*- coding: utf-8 -*-
"""template_pool.py — resolve brief.template field to a real .pptx path or builtin palette.

template field 取值:
  "" 或 "auto"             -> 取默认模板池首个存在者(同 DEFAULT_POOL 顺序)
  "<style 名>"             -> 取 STYLES 中该风格名对应的路径(如 "red-gov")
  "builtin:<palette 名>"   -> 不用 .pptx,用 builtin_palettes 里的内置配色(无品牌)
  "<绝对/相对路径>"        -> 该 .pptx 路径(存在与否交给 inspect 阶段报错)
  "none"                   -> None(slide-maker 从零设计)

默认模板池与 SKILL.md ## Default template pool 节一致。forker 改自己机器的模板路径,
或在 STYLES 里给风格起名。DEFAULT_POOL 保持纯路径列表(测试 monkeypatch 兼容)。
"""
import os

DEFAULT_POOL = [
    r"C:\Users\KC\orca\projects\Pre-seles-architect-scheme\output\deepseek-harness培训\DeepSeek-Harness能力培训.pptx",
    r"C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx",
]

# 风格名 -> 路径(给 brief.template 用风格名选;forker 加自己模板时这里起名)。
# 现两个模板同属金山云红政企风格,都标 red-gov(取首个即可,无 tilt 选择)。
STYLES = {
    "red-gov": DEFAULT_POOL[0],
    "red-gov-mem": DEFAULT_POOL[1],   # 记忆系统那份,同风格不同页型范例
}

def list_styles():
    """返回池中可用风格 [(name, exists, accent_hint), ...],供 Stage 0 展示可选。"""
    return [(n, os.path.isfile(p), "red-accent 政企") for n, p in STYLES.items()]

def is_builtin(token):
    """token 形如 'builtin:slate-business' -> palette 名;否则 None。"""
    if token and token.startswith("builtin:"):
        return token.split(":", 1)[1].strip()
    return None

def resolve(template_field):
    """返回应 inspect 的 .pptx 绝对路径,或 None(不用模板)。
    builtin:<名> 也返回 None(由调用方转去 builtin_palettes 取 palette,不 inspect .pptx)。"""
    t = (template_field or "").strip()
    # builtin 配色:不走 .pptx
    pal = is_builtin(t)
    if pal:
        return None
    if t == "" or t == "auto":
        for p in DEFAULT_POOL:
            if os.path.isfile(p):
                return p
        return None
    if t == "none":
        return None
    # 风格名
    if t in STYLES:
        return STYLES[t]
    return t   # 用户指定路径,原样返回
