---
name: editing-office-docs
description: >-
  Use when programmatically inserting, modifying, or extracting content in
  Microsoft Word .doc/.docx documents via python-docx — especially adding
  chapters/sections/tables to an existing structured Word file, working with
  legacy binary .doc, or batch edits needing visible highlight markers. Targets
  the Windows + LibreOffice toolchain and the non-obvious python-docx gotchas
  (missing Table Grid style, mandatory table width arg, insertion-order
  scramble, silent content loss) that break naive approaches. Trigger on:
  改Word/补充文档章节/往docx插表格/doc转docx/标黄修改处/审计意见补章节.
---

# Editing Office docs

程序化编辑 Word `.doc`/`.docx` 的可复用技法。核心链路是 **读 → 改 → 校验**：
用 LibreOffice 把二进制 `.doc` 转成 `.docx`，用 python-docx 在指定锚点插入
章节/段落/表格（必要时加黄色高亮标记修改处），转回 `.doc` 交付，**再从最终
交付物重新提取确认内容真的落地**。

可复用工具与踩坑详解见同目录 `scripts/docx_tools.py` 和
`references/python-docx-gotchas.md`。先读本文件建立整体认识，动手时再翻参考。

## 非协商契约：必须从最终交付物校验

**`build` 脚本打印 "saved / 完成" 不代表内容进了交付文件。** python-docx
在锚点处插段落+表格时，顺序会乱、内容会丢、样式会错——而 `.save()` 照样
成功返回，不报任何错。本 skill 的全部价值在于：**交付前，把最终 `.doc`
重新转 `.docx`、提取大纲与正文，逐条断言每个应插入片段都真实存在且顺序正确。**

这一步省掉 = 把可能内容丢失的文件交出去，还自信地说"已完成"。这是最严重
的错误，不可省。

## 何时用 / 何时不用

**用：**
- 往已有结构化 Word 文档补章节、补表格、补段落（如按审计意见补充设计说明）
- 源文件是旧版二进制 `.doc`（python-docx 读不了）
- 要把修改处用高亮标出来给人审阅
- 批量、可复现地改文档（手工改易错且不可重现）

**不用：**
- 只改几个字、调格式 → 直接 Word 手工改更快
- 纯新文档从零写 → 直接 `python-docx` 顺序构建即可，无需本 skill 的锚点插入
- 需要 Word 专属功能（复杂样式、修订模式 track-changes、目录域自动更新）
  → python-docx 不擅长，说明局限后用 Word 手工或其它工具

## 工作流

| 步骤 | 做什么 | 工具 |
|---|---|---|
| 1. 读 | `.doc` → `convert(...,'docx')` → `extract_outline` 摸清章节结构与锚点 | `docx_tools.convert/extract_outline` |
| 2. 定锚点 | 用现有章节标题文本 `find_para_exact` 定位插入位置 | `find_para_exact/contains` |
| 3. 组织 blocks | 要插的内容写成 `[('h',级别,标题),('p',正文),('table',行数据)]` | — |
| 4. 插入 | `insert_blocks_before(锚点, blocks, highlight=True)` 或 `append_blocks` | **游标法**，见下 |
| 5. 存 + 转回 | `.save()` → `convert(...,'doc')` 覆盖交付 | `convert` |
| 6. 校验 | `verify_landed(最终doc, 应有片段)` → 必须全中 | `verify_landed` |

## 最关键的几个坑（内联，详见 references）

**1. `.doc` 是二进制，python-docx 读不了。** 必须先 `convert(in,'docx',outdir)`
转成 `.docx`，改完再 `convert(...,'doc')` 转回。每次转换用独立 LibreOffice
profile（`-env:UserInstallation=...`），避免缓存冲突。

**2. 这些文档没有 `Table Grid` 样式。** `table.style = 'Table Grid'` 直接
`KeyError`。用 `set_table_borders(table)` 手动写 `w:tblBorders` 加边框。

**3. `add_table` 必须给 `width`。** 某些 python-docx 版本 `add_table(rows, cols)`
缺 `width` 位置参数会 `TypeError`。固定写 `add_table(rows=n, cols=m, width=Inches(6.5))`。

**4. 批量插入用游标法，别用逆序 addprevious。** 混合段落+表格时，"逆序
`addprevious(anchor)`" 会打乱段落与表格的相对顺序、甚至丢内容。正确做法：
首个 `anchor.addprevious(el0)`，之后 `prev.addnext(el); prev=el` 逐个接龙。
`insert_blocks_before` 已内置此法，直接用。

**5. 标题用 builtin `Heading N`。** 这类政务文档标题样式名就是 `Heading 1/2/3`，
直接 `add_paragraph(style='Heading 2')`。章节编号（如 "6.5"）写进标题文本里，
与原文 "6.4.系统安全维护" 风格一致；别指望自动编号。

**6. 高亮用 `run.font.highlight_color = WD_COLOR_INDEX.YELLOW`。** 这是 Word
荧光笔标记，不是只读保护，用户可随时取消。改过的内容逐 run 设此属性即可。

## 快速参考

| 任务 | 调用 |
|---|---|
| `.doc`→`.docx` | `docx_tools.convert(path,'docx',outdir)` |
| 提大纲 | `docx_tools.extract_outline(docx_path)` |
| 找锚点 | `find_para_exact(doc, '部署结构设计')` |
| 前插章节 | `insert_blocks_before(anchor, blocks, highlight=True)` |
| 末尾追加 | `append_blocks(doc, blocks, highlight=True)` |
| 表格加边框 | `set_table_borders(table)` |
| 转回 `.doc` | `convert(docx_path,'doc',outdir)` |
| 校验落地 | `verify_landed(final_doc, ['片段1','片段2'], work_dir)` |

blocks 元组：`('h',级别,文本)` 标题 · `('p',文本)`/`('note',文本)` 正文 ·
`('table', [[行],[行],...])` 表格（首行加粗当表头）。

## 常见错误

| 现象 | 原因 | 修法 |
|---|---|---|
| `KeyError: 'Table Grid'` | 文档无该命名样式 | `set_table_borders` |
| `add_table() missing width` | 缺 width 位置参数 | 传 `width=Inches(6.5)` |
| 插入后顺序乱/表格跑到标题前 | 用了逆序 addprevious | 用游标法 `insert_blocks_before` |
| 标题样式没生效 | 用错样式名或自定义名 | 确认是 `Heading N`，用 `extract_outline` 核对 |
| 自信"完成"实则丢内容 | 只信 `.save()` 成功 | `verify_landed` 从最终 `.doc` 复查 |
| 转换卡住/报锁 | LibreOffice profile 被占 | 每次用独立 `UserInstallation` profile |
| `.doc` 读取失败 | 当 `.docx` 直接 `Document()` | 先 `convert` 成 `.docx` |

## 局限（要如实告知用户）

- **目录不会自动更新**：python-docx 插了新章节，Word 里的目录域还是旧的。
  交付时提醒用户在 Word 里选中目录→右键→「更新域」→「更新整个目录」。
- **复杂格式会损耗**：LibreOffice 转 `.doc`→`.docx`→`.doc` 两轮可能微调
  某些格式。交付前留原始备份，便于回退。
- **不擅长 track-changes/修订模式/复杂图文混排**：这类需求说明局限后建议手工或专用工具。
- **中文标题编号**：本 skill 把编号写死在标题文本里，不依赖自动编号域。

## Install / 依赖

```bash
pip install python-docx
# .doc<->.docx 互转需 LibreOffice (soffice);纯 .docx 编辑无需
```
`scripts/docx_tools.py` 可直接 `import`，无需安装为本 skill 的一部分。
