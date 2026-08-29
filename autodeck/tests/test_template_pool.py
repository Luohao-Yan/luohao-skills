# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import template_pool

def test_resolve_explicit_path(tmp_path):
    f = tmp_path / "t.pptx"; f.write_text("x")
    assert template_pool.resolve(str(f)) == str(f)

def test_resolve_auto_returns_first_existing(monkeypatch, tmp_path):
    a = tmp_path / "a.pptx"; a.write_text("x")   # 存在
    b = tmp_path / "b.pptx"                       # 不存在
    monkeypatch.setattr(template_pool, "DEFAULT_POOL", [str(b), str(a)])
    assert template_pool.resolve("auto") == str(a)   # 跳过不存在的,取首个存在

def test_resolve_auto_none_exist(monkeypatch, tmp_path):
    monkeypatch.setattr(template_pool, "DEFAULT_POOL", [str(tmp_path/"x.pptx"), str(tmp_path/"y.pptx")])
    assert template_pool.resolve("auto") is None

def test_resolve_none_keyword(monkeypatch, tmp_path):
    a = tmp_path/"a.pptx"; a.write_text("x")
    monkeypatch.setattr(template_pool, "DEFAULT_POOL", [str(a)])
    assert template_pool.resolve("none") is None

def test_resolve_empty_like_auto(monkeypatch, tmp_path):
    a = tmp_path/"a.pptx"; a.write_text("x")
    monkeypatch.setattr(template_pool, "DEFAULT_POOL", [str(a)])
    assert template_pool.resolve("") == str(a)
