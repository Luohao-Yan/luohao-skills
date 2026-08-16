# python-docx / LibreOffice 踩坑详解

每条都是真实撞过、修过的坑，附原报错与修法。SKILL.md 内联了摘要，这里是细节。

---

## 0. 总根源：`.save()` 成功 ≠ 内容正确

python-docx 的 `.save()` 只把内存里的 XML 树写盘，**不管你插入的元素顺序对不对、有没有丢、样式名存不存在**——错了它照样返回，不抛异常。

所以本 skill 的核心纪律是：**交付前从最终 `.doc` 重新转出、提取、断言**。
不要把"脚本跑完没报错"当成"内容进文档了"。下面的坑 1–4 都会被 `.save()` 默默吞掉，只有第 6 步校验能逮住。

---

## 1. `.doc` 是二进制，python-docx 直接读会失败

```
>>> Document('xxx.doc')
zipfile.BadZipFile: File is not a zip file
```

`.doc`（Word 97-2003）是 OLE 复合二进制，不是 OOXML。python-docx 只能读 `.docx`（zip 包）。

**修法**：LibreOffice headless 转。
```python
docx_path = convert('xxx.doc', 'docx', outdir)   # docx_tools.convert
d = Document(docx_path)
# ... 改 ...
convert(docx_path, 'doc', outdir)                # 转回 .doc
```

转换命令要点：
- 加 `--headless`，否则可能弹 GUI 卡住。
- 每次用独立 `-env:UserInstallation=file:///.../tmp/<profile>`，否则同一 profile 被占会报"另一个实例在运行"或静默失败。
- `--outdir` 指定输出目录，输出文件名 = 源名 + 目标后缀。
- 转换是同步阻塞，给足 timeout（大文档几十秒）。

---

## 2. `Table Grid` 样式不存在 → KeyError

```
table.style = 'Table Grid'
KeyError: "no style with name 'Table Grid'"
```

很多政务/企业 `.doc` 转出来的 `.docx` **没有定义任何命名表格样式**，现有表格的 `table.style` 是 `None`（边框直接写在表格属性上，不靠样式）。

**修法**：手动给表格写 `w:tblBorders`，不依赖样式名。
```python
def set_table_borders(table, color='000000', sz='4'):
    tbl = table._element
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr'); tbl.insert(0, tblPr)
    old = tblPr.find(qn('w:tblBorders'))
    if old is not None: tblPr.remove(old)
    borders = OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        e = OxmlElement(f'w:{edge}')
        e.set(qn('w:val'),'single'); e.set(qn('w:sz'),sz)
        e.set(qn('w:space'),'0'); e.set(qn('w:color'),color)
        borders.append(e)
    tblPr.append(borders)
```
`docx_tools.set_table_borders` 即此实现。

---

## 3. `add_table` 缺 width → TypeError

```
t = doc.add_table(rows=3, cols=2)
TypeError: BlockItemContainer.add_table() missing 1 required positional argument: 'width'
```

某些 python-docx 版本（含 1.2.0 在无默认表格宽度的文档上）`width` 是必填位置参数，不给就抛错。

**修法**：固定传 `width=Inches(6.5)`。
```python
t = doc.add_table(rows=len(rows), cols=len(rows[0]), width=Inches(6.5))
```

---

## 4. 批量插入顺序乱 / 丢内容（最隐蔽）

### 错误做法：逆序 `addprevious`

```python
created = [make(b) for b in blocks]      # 都先 add 到文档末尾
for el in reversed(created):
    anchor.addprevious(el)              # ❌ 乱序+丢内容
```

直觉上"逆序 addprevious"该得到正序，但实测混合**段落 + 表格**时：
- 段落和表格的相对顺序会错乱（标题跑到正文后、表格跑到标题前）；
- 严重时整段 blocks 只剩一个标题，正文和表格丢失。

原因：`addprevious` 把元素插到 anchor 正前方，多个元素依次插入时，
python-docx 对段落与表格元素的相对定位处理不一致，逆序无法保证稳定正序。

### 正确做法：游标法（cursor chaining）

```python
created = [make(b) for b in blocks]
anchor.addprevious(created[0])           # 首个插到 anchor 前
prev = created[0]
for el in created[1:]:                  # 之后每个接在 prev 之后
    prev.addnext(el)
    prev = el
```

首个 `addprevious`，后续 `addnext` 接龙，顺序天然正确，不丢内容。
`docx_tools.insert_blocks_before` 已内置此法。

### 末尾追加
`add_paragraph` / `add_table` 本身就追加到 body 末尾（sectPr 前），顺序天然正确，
无需移动。用 `append_blocks` 即可。

---

## 5. 标题样式名

这类文档的标题用 builtin `Heading 1/2/3`（不是中文"标题 1"也不是自定义名）：
```python
p = doc.add_paragraph(style='Heading 2')
p.add_run('6.5 系统安全设计')
```

- 章节编号（"6.5"）直接写进标题文本，与原文 `6.4.系统安全维护` 风格一致；
  别指望自动编号——这些文档的标题样式未必挂了 numbering。
- 拿不准样式名时，先 `extract_outline(path)` 看现有标题用的什么级别，照抄。
- `find_para_exact` 用**完整标题文本**（含编号）做锚点最稳，如 `'部署结构设计'`、`'5.数据库设计'`。

---

## 6. 高亮修改处

Word 的"文字突出显示"（荧光笔）：
```python
from docx.enum.text import WD_COLOR_INDEX
for r in paragraph.runs:
    r.font.highlight_color = WD_COLOR_INDEX.YELLOW
```
- 是标记、不是保护，用户可随时选中→取消高亮。
- 表格单元格：遍历 `cell.paragraphs` 的 runs 设同样属性。
- 标题段也能标黄，方便审阅定位。
- `docx_tools.highlight_runs` / `highlight_table` 已封装。

---

## 7. 端到端校验（非协商）

```python
ok, missing = verify_landed('最终.doc', ['6.5 系统安全设计','接口1：OA 公文入库', ...], work_dir)
assert ok, f'未落地: {missing}'
```

`verify_landed` 把最终 `.doc` 重新转 `.docx`，`has_text` 在段落+表格里逐片段搜索。
**任何片段 missing 都说明内容没进交付物**，必须修，不能放过。

校验还可加顺序断言：用 `iter_blocks(doc)` 拿真实块顺序，断言"新章节在锚点前"
"接口1 在接口2 前"等，逮住坑 4 的乱序。

---

## 8. 其它小坑

- **图片/E-R 图**：`doc.inline_shapes` 只数行内图；浮动图要数 `w:drawing` 元素。
  同一图被多次引用时 media 文件只有 1 个但 `w:drawing` 有多个，属正常。
- **`.doc` 转换后体积变化**：`doc→docx→doc` 两轮可能让体积从 2.6MB 变 1.6MB，
  属 LibreOffice 重压缩，内容不丢。留原始备份便于回退。
- **目录域不更新**：python-docx 不会刷新 TOC。交付提醒用户在 Word 里
  选中目录→右键→「更新域」→「更新整个目录」。
- **并发转换**：同一 LibreOffice profile 被两个进程占用会失败。`convert` 用
  独立 `UserInstallation` profile 规避。
