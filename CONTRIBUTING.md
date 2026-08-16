# 贡献约定

本仓库是 Claude Code **skill 集合**,每个子目录是一个独立 skill。加新 skill 时遵循以下约定,保持集合整洁、可被 `npx skills add` 单独安装。

## 目录结构

```
luohao-skills/
├─ README.md          # 集合索引(每加一个 skill 在此加一行)
├─ LICENSE            # 根 MIT(子 skill 可自带 LICENSE,优先子级)
├─ CONTRIBUTING.md    # 本文件
└─ <skill-name>/      # 一个 skill 一个目录
    └─ SKILL.md       # 必须在子目录根,frontmatter 含 name(=目录名)+description
```

## 加一个新 skill

1. 在仓库根建 `<skill-name>/`(kebab-case,语义化短名)。
2. 放 `SKILL.md`(`name` 字段必须等于目录名)。
3. skill 内部按需放 `references/` `scripts/` `templates/` `examples/`。
4. 在根 `README.md` 的 Skills 表加一行:`| [skill-name](skill-name/) | 一句话作用 | 安装命令 |`。
5. `git add -A && git commit -m "feat: <skill-name> skill" && git push`。

## 约定

- **一个 skill 一个目录**,不嵌套,skill 之间平级互不依赖(除非 README 明示依赖,如 tech-training-deck 依赖 slide-maker)。
- **不提交运行时产物**:`render/` `extracted/` `*.deck-gates.json` `__pycache__/`(已在根 `.gitignore`)。
- **不提交企业/版权 .pptx 模板**:模板由用户自传,examples 里只放脱敏 md/build/profile。
- **提交邮箱**:用 GitHub noreply(`Luohao-Yan@users.noreply.github.com`),不暴露工作邮箱:
  `git config user.email "Luohao-Yan@users.noreply.github.com"`。
- **提交信息**:中文,`feat: / fix: / docs:` 前缀。

## 安装单个 skill

```sh
npx skills add Luohao-Yan/luohao-skills@<skill-name> -g -y
```
