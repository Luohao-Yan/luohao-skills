# -*- coding: utf-8 -*-
"""template_pool.py — resolve brief.template field to a real .pptx path.

template: auto(默认) -> 取默认模板池首个存在者;
template: <path>    -> 该路径(存在与否交给 inspect 阶段报错);
template: none      -> None(slide-maker 从零设计);
空值                 -> 等同 auto.

默认模板池与 SKILL.md ## Default template pool 节一致。forker 改自己机器的模板路径。
"""
import os

DEFAULT_POOL = [
    r"C:\Users\KC\orca\projects\Pre-seles-architect-scheme\output\deepseek-harness培训\DeepSeek-Harness能力培训.pptx",
    r"C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx",
]

def resolve(template_field):
    """返回应 inspect 的 .pptx 绝对路径,或 None(不用模板)。"""
    t = (template_field or "").strip()
    if t == "" or t == "auto":
        for p in DEFAULT_POOL:
            if os.path.isfile(p):
                return p
        return None
    if t == "none":
        return None
    return t   # 用户指定路径,原样返回
