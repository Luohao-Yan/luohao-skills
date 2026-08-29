# -*- coding: utf-8 -*-
import os, tempfile
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import brief
import pathguard

def test_defaults_has_14_fields():
    assert len(brief.DEFAULTS) == 14
    for k in ["subject","tilt","audience","purpose","pages","animation",
              "template","language","emphasis","fidelity",
              "need_arch_diagram","need_network_topo","storyline","outdir"]:
        assert k in brief.DEFAULTS

def test_storyline_default_empty_and_preserved():
    # 没给 storyline → 默认空 dict,不报错
    m = brief.merge_with_defaults({"subject":"X","tilt":"tech"})
    assert m["storyline"] == {}
    # 给了 storyline(dict) → 原样保留(agent 在 Stage 0/2 推导填写)
    sl = {"arc":"纠偏→发现→定位→深入→战略→追问→应对→收尾",
          "peak": 6,
          "beats":[{"page":3,"role":"hook纠偏","takeaway":"别再混为一谈",
                    "from":"封面承诺","to":"关键发现"}]}
    m2 = brief.merge_with_defaults({"subject":"X","tilt":"tech","storyline":sl})
    assert m2["storyline"] == sl

def test_merge_with_defaults_fills_missing():
    ans = {"subject":"X","tilt":"tech","audience":"team"}
    m = brief.merge_with_defaults(ans)
    assert m["tilt"] == "tech"
    assert m["language"] == "zh"            # 默认
    assert m["fidelity"] == "traced"        # 默认

def test_need_arch_diagram_derived_from_tilt():
    m = brief.merge_with_defaults({"subject":"X","tilt":"tech"})
    assert m["need_arch_diagram"] is True
    m = brief.merge_with_defaults({"subject":"X","tilt":"vision"})
    assert m["need_arch_diagram"] is False
    # 用户显式覆盖优先
    m = brief.merge_with_defaults({"subject":"X","tilt":"tech","need_arch_diagram":False})
    assert m["need_arch_diagram"] is False

def test_write_and_load_roundtrip(tmp_path):
    p = str(tmp_path / "brief.yaml")
    sl = {"arc":"纠偏→发现→定位→深入→战略→追问→应对→收尾","peak":6,
          "beats":[{"page":3,"role":"hook纠偏","takeaway":"别再混为一谈"}]}
    data = brief.merge_with_defaults({"subject":"DeepSeek-V4-Flash 部署","tilt":"tech",
                                      "storyline":sl})
    brief.write_brief(data, p)
    loaded = brief.load_brief(p)
    assert loaded["subject"] == "DeepSeek-V4-Flash 部署"
    assert loaded["need_arch_diagram"] is True
    assert loaded["storyline"] == sl        # 叙事弧 dict 经 YAML 往返保留

def test_load_brief_fills_missing_field(tmp_path):
    """Global Constraint:字段缺失用默认兜底,不报错。"""
    p = str(tmp_path / "brief.yaml")
    pathguard.write_guarded(p, "subject: X\ntilt: balanced\n", inside=False)
    loaded = brief.load_brief(p)
    assert loaded["fidelity"] == "traced"   # 缺失→默认
    assert loaded["pages"] == "15-20"

def test_slugify():
    assert brief.slugify("DeepSeek-V4-Flash 部署与适配") == "deepseek-v4-flash"


# ---- stage0_brief: 把「问不问 / 问什么」封进函数,无人值守不 hang ----
# asker 注入:代表 AskUserQuestion 这个阻塞副作用。测试靠它验证「问没问、问了哪些字段」,
# 不依赖真实 AskUserQuestion(那会 hang)。stage0_brief 是纯函数 + 注入副作用。

def test_stage0_brief_non_interactive_never_asks():
    """无人值守:interactive=False 时无论缺多少字段都不调 asker,全默认直入。"""
    calls = []
    def asker(missing):
        calls.append(missing); return {}
    b = brief.stage0_brief("某技术主题", existing=None, interactive=False, asker=asker)
    assert calls == []                          # 没问
    assert b["subject"] == "某技术主题"
    assert b["audience"] == "leaders"           # 默认
    assert b["tilt"] == "balanced"
    assert b["outdir"].startswith("output/")    # 默认推导
    assert b["need_arch_diagram"] is False       # tilt 非 tech 推导

def test_stage0_brief_non_interactive_existing_wins():
    """无人值守 + 预填:existing 优先,缺失兜默认,不问。"""
    calls = []
    def asker(missing):
        calls.append(missing); return {}
    b = brief.stage0_brief("DeepSeek Harness",
        existing={"subject":"DeepSeek Harness","tilt":"tech","audience":"team","pages":"10-15"},
        interactive=False, asker=asker)
    assert calls == []
    assert b["tilt"] == "tech"                   # 预填优先
    assert b["audience"] == "team"
    assert b["pages"] == "10-15"
    assert b["language"] == "zh"                 # 缺失→默认
    assert b["need_arch_diagram"] is True        # tilt=tech 推导(预填没给这字段)

def test_stage0_brief_interactive_no_missing_never_asks():
    """交互 + 全预填:无 missing 就不问,直接返回。"""
    full = brief.merge_with_defaults({"subject":"X"})   # 14 字段全齐
    calls = []
    def asker(missing):
        calls.append(missing); return {}
    b = brief.stage0_brief("X", existing=full, interactive=True, asker=asker)
    assert calls == []
    assert b == full

def test_stage0_brief_interactive_asks_only_missing():
    """交互 + 部分预填:只对 missing 字段问,不问已填的。"""
    calls = []
    def asker(missing):
        calls.append(list(missing))
        # 假装用户回答了 missing 里的两问
        return {"audience":"customer","pages":"20+"}
    b = brief.stage0_brief("某主题",
        existing={"subject":"某主题","tilt":"vision"},   # 只预填两字段
        interactive=True, asker=asker)
    assert len(calls) == 1
    asked = set(calls[0])
    # 已填的 subject/tilt 不能被问
    assert "subject" not in asked and "tilt" not in asked
    # 缺的 audience/pages 应在 missing 里(具体轮次编排不强制,只要被问了)
    assert "audience" in asked and "pages" in asked
    # 用户答的优先 + 默认兜底其余
    assert b["audience"] == "customer"
    assert b["pages"] == "20+"
    assert b["language"] == "zh"                   # 用户没答的→默认
    assert b["need_arch_diagram"] is False         # tilt=vision 推导

def test_stage0_brief_interactive_no_asker_falls_back_to_defaults():
    """安全网:interactive=True 但 asker 没传(被 cron 调用、agent 忘传)时,
    不崩、不 hang,退回全默认——等价于无人值守。"""
    b = brief.stage0_brief("某主题", existing={"subject":"某主题"}, interactive=True, asker=None)
    assert b["subject"] == "某主题"
    assert b["audience"] == "leaders"              # 没人答→默认
    assert b["tilt"] == "balanced"

def test_stage0_brief_preserves_explicit_need_arch_diagram():
    """existing 显式给了 need_arch_diagram,不能被 tilt 推导覆盖。"""
    b = brief.stage0_brief("X",
        existing={"subject":"X","tilt":"balanced","need_arch_diagram":True},
        interactive=False, asker=lambda m: {})
    assert b["need_arch_diagram"] is True          # 显式优先,不被 tilt=balanced 推成 False

def test_stage0_brief_outdir_existing_wins():
    """existing 给了 outdir 就用,别用 subject slug 覆盖推导。"""
    b = brief.stage0_brief("某主题",
        existing={"subject":"某主题","outdir":"my/out"},
        interactive=False, asker=lambda m: {})
    assert b["outdir"] == "my/out"
    # 没给 outdir 才推导
    b2 = brief.stage0_brief("某主题", existing={"subject":"某主题"},
        interactive=False, asker=lambda m: {})
    assert "output/" in b2["outdir"]


def test_stage0_brief_zero_interaction_roundtrip(tmp_path):
    """落地清单第5项:零交互路径全默认能跑通,不 hang。
    stage0_brief(interactive=False) → write_brief → load_brief 往返,
    字段齐全、推导正确、全程不调任何 asker(=不触发 AskUserQuestion=不 hang)。"""
    calls = []
    def trap_asker(missing):
        calls.append(missing)            # 无人值守若被调,这行就是 hang 的信号
        raise AssertionError("无人值守不应调 asker,却问了: %r" % (missing,))
    b = brief.stage0_brief("DeepSeek Harness 自动简报",
                           existing=None, interactive=False, asker=trap_asker)
    # 没问 = 没 hang
    assert calls == []
    # 14 字段全齐(经 write/load 往返后仍齐)
    p = str(tmp_path / "brief.yaml")
    brief.write_brief(b, p)
    loaded = brief.load_brief(p)
    for k in ["subject","tilt","audience","purpose","pages","animation","template",
              "language","emphasis","fidelity","need_arch_diagram","need_network_topo","outdir"]:
        assert k in loaded, "roundtrip 丢失字段: %s" % k
    # 推导正确:subject 带、outdir 推导、need_arch_diagram 由 tilt(balanced)推 false
    assert loaded["subject"] == "DeepSeek Harness 自动简报"
    assert loaded["outdir"].startswith("output/")
    assert loaded["need_arch_diagram"] is False
    # 再读回去也不触发任何交互
    reloaded = brief.load_brief(p)
    assert reloaded["audience"] == "leaders"
