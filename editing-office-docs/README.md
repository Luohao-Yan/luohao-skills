# editing-office-docs

程序化编辑 Word `.doc`/`.docx` 文档的 skill：读 → 改 → 校验。
封装在政务文档补充场景里踩过坑、验证过的 python-docx + LibreOffice 用法。

## 能做什么

- 把旧版二进制 `.doc` 转成 `.docx` 编辑、再转回 `.doc` 交付
- 在已有结构化 Word 文档的指定章节锚点前/后插入新章节、段落、表格
- 给修改处加黄色高亮，方便人工审阅
- 端到端校验：从最终交付的 `.doc` 重新提取，确认内容真的落地（不轻信 `.save()` 成功）

## 安装

```bash
npx skills add Luohao-Yan/luohao-skills@editing-office-docs -g -y
```

## 依赖

```bash
pip install python-docx
# .doc <-> .docx 互转需要 LibreOffice (soffice);纯 .docx 编辑无需
```

- [python-docx](https://python-docx.readthedocs.io/)
- [LibreOffice](https://www.libreoffice.org/)（仅格式互转时需要）

## 内容

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 主参考：触发条件、工作流、关键坑摘要、快速参考 |
| `scripts/docx_tools.py` | 可复用工具（convert/extract_outline/find_para/insert_blocks/set_table_borders/highlight/verify_landed） |
| `scripts/_smoke_test.py` | 工具冒烟测试（建docx→插入→校验，证明可独立运行） |
| `references/python-docx-gotchas.md` | 8 个踩坑的真实报错与修法详解 |

## 用例

按审计意见往《软件详细设计说明书》补"微服务架构设计""内部服务间接口""系统安全设计"
三章，源文件是 `.doc`，补完要标黄给审阅方看，并确认内容进了交付文件——正是本 skill 的典型场景。
