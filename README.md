# luohao-skills

我的 Claude Code skill 集合。每个子目录是一个独立 skill,各自带 `SKILL.md`。

## Skills

| Skill | 作用 | 安装 |
|---|---|---|
| [tech-training-deck](tech-training-deck/) | 技术主题 → 给领导培训材料(调研→培训md→模板品牌PPT)一条龙 | `npx skills add Luohao-Yan/luohao-skills@tech-training-deck -g -y` |

> 安装单个 skill: `npx skills add Luohao-Yan/luohao-skills@<skill名> -g -y`

## 目录约定

- 每个 skill 一个子目录,根目录放 `SKILL.md`。
- 子目录内可有 `references/` `scripts/` `templates/` `examples/` 等。
- 单 skill 依赖(如 tech-training-deck 依赖 [slide-maker](https://github.com/addsumtech/slides_maker))在各 skill 的 README 里说明。
