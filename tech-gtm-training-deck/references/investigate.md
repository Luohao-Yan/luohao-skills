# Stage 1 — Investigate (source-faithful, line-traced, no fabrication)

You are investigating a technical subject so that a leadership briefing built on
your work is **defensible under scrutiny**. The bar is higher than "sounds right":
every claim must trace to a source the reader can open. Read this before
investigating; it is the contract that makes the rest of the pipeline trustworthy.

## Three source tiers — inspect each by its nature

A subject is rarely one source. Split it by where the truth actually lives and
inspect each tier with the tool that tier demands. Declare each claim's tier in the
doc (readers weight them differently).

### Tier A — Local source code (read to line-level)
When the subject is a repo on the machine (or a vendored copy), **the code is the
ground truth**, not the marketing page.
- Read architecture docs first (`README`, `docs/architecture*`, `AGENTS.md`) to get
  the intended model, then **verify each architectural claim against the code** —
  docs drift, code doesn't.
- Cite `file_path:line` for every mechanism: `docs/architecture.zh.md:9-13`,
  `src/sandbox.ts:129`, `packages/preset/.../mount.ts:332-381`. A claim without a
  locator is a claim you haven't verified.
- Run cheap verifications a doc can't give you: `wc -l` a file before quoting its
  length, `grep` a symbol before asserting it exists, list a directory before
  describing its contents. The number you quote is the number you measured.
- When a doc and the code disagree, **the code wins** — and you say so explicitly
  in the doc (it is itself a finding).

### Tier B — Installed apps on the machine (inspect, don't assume)
When the subject is a desktop product, its installed copy is more honest than its
press coverage. Do not infer capabilities from the product name or a web screenshot.
- Locate the install dir (`Program Files`, `AppData/Local`, `AppData/Roaming`,
  `Local/Programs`), read `package.json` / version files / `exe` ProductVersion.
- For Electron apps: `app.asar` is the source — `npx asar list` or read
  `app.asar.unpacked` for the entry, deps, and skill/plugin manifests. For native
  apps (Qt/C++): read the binary's metadata and bundled config.
- Determine what's actually inside: does it contain a coding/IDE capability? Office
  editing? A chat assistant? An embedded agent harness? **Open the files, don't
  guess from the name.**
- Model backend: read the config / request domain / provider list (e.g. a
  `models.json` pointing at a gateway). Note the default vs. switchable.
- **Read-only analysis.** Never run installers, never modify the app. Only read
  files and list dirs.

### Tier C — Public info (official + cross-check, label attribution)
When tiers A/B can't reach (e.g. a product not installed, a release announcement),
use public info — but it is the **lowest-weight tier** and the most prone to the
attribution errors a leadership briefing must avoid.
- Prefer the official page (product site, company site) for *self-description*, and
  cross-check *attribution/ownership* against independent sources (encyclopedia,
  multiple outlets). A product's own page will not tell you it belongs to a rival.
- Note that JS-rendered marketing pages may fetch as near-empty (only a title) —
  don't treat a thin fetch as "no info," treat it as "needs another source."
- When public sources conflict, state the conflict and which you trust, why.

## The attribution-correction pattern (the highest-value move)

The single most common failure in tech briefings is **misattributing a product**:
"X is made by Y" when it isn't, conflating two products with similar names,
treating a third-party component as a company's in-house tech. A leadership briefing
that gets ownership wrong loses all credibility on everything else.

- Verify ownership with **on-machine evidence** (Tier B) when possible — the
  `CompanyName` in the exe metadata, the publisher in the installer signature, the
  request domain. This beats any number of articles.
- When a product embeds a third-party open-source component, **say so** —
  "Company Z's desktop agent embeds third-party Pi (v0.79.3)" is a finding; "Company
  Z built its own agent" is a fabrication if it didn't.
- Build a **one-row-per-entity ownership table** early and let it discipline the
  whole doc: columns = name / owner / form / key capability / model backend / embedded
  harness. Every later claim must be consistent with this table.
- If a market-common belief contradicts your evidence, **the evidence wins and you
  name the correction** — that correction is often the briefing's most memorable
  point.

## Parallelize investigation across independent lines, synthesize in one mind

A subject with multiple tiers or multiple products is a fan-out opportunity — but
only across **independent** lines. Dispatch parallel Explore agents, one per line:
- one reads the source code to line-level,
- one inspects each installed app,
- one chases the public-info + attribution cross-check,
- one maps the comparison subject.

**Never** split one line's argument across blind agents (don't have one agent read
a repo's intro and another its internals — the through-line is one mind's job).
When the agents return, **synthesize back into one comprehension** before writing the
doc: reconcile conflicts, deduplicate, assign tiers, build the ownership table.
The synthesis is where fabrication dies — if two agents' claims don't reconcile,
you investigate the gap, you don't paper over it.

## No fabrication — the explicit floor

If you cannot reach a tier, say **"not found / not verified / to confirm with the
user."** A labeled gap is honest; an invented fact is a lie that will surface in
front of the audience. The same applies to product capabilities you assumed but
didn't open: if you didn't read the asar, you don't know what's inside — say so.

The one thing you may draft without source is **forward-looking recommendations**
(what *we* should do) — and only as a flagged extrapolation grounded in verified
facts, never as if the source said it.

## Output of stage 1

A comprehension in your head + the **ownership table** + a per-source evidence list
(locators for tier A/B, URLs + cross-checks for tier C), with gaps explicitly
marked. This feeds Stage 2 (`references/training-doc.md`), which turns it into the
structured doc — every claim already carries its trace, so the doc can be written
without going back to investigate.
