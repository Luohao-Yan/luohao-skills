# -*- coding: utf-8 -*-
import os, tempfile
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import brief

def test_defaults_has_13_fields():
    assert len(brief.DEFAULTS) == 13
    for k in ["subject","tilt","audience","purpose","pages","animation",
              "template","language","emphasis","fidelity",
              "need_arch_diagram","need_network_topo","outdir"]:
        assert k in brief.DEFAULTS

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
    data = brief.merge_with_defaults({"subject":"DeepSeek-V4-Flash 部署","tilt":"tech"})
    brief.write_brief(data, p)
    loaded = brief.load_brief(p)
    assert loaded["subject"] == "DeepSeek-V4-Flash 部署"
    assert loaded["need_arch_diagram"] is True

def test_load_brief_fills_missing_field(tmp_path):
    """Global Constraint:字段缺失用默认兜底,不报错。"""
    p = str(tmp_path / "brief.yaml")
    with open(p,"w",encoding="utf-8") as f:
        f.write("subject: X\ntilt: balanced\n")
    loaded = brief.load_brief(p)
    assert loaded["fidelity"] == "traced"   # 缺失→默认
    assert loaded["pages"] == "15-20"

def test_slugify():
    assert brief.slugify("DeepSeek-V4-Flash 部署与适配") == "deepseek-v4-flash"
