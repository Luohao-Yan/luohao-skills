# -*- coding: utf-8 -*-
"""build.py — DeepSeek Harness 培训 deck(示例,品牌色从 profile.yaml 读,非硬编)

tech-training-deck skill 的 Stage 3 产物示例。复用 slide-maker 的 deckkit/anim,
品牌色/字体/layout 从 profile.yaml 通过 deck_helpers.Deck 加载。

跑通需:① 装好 slide-maker skill;② 把 TPL 改成你的 .pptx;③ profile.yaml 填好 semantic_contract。
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))   # examples/deepseek-harness/
SKILL_ROOT = os.path.dirname(os.path.dirname(HERE))  # tech-training-deck/
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))   # 本 skill 的 scripts(含 slide_maker_path/load_profile/deck_helpers)
from slide_maker_path import find_slide_maker
sys.path.insert(0, find_slide_maker())   # slide-maker 的 scripts(deckkit/anim,自动探测)
import deckkit as dk
from anim import Build
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from load_profile import load
from deck_helpers import Deck, set_title, num_circle, chap, card, para, notes

TPL = r"<改为你自己的.pptx模板路径>"   # 例:r"C:/Users/.../某企业模板.pptx"
OUT = os.path.join(HERE, "training-deck.pptx")

P = load(os.path.join(HERE, "profile.yaml"))
D = Deck(P)
W_IN, H_IN = D.W, D.H
WHITE = RGBColor(0xFF,0xFF,0xFF)
DARK = RGBColor(0x2A,0x2A,0x33)
INK = RGBColor(0x2A,0x2A,0x33)
MUTE = RGBColor(0x6B,0x6B,0x6B)
CARDBG = RGBColor(0xF7,0xF7,0xFA)
DEEP = RGBColor(0xC6,0x00,0x00)

def build():
    prs = dk.open_template(TPL)

    # 1 封面
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("cover")])
    try:
        t = s.placeholders[0]; t.text = "DeepSeek Harness 能力培训"
        for p in t.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(40); r.font.bold=True; r.font.color.rgb=WHITE; r.font.name=dk.EAFONT
                dk._apply_ea(r, dk.EAFONT)
    except Exception: pass
    for pidx, txt in [(10,"给公司领导 · 一切皆插件 · 模型底座之争"),(11,"2026/08/16")]:
        try:
            ph = s.placeholders[pidx]; ph.text = txt
            for p in ph.text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = dk.EAFONT; dk._apply_ea(r, dk.EAFONT)
        except Exception: pass
    notes(s, "开场:今天用十几分钟,讲清 DeepSeek 开源的 Harness 是什么、为什么重要。")

    # 2 目录
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "目录  Catalog", D.anchor)
    col = dk.columns(2, slide=s, top=1.4, bottom=0.7, margin=0.62, gap=0.5)
    for label, items, accent, ci in [("01 认清四个产品",["四个产品到底是谁的","WorkBuddy/灵犀/Comate 区别","关键发现:Comate 内嵌 Pi"], D.anchor, 0),
                                       ("02 看懂 Harness 与战略",["一切皆插件怎么实现","DeepSeek 如何锁模型底座","dsh vs Pi 对比 · 给我们的建议"], D.comparator, 1)]:
        x,y,w,h = col[ci]
        card(s, x, y, w, h, fill=CARDBG, line=accent, line_w=1.2)
        dk.text(s, x+0.3, y+0.22, w-0.6, 0.4, [[(label[:2], 22, accent, True, False, dk.FONT)]], wrap=False)
        dk.text(s, x+0.3, y+0.62, w-0.6, 0.4, [[(label[3:], 18, DARK, True, False, dk.EAFONT)]], wrap=False)
        yy = y+1.15
        for it in items:
            dk.text(s, x+0.4, yy, w-0.8, 0.32, [[("#  "+it, 13.5, INK, False, False, dk.EAFONT)]]); yy += 0.38
    notes(s, "分两部分:先厘清易混产品,再看架构和战略,最后给建议。")

    # 3 章节页
    chap(prs, D, "chapter", "01", "先厘清:这些产品到底是什么", sub="WorkBuddy·灵犀·Comate·dsh 各是谁的")
    notes(s, "市面上几个产品常被混为一谈,先把归属讲清楚。")

    # 4 四产品归属表
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "先纠偏:四个产品,四个归属", D.anchor)
    cols = dk.columns(4, slide=s, top=1.35, bottom=0.95, margin=0.5, gap=0.28)
    data = [("DeepSeek Harness","DeepSeek 官方","开源 Agent 框架","编程底座\n不含办公",D.anchor),
            ("WorkBuddy","腾讯·非DeepSeek","桌面工作台","编程强\n办公靠技能",D.comparator),
            ("WPS 灵犀","金山 WPS","AI 办公智能体","编程+办公\n都在壳里",DEEP),
            ("WPS Comate","金山 WPS","桌面 Agent","内嵌 Pi\n编程+JSAPI",D.neutral)]
    for (name,owner,form,feat,col),c in zip(data, cols):
        x,y,w,h = c
        card(s, x, y, w, h, fill=WHITE, line=col, line_w=1.6, r=0.1)
        dk.box(s, x, y, w, 0.52, fill=col, round=True, corners='top', r=0.1)
        dk.text(s, x+0.16, y+0.05, w-0.32, 0.42, [[(name, 16, WHITE, True, False, dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE)
        dk.text(s, x+0.18, y+0.64, w-0.36, 0.32, [[(owner, 13, col, True, False, dk.EAFONT)]], wrap=False)
        dk.text(s, x+0.18, y+1.0, w-0.36, 0.32, [[(form, 12.5, D.neutral, False, False, dk.EAFONT)]])
        dk.box(s, x+0.18, y+1.38, w-0.36, 0.012, fill=RGBColor(0xDD,0xDD,0xDD))
        dk.text(s, x+0.18, y+1.5, w-0.36, 0.7, [[(feat, 13, INK, False, False, dk.EAFONT)]], line_spacing=1.2)
    dk.bottom_callout(s, 0.5, W_IN-1.0, "关键纠偏", "WorkBuddy 是腾讯的、非 DeepSeek;灵犀(千万办公)才含 WPS 办公功能;Comate 内嵌第三方开源 Pi。", label_c=D.anchor, body_c=DARK)
    notes(s, "WorkBuddy 不是 DeepSeek 的,是腾讯;灵犀才真正含 WPS 办公;Comate 内嵌第三方 Pi。")

    # 5 关键发现(深色页)
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("dark")]); set_title(s, "关键发现:WPS Comate 内嵌的就是 Pi", WHITE)
    cols = dk.columns(2, slide=s, top=1.35, bottom=0.75, margin=0.5, gap=0.5)
    x,y,w,h = cols[0]
    card(s, x, y, w, h, fill=RGBColor(0x2A,0x14,0x18), line=D.anchor, line_w=1.5)
    dk.text(s, x+0.3, y+0.25, w-0.6, 0.5, [[("本机实测", 13, D.comparator, True, False, dk.EAFONT)]], wrap=False)
    dk.text(s, x+0.3, y+0.6, w-0.6, 1.2, [[("金山自家的 WPS Comate,",16,WHITE,True,False,dk.EAFONT),("核心就是 Pi",16,D.emphasis,True,False,dk.EAFONT),(" v0.79.3",15,WHITE,False,False,dk.EAFONT)]], line_spacing=1.3)
    x,y,w,h = cols[1]
    card(s, x, y, w, h, fill=RGBColor(0x1A,0x22,0x2E), line=D.neutral, line_w=1.2)
    dk.text(s, x+0.3, y+0.25, w-0.6, 0.4, [[("意味着什么", 13, D.emphasis, True, False, dk.EAFONT)]], wrap=False)
    for i,it in enumerate(["Pi 轻量路线已被产品化落地","选型与产品方向一致、风险低","与 dsh 同源 pi-ai,可平滑评估"]):
        dk.text(s, x+0.3, y+0.7+i*0.56, w-0.6, 0.5, [[("▸  ",13,D.anchor,True,False,dk.FONT),(it,13,WHITE,False,False,dk.EAFONT)]], line_spacing=1.2)
    dk.bottom_callout(s, 0.5, W_IN-1.0, "三大 harness 互不内嵌", "WorkBuddy 用 codebuddy、Comate 用 Pi、DeepSeek 用 dsh——各自独立。", label_c=D.emphasis, body_c=WHITE, fill=RGBColor(0x2A,0x14,0x18))
    notes(s, "金山自家 Comate 的核心运行时就是第三方 Pi;我们也在用 Pi。三大 harness 互不内嵌。")

    # 6 章节页
    chap(prs, D, "chapter", "02", 'DeepSeek Harness 如何"一切皆插件"', sub="Cordis·能力 seam·插件树·创造模式")
    notes(s, "进入架构,目标让领导看懂插件化体现在哪。")

    # 7 定位+四模式
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "定位:Agent = 模型 + Harness", D.anchor)
    dk.text(s, 0.7, 1.5, 12, 1.2, [[("Agent",40,D.anchor,True,False,dk.FONT),(" = ",32,DARK,True,False,dk.FONT),("模型",34,D.neutral,True,False,dk.EAFONT),(" + ",30,DARK,True,False,dk.FONT),("Harness",40,D.comparator,True,False,dk.FONT)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    dk.text(s, 0.7, 2.7, 12, 0.5, [[("模型负责『想』,Harness 负责理解环境、调工具、组织多步任务", 14, MUTE, False, False, dk.EAFONT)]], align=PP_ALIGN.CENTER)
    modes = [("标准","默认全套工具,日常开发"),("PTC","生成代码组合多步调用"),("极简","只留 Shell,跑基准"),("创造","agent 改自己的插件")]
    cols = dk.columns(4, slide=s, top=3.6, bottom=0.95, margin=0.5, gap=0.3)
    b8 = Build(s)
    for i,((n,d),c) in enumerate(zip(modes, cols)):
        x,y,w,h = c
        with b8.step():
            card(s, x, y, w, h, fill=CARDBG, line=D.neutral, line_w=1.0, r=0.1)
            num_circle(s, x+w/2-0.28, y+0.18, 0.56, i+1, D.anchor, D.comparator, size=16)
            dk.text(s, x+0.12, y+0.82, w-0.24, 0.35, [[(n, 15, D.anchor, True, False, dk.EAFONT)]], align=PP_ALIGN.CENTER)
            dk.text(s, x+0.12, y+1.18, w-0.24, 0.6, [[(d, 14, INK, False, False, dk.EAFONT)]], align=PP_ALIGN.CENTER, line_spacing=1.1)
    b8.apply(effect="fade")
    dk.bottom_callout(s, 0.5, W_IN-1.0, "一句话", "让大模型『能动手干活』的运行时底座,对标 Claude Code / Codex,开源。", label_c=D.anchor, body_c=DARK)
    notes(s, "Agent=模型+Harness。四模式:标准/PTC/极简/创造。创造模式 agent 能改自己的插件。")

    # 8 Cordis 五概念
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "Cordis 五概念,让每一部分都可替换", D.anchor)
    concepts = [("插件=服务","ctx.*","带 apply(ctx) 的函数或 Service 子类"),("上下文按 key 找","ctx.tools/llm","按稳定 key 找服务,不 import 实现"),("inject 声明依赖","inject:[]","等依赖就绪才启动,加载顺序由依赖决定"),("事件四模式","emit/waterfall/…","观察·改写·扇出·按序"),("注册可逆","ctx.effect/on","装的副作用卸载时自动撤销")]
    rows = dk.rows(5, slide=s, top=1.4, bottom=0.75, gap=0.22)
    for i,((n,key,d),c) in enumerate(zip(concepts, rows)):
        x,y,w,h = c
        dk.box(s, x, y, 0.42, h, fill=D.anchor, round=True, r=0.06)
        dk.text(s, x, y, 0.42, h, [[(str(i+1),16,WHITE,True,False,dk.FONT)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        card(s, x+0.55, y, w-0.55, h, fill=CARDBG, line=RGBColor(0xE8,0xE8,0xEE), line_w=1.0, r=0.06)
        dk.text(s, x+0.75, y+0.06, 3.4, 0.35, [[(n,14,D.anchor,True,False,dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        dk.text(s, x+0.75, y+0.06, 3.4, h-0.12, [[(key,13,D.neutral,False,False,dk.FONT)]], anchor=MSO_ANCHOR.BOTTOM, wrap=False)
        dk.box(s, x+4.25, y+0.12, 0.012, h-0.24, fill=RGBColor(0xDD,0xDD,0xDD))
        dk.text(s, x+4.45, y+0.05, w-4.65, h-0.1, [[(d,14,INK,False,False,dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
    notes(s, "Cordis 五概念:插件=服务/上下文按key/inject/事件四模式/注册可逆。没有特权内核。")

    # 9 signature move: ctx.llm 插槽图
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "能力 seam:换一个 Provider,换一个世界", D.anchor)
    slot_x, slot_y, slot_w, slot_h = 0.62, 1.4, 3.3, 2.6
    card(s, slot_x, slot_y, slot_w, slot_h, fill=RGBColor(0x1A,0x22,0x2E), line=D.neutral, line_w=2.0, r=0.1)
    dk.text(s, slot_x+0.2, slot_y+0.15, slot_w-0.4, 0.4, [[("ctx.llm 插槽", 14, D.emphasis, True, False, dk.FONT)]], anchor=MSO_ANCHOR.MIDDLE)
    dk.box(s, slot_x+0.35, slot_y+1.1, slot_w-0.7, 1.2, fill=RGBColor(0x0D,0x12,0x1A), line=D.anchor, line_w=1.5, round=True, r=0.08)
    dk.text(s, slot_x+0.35, slot_y+1.1, slot_w-0.7, 1.2, [[("Provider\n插这里",14,RGBColor(0xFF,0xAA,0xAA),False,False,dk.EAFONT)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
    dk.arrow(s, slot_x+slot_w+0.05, slot_y+slot_h/2-0.25, 0.7, 0.5, color=D.anchor, direction='right')
    provs = [("llm-deepseek","DeepSeek 原生",D.anchor,True),("llm-pi-ai","经 pi-ai 接任意",D.comparator,False),("llm-replay","回放测试",MUTE,False)]
    px = slot_x+slot_w+0.95; pw = (W_IN-0.62-px-0.3)/3 - 0.2
    for i,(nm,d,col,hi) in enumerate(provs):
        x = px + i*(pw+0.25); y = slot_y+0.1
        card(s, x, y, pw, 2.6, fill=RGBColor(0xFF,0xF4,0xF6) if hi else WHITE, line=col, line_w=2.2 if hi else 1.2, r=0.1)
        if hi:
            dk.box(s, x, y, pw, 0.4, fill=col, round=True, corners='top', r=0.1)
            dk.text(s, x+0.1, y+0.02, pw-0.2, 0.36, [[("★ 默认",11,WHITE,True,False,dk.EAFONT)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        dk.text(s, x+0.12, y+0.5, pw-0.24, 0.4, [[(nm,14,col,True,False,dk.FONT)]], align=PP_ALIGN.CENTER, wrap=False)
        dk.text(s, x+0.12, y+0.95, pw-0.24, 0.5, [[(d,13,INK,False,False,dk.EAFONT)]], align=PP_ALIGN.CENTER, line_spacing=1.15)
        dk.text(s, x+0.12, y+1.62, pw-0.24, 0.8, [[("换这个\n= 换模型底座",14,D.anchor,True,False,dk.EAFONT)]], align=PP_ALIGN.CENTER, line_spacing=1.1)
    dk.bottom_callout(s, 0.5, W_IN-1.0, "seam 三角色", "Service Definition·Service Provider(并列可换)·Consumer——三者一并设计才是一个完整能力。", label_c=D.anchor, body_c=DARK)
    notes(s, "ctx.llm 是插槽,三个 Provider 可换,DeepSeek 默认。换 Provider=换模型底座。")

    # 10 章节页
    chap(prs, D, "chapter", "03", "DeepSeek 如何用 Harness 锁定模型底座", sub="用『动手层』标准化,反向锁定『模型层』")
    notes(s, "进入战略,今天最该记住的部分。")

    # 11 战略四步
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "战略:用『动手层』标准化,反向锁定『模型层』", D.anchor)
    steps = [("默认带 DeepSeek","模型在 dsh 是可换插件,但默认体验/生态偏 DeepSeek"),("先选 harness 再选模型","团队建技术栈后迁移成本陡增;换模型只是一个插件"),("数据/反馈回流","更多 Agent 跑在 DeepSeek 上,真实数据反哺迭代"),("生态飞轮","Cordis + dsh-plugin 话题;24h 已 288 个插件仓")]
    rows = dk.rows(4, slide=s, top=1.4, bottom=1.1, gap=0.24)
    b13 = Build(s)
    for i,((n,d),c) in enumerate(zip(steps, rows)):
        x,y,w,h = c
        with b13.step():
            num_circle(s, x+0.1, y+h/2-0.27, 0.54, i+1, D.anchor, D.comparator, size=18)
            card(s, x+0.8, y, w-0.8, h, fill=CARDBG, line=RGBColor(0xE8,0xE8,0xEE), line_w=1.0, r=0.08)
            dk.text(s, x+1.0, y+0.12, w-1.2, 0.35, [[(n,15,D.anchor,True,False,dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE, wrap=False)
            dk.text(s, x+1.0, y+0.12, w-1.2, h-0.24, [[("　",1,WHITE,False,False),(d,14,INK,False,False,dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)
    b13.apply(effect="fade")
    dk.bottom_callout(s, 0.5, W_IN-1.0, "一句话", "谁定义 harness 标准,谁就定义模型被怎么用、用谁的。同时开源模型和 harness,用动手层标准化反向强化模型层粘性。", label_c=D.anchor, body_c=DARK)
    notes(s, "四步:默认带DeepSeek/先选harness/数据回流/生态飞轮。谁定义harness谁定义模型分发。")

    # 12 dsh vs Pi 对比
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "dsh 与 Pi:同源 pi-ai,分道于架构", D.anchor)
    headers = ["维度","DeepSeek Harness (dsh)","Pi"]
    rows_data = [["定位","官方开源·有 Web UI+CLI","独立开发者·纯终端 TUI(已入 Comate)"],["架构","一切皆插件·Cordis DI 容器","最小核心·注册式扩展"],["模型","默认 DeepSeek·多 provider","不锁定·30+ provider"],["能力包","官方维护几十个(一等公民)","核心 5 包,余靠扩展"],["办公","无","无(Comate 经 JSAPI 补)"],["部署","npx dsh web 一键起","npm i -g pi-coding-agent"],["底层","把 pi-ai 当可插拔后端","把 pi-ai 当内置底座"]]
    col_w = [1.7, 5.75, 5.25]
    dk.table(s, 0.62, 1.4, sum(col_w), [headers]+rows_data, col_w=col_w, header=True, size=13, row_h=0.56, head_c=D.anchor, body_c=INK, hi_fill=RGBColor(0xFF,0xF4,0xF6), hi_c=D.anchor)
    dk.text(s, 0.62, H_IN-0.55, 12.1, 0.45, [[("关键同源:",12.5,D.anchor,True,False,dk.EAFONT),("两者都用 ",12.5,INK,False,False,dk.EAFONT),("@earendil-works/pi-ai",12.5,D.neutral,True,False,dk.FONT),(" 作 LLM 抽象层——用 Pi 调通公司模型的经验可复用到评估 dsh。",12.5,INK,False,False,dk.EAFONT)]], line_spacing=1.15)
    notes(s, "对比:Pi 非金山自研但已被 Comate 内嵌。七维对比。同源 pi-ai,迁移成本低。")

    # 13 建议
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "五条建议,应对 harness 之争与模型趋同", D.anchor)
    advs = [("跟踪分发权","把 harness=分发权列为新战略变量","政企选型可能先选框架再选模型"),("借鉴 seam 化","研究 dsh seam 对架构的借鉴","适配私有化换模型/换部署/换沙箱"),("Pi 路线坚定","Pi 已被产品化验证、与 dsh 同源","短期提效,dsh 作平台化备选"),("勿上生产","dsh 是开发者预览、有破坏性变更","定位预研/POC,版本收敛再评估"),("厘清口径","对外统一产品归属口径","讲混会损害可信度")]
    rows = dk.rows(5, slide=s, top=1.4, bottom=0.75, gap=0.2)
    for i,((n,d,how),c) in enumerate(zip(advs, rows)):
        x,y,w,h = c
        num_circle(s, x, y+h/2-0.24, 0.48, i+1, D.anchor, D.comparator, size=15)
        card(s, x+0.65, y, w-0.65, h, fill=WHITE if i%2==0 else CARDBG, line=RGBColor(0xE8,0xE8,0xEE), line_w=1.0, r=0.06)
        dk.text(s, x+0.85, y+0.05, 3.1, h-0.1, [[(n,14,D.anchor,True,False,dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        dk.box(s, x+4.05, y+0.1, 0.012, h-0.2, fill=RGBColor(0xDD,0xDD,0xDD))
        dk.text(s, x+4.25, y+0.05, w-4.45, h-0.1, [[(d,14,INK,False,False,dk.EAFONT)]], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)
    dk.text(s, 0.62, H_IN-0.42, 12, 0.32, [[("口径:",11,MUTE,False,False,dk.EAFONT),("WorkBuddy=腾讯·灵犀=金山·Comate=金山(内嵌Pi)·Pi=第三方·dsh=DeepSeek",11,D.neutral,False,False,dk.EAFONT)]])
    notes(s, "五条:跟踪分发权/借鉴seam/Pi坚定/勿上生产/厘清口径。")

    # 14 结论
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("red_conclusion")]); set_title(s, "结论", WHITE)
    dk.text(s, 1.0, 2.2, 11.3, 2.0, [[("dsh 既是",24,WHITE,True,False,dk.EAFONT),("技术借鉴对象",26,D.emphasis,True,False,dk.EAFONT),(",也是",24,WHITE,True,False,dk.EAFONT),("战略变量",26,D.emphasis,True,False,dk.EAFONT),("。",24,WHITE,True,False,dk.EAFONT)],[("",8,WHITE,False,False)],[("短期:Pi 路线已被验证落地、且本团队在用——可坚定。",16,WHITE,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("中期:dsh 作平台化底座候选持续观察,借鉴其 seam 化设计。",16,WHITE,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("长期:评估把自身方案架构『接缝化』,对冲模型层趋同风险。",16,WHITE,False,False,dk.EAFONT)]], line_spacing=1.2)
    notes(s, "收尾:dsh 既是借鉴对象也是战略变量。短期Pi坚定,中期dsh观察,长期接缝化。")

    # 15 附录
    s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")]); set_title(s, "附录·证据出处", D.anchor)
    dk.text(s, 0.7, 1.5, 12, 5, [[("A. DeepSeek Harness(本地源码):",12.5,D.anchor,True,False,dk.EAFONT),(" README/architecture/cordis-primer · agent-presets · cordis-host-runner · llm-pi-ai",11,INK,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("B. Pi(本机已装 0.84.2):",12.5,D.comparator,True,False,dk.EAFONT),(" @earendil-works/pi-coding-agent · 本机 models.json · 与 dsh 共用 pi-ai",11,INK,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("C. WorkBuddy(本机实测):",12.5,D.anchor,True,False,dk.EAFONT),(" AppData/Local/Programs/WorkBuddy(腾讯,Electron)·codebuddy CLI·copilot.tencent.com",11,INK,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("D. WPS Comate(本机实测):",12.5,D.anchor,True,False,dk.EAFONT),(" AppData/Local/WPS Comate(金山·内嵌Pi v0.79.3)·comate.wps.cn",11,INK,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("E. WPS 灵犀(官方):",12.5,D.anchor,True,False,dk.EAFONT),(" lingxi.wps.cn · Python/Node/AirScript + WPS Office 集成",11,INK,False,False,dk.EAFONT)],[("",6,WHITE,False,False)],[("完整证据见同名 md 培训稿附录。",11,MUTE,False,False,dk.EAFONT)]], line_spacing=1.1)
    notes(s, "附录:所有结论的证据出处。完整证据链在培训稿 md 附录。")

    dk.lint_layout(prs, strict=True)
    prs.save(OUT)
    print("saved:", OUT, "slides:", len(prs.slides._sldIdLst))

if __name__ == "__main__":
    build()
