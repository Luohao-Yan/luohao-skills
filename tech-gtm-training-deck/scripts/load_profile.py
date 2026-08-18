#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""load_profile.py — build 脚本通过它从 profile.yaml 加载品牌色/字体/layout idx。

修"人工抄硬编码常量、易与模板漂移"的坑:build 脚本不再写
    RED = RGBColor(0xE6, 0x00, 0x2D)   # 从 profile 抄来的
而是写
    from load_profile import load
    P = load("profile.yaml")
    RED = P.color("accent1")           # 直接从模板主题色来

用法(build 脚本内):
    import sys, os
    sys.path.insert(0, "<skill>/scripts")
    from load_profile import load
    P = load(os.path.join(os.path.dirname(__file__), "profile.yaml"))
    RED = P.color("accent1")          # RGBColor
    FONT, EAFONT = P.fonts()
    LAYOUT_CONTENT = P.layout("content")  # int idx
"""
import os
try:
    import yaml
except ImportError:
    raise SystemExit("load_profile 需要 PyYAML: pip install pyyaml")
from pptx.dml.color import RGBColor

class Profile:
    def __init__(self, data, path):
        self.data = data
        self.path = path
        self._colors = data.get("colors", {})
        self._fonts = data.get("fonts", {})
        self._layouts = data.get("layouts", {})
        self._sem = data.get("semantic_contract", {}) or {}
    def color(self, accent_or_role):
        """按 accent 名(accent1)或语义角色(anchor_subject)取色,返回 RGBColor。
        先查语义契约,再查 accent 本名。"""
        key = self._sem.get(accent_or_role, accent_or_role)
        hexv = self._colors.get(key) or self._colors.get(accent_or_role)
        if not hexv:
            raise KeyError(f"profile 无此色: {accent_or_role} (语义契约={self._sem}, 已知 accents={list(self._colors)})")
        h = hexv.lstrip("#")
        return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))
    def colors(self):
        """返回 {accent: RGBColor} 全表。"""
        return {k: self.color(k) for k in self._colors}
    def fonts(self):
        """返回 (latin, ea) 元组,供 deckkit dk.FONT/dk.EAFONT。"""
        f = self._fonts
        return f.get("latin", "Arial"), f.get("ea", "Arial")
    def layout(self, role):
        """按 role 名取 layout idx(int)。"""
        idx = self._layouts.get(role)
        if idx is None:
            raise KeyError(f"profile 无此 layout role: {role} (已知={list(self._layouts)})")
        return idx
    def canvas(self):
        c = self.data.get("canvas", {})
        return c.get("w_in", 13.333), c.get("h_in", 7.5)
    def gradient3(self):
        return [self.color(h) if isinstance(h,str) else h for h in self._fonts.get("gradient3", [])]

def load(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"profile.yaml 不存在: {path} (先跑 inspect_and_profile.py 生成)")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Profile(data, path)
