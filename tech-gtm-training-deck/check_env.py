#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_env.py — tech-gtm-training-deck 环境预检(只报告,不自动装)。

检查:
  1. slide-maker skill 是否已装(本 skill 的 Stage 3 依赖它提供 deckkit/anim/render/lint)
  2. 本 skill 自身依赖:python-pptx / PyYAML / Pillow
  3. slide-maker 的依赖(渲染/lint 用):PyMuPDF / matplotlib / numpy
  4. LibreOffice(soffice,渲染 PNG 用)

每项缺失打印精确修复命令。退出码:全 OK=0,有缺失=1。
"""
import sys, os, shutil

SKILL_NAME = "tech-gtm-training-deck"
SLIDE_MAKER_PATHS = [
    os.path.expanduser(r"~/.claude/skills/slide-maker/scripts/deckkit.py"),
    os.path.expanduser(r"~/.agents/skills/slide-maker/scripts/deckkit.py"),
]

def check_module(mod, pip_name=None):
    try:
        __import__(mod)
        return True, None
    except ImportError:
        return False, pip_name or mod

def check_slide_maker():
    for p in SLIDE_MAKER_PATHS:
        if os.path.isfile(p):
            return True, p
    return False, None

def check_soffice():
    for name in ["soffice", "soffice.com", "soffice.exe"]:
        if shutil.which(name):
            return True, name
    # Windows: 常见安装路径(不在 PATH 时)
    for p in [r"C:\Program Files\LibreOffice\program\soffice.com",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.com"]:
        if os.path.isfile(p):
            return True, p
    return False, None

def check_icons():
    """内置网络设备图标数(network_topo 用)。缺则 network_topo 降级为形状节点。"""
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, "assets", "icons")
    if not os.path.isdir(d):
        return 0, d
    return sum(1 for f in os.listdir(d) if f.endswith(".png")), d

def main():
    ok = True
    print(f"{SKILL_NAME} environment check:\n")
    # 1. slide-maker
    sm, smp = check_slide_maker()
    if sm:
        print(f"  [ok]  slide-maker skill: {smp}")
    else:
        ok = False
        print(f"  [MISSING] slide-maker skill (Stage 3 needs deckkit/anim/render/lint)")
        print(f"           -> npx skills add addsumtech/slides_maker -g -y")
        print(f"           (or git clone https://github.com/addsumtech/slides_maker ~/.claude/skills/slide-maker)")

    # 2. 本 skill 依赖
    print()
    for mod, pip, label in [("pptx","python-pptx","read .pptx theme"),
                            ("yaml","PyYAML","profile.yaml load"),
                            ("PIL","Pillow","image metrics (optional)")]:
        mok, _ = check_module(mod, pip)
        if mok:
            print(f"  [ok]  {pip}")
        elif label.endswith("(optional)"):
            print(f"  [--]  {pip} (optional)")
        else:
            ok = False
            print(f"  [MISSING] {pip} — {label}")

    # 3. slide-maker 依赖(渲染/lint)
    print()
    for mod, pip in [("fitz","PyMuPDF"),("matplotlib","matplotlib"),("numpy","numpy")]:
        mok, _ = check_module(mod, pip)
        print(f"  [{'ok' if mok else 'MISSING'}]  {pip}  (slide-maker 用: 渲染/lint)")

    # 4. LibreOffice
    print()
    soff, soffn = check_soffice()
    if soff:
        print(f"  [ok]  LibreOffice ({soffn})")
    else:
        print(f"  [--]  LibreOffice (soffice) — PNG 渲染用;Stage 1-2 不需要")
        print(f"        Windows: 安装 LibreOffice | macOS: brew install --cask libreoffice | Linux: apt install libreoffice")

    # 5. 内置网络图标
    print()
    n, d = check_icons()
    if n >= 9:
        print(f"  [ok]  内置网络图标 {n} 个 (assets/icons/)")
    elif n > 0:
        print(f"  [--]  内置网络图标仅 {n} 个 (期望约9);network_topo 将对缺失 kind 降级为形状节点")
        print(f"        -> 在有 Chrome+联网的机器: set CHROME=... && python scripts/gen_icons.py")
    else:
        print(f"  [--]  assets/icons/ 为空(未生成);network_topo 降级为形状节点")
        print(f"        -> 可选: 装 Chrome + 设 CHROME 环境变量,跑 python scripts/gen_icons.py 生成图标")

    print()
    if ok:
        print("  => ready. Stages 1-2 always work; Stage 3 needs slide-maker + its deps above.")
    else:
        print("  => 有缺失,按上面命令安装后重跑。")
        print(f"     pip install -r requirements.txt")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
