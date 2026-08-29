#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pathguard.py — 写盘路径安全护栏(防 CWE-22 路径穿越)。

本 skill 的脚本会把 用户输入的路径(CLI 参数 / brief.outdir)写成文件:
    new_deck 的 --out、inspect_and_profile 的 --out、brief 的 outdir ...
若直接写,用户(或被诱导传参)可用 ../ 把产物写到预期目录之外。这里在写盘前统一校验:

  unsafe(path)              -> True:路径含 ".." 穿越组件(含 Windows 反斜杠写法)
  ensure_no_dotdot(path)    -> 拒绝任何含 ".." 组件的路径,否则回 path
  ensure_inside(path, base) -> 解析后必须落在 base(默认 CWD)之内,否则抛 ValueError

纯函数,外加 write_guarded 一个护栏内落盘入口。写盘处 import pathguard 后统一走 write_guarded。
"""
import os
from pathlib import Path

def _parts(path):
    """把路径按分隔符拆成组件,兼容 Windows 反斜杠('..\\evil')与正斜杠混用。
    统一把 \\ 归一为 / 再拆,避免 os.sep 平台差异导致漏判 'a/../b' 里的 '..'。"""
    return str(path).replace("\\", "/").split("/")

def unsafe(path):
    """是否含 '..' 目录穿越组件。含 -> True(拒绝写)。"""
    return ".." in _parts(path)

def ensure_no_dotdot(path):
    """拒绝含 '..' 组件的路径(穿越逃逸的根因);干净则原样返回。"""
    if unsafe(path):
        raise ValueError(f"path contains '..' traversal component: {path!r}")
    return path

def ensure_inside(path, base=None):
    """解析后必须落在 base(默认当前工作目录)之内;越界抛 ValueError。"""
    base = os.path.abspath(base or os.curdir)
    full = os.path.abspath(path)
    if full != base and not full.startswith(base + os.sep):
        raise ValueError(f"refusing to write outside {base}: {path!r}")
    return path

def safe_out_path(path, base=None):
    """写盘前统一护栏:拒绝 '..' + 约束在 base(CWD)内,返回原 path。"""
    ensure_no_dotdot(path)
    return ensure_inside(path, base)

def write_guarded(path, text, *, base=None, inside=True, encoding="utf-8"):
    """护栏内写 UTF-8 文本,再落盘。

    - inside=True(默认):dotdot 拒绝 + 约束在 base(CWD)内 —— 供 CLI 产物
      (new_deck --out / inspect --out)等应留在项目内的写路径。
    - inside=False:仅拒绝 '..' 穿越,不做 CWD 约束 —— 供 write_brief 等
      把 brief.yaml 写到显式绝对路径(如用户指定的 outdir / pytest tmp_path)的库调用。
    调用方不要再自行以写模式落盘——统一走这里,杜绝漏掉护栏。
    返回写入的绝对路径。
    """
    safe = safe_out_path(path, base) if inside else ensure_no_dotdot(path)
    Path(safe).parent.mkdir(parents=True, exist_ok=True)
    Path(safe).write_text(text, encoding=encoding)
    return os.path.abspath(safe)
