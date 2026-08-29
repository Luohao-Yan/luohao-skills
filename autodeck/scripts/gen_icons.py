# -*- coding: utf-8 -*-
"""gen_icons.py — 一次性生成 assets/icons/ 下的网络设备图标 PNG(离线内置用)。

用 slide-maker 的 icons.py 从 tabler/lucide 抓 SVG + Chrome 光栅成 PNG,
固定深蓝灰 #3F5469。生成后提交 PNG 入仓,运行时 network_topo() 直接读,
不依赖 Chrome/联网。

前置:本机装 Chrome + 设 CHROME 环境变量(Windows):
    set CHROME=C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
需联网(从 CDN 抓 SVG)。

用法:
    python scripts/gen_icons.py
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))
from slide_maker_path import find_slide_maker
SM = find_slide_maker()

ICONS = {
    "server":   "tabler:server",
    "router":   "tabler:router",
    "switch":   "tabler:switch",
    "cloud":    "tabler:cloud",
    "lan":      "tabler:network",
    "firewall": "lucide:shield",
    "ap":       "tabler:access-point",
    "database": "lucide:database",
    "laptop":   "tabler:device-laptop",
}
COLOR = "#3F5469"
OUT_DIR = os.path.join(SKILL_ROOT, "assets", "icons")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    icons_py = os.path.join(SM, "icons.py")
    ok, fail = [], []
    for name, spec in ICONS.items():
        out = os.path.join(OUT_DIR, f"{name}.png")
        r = subprocess.run([sys.executable, icons_py, spec, out, "--color", COLOR, "--px", "160"],
                           capture_output=True, text=True)
        if os.path.isfile(out) and os.path.getsize(out) > 100:
            ok.append(name)
        else:
            fail.append((name, spec, r.stderr.strip().splitlines()[-1] if r.stderr else "?"))
    print(f"generated {len(ok)}: {ok}")
    if fail:
        print(f"FAILED {len(fail)}:")
        for n, s, e in fail:
            print(f"  {n} ({s}): {e}")
        print("\n前置检查: 设 CHROME 环境变量 + 联网。见 gen_icons.py docstring。")
        sys.exit(1)

if __name__ == "__main__":
    main()
