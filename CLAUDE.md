# Biofluid Mechanics & Biomedical Technology — lab website

Hugo site for the Laboratory of Biofluid Mechanics & Biomedical Technology,
School of Mechanical Engineering, NTUA. Built on the **HugoBlox** academic-cv
starter (Hugo Modules, `go.mod`), with a custom design called **Flow Plate**.

Live: <https://biofluids-lab.github.io/Website/> — currently still the stock
starter. The design lives on `design/flow-plate` and has not been merged.

```
pnpm dev          # dev server, usually http://localhost:1313
hugo --minify     # production build; expect 0 warnings, 0 errors
```

## The one rule that matters

**Add; never override.** ~80% of the design is reachable through data and
config. The rest is done by adding blocks under names HugoBlox does not ship,
so a module upgrade cannot collide with any of it.

The four sanctioned extension points, all used here:

| Where | What it does |
|---|---|
| `data/themes/biofluids.yaml`, `data/fonts/biofluids.yaml` | palette and type as *packs*; project `data/` merges over the module's |
| `config/_default/params.yaml` | selects those packs, plus `layout.radius/spacing`, `header.theme_picker` |
| `assets/css/custom.css` | official hook, read by `site_head.html` via `fileExists` |
| `layouts/_partials/hooks/head-end/` | collected by `functions/get_hook.html` |

Blocks resolve as `_partials/hbx/blocks/<type>/block.html`, and Hugo checks
project layouts before the module. The seventeen `bf-*` blocks use names
HugoBlox never ships, so they are collision-proof. **Adding a new `bf-*` name
is safe. Overriding a name HugoBlox ships is a permanent fork.**

### The one deliberate exception

`layouts/authors/term.html` **shadows** a shipped file. The author page has no
data or config route, so there was no other way to stop it rendering news and
funding items as big cards. It is kept to a single leaf layout depending on one
module function (`get_author_profile`) plus `hugo.Data.authors`. If a module
bump breaks it, that is the file to look at.

## Constraints from the lab

- **Bilingual later.** A Greek version is planned. This already rules out most
  display faces: Commissioner, Source Serif 4 and JetBrains Mono all carry
  Greek. The stock `academic` pack's Lora does **not** — Greek headings there
  fell back silently to a system serif, which is a latent bug in the starter,
  not something this redesign introduced.
- **Stay close to HugoBlox** so updates stay easy. Hence the rule above.
- **Imagery is poor quality.** That is why every image is a framed, captioned
  *plate* rather than a full-bleed hero — uneven source material then reads as
  one deliberate set.

## Design vocabulary

Tokens and components live in `assets/css/custom.css`, all prefixed `--bf-` /
`.bf-`. Colour comes from a velocity colourmap: ink → petrol → teal → sand →
rust. Sections alternate paper and tint bands instead of using rules.

Explicit user preferences, learned by correction — do not reintroduce:

- No ordinal numbering anywhere (no § marks, no "Fig. N")
- No horizontal rules between sections; alternate tint instead
- No small rust/orange squares as section marks
- No mono keyword eyebrows above card or project titles
- No keyword chips on the People list

## Landmines

Each of these cost real debugging time.

- **`.Section` only resolves to the top-level content directory.** Nested
  collections must filter by tag or front-matter field, never by section.
- **`parse_block_v3` labels every wrapper section `blox-_`**, not
  `blox-<blockname>`. A selector like `section[class*="blox-bf-"]` matches
  nothing. **This is currently an open bug** — see below.
- **Go's `html/template` will not build a tag name from a variable.** It
  escapes the whole construct to visible text. Use two literal branches.
- **`functions/get_author_name` takes a page, not a slug**, and returns only
  the first author. Use `functions/get_author_profile`, which takes a slug and
  returns `.has_data` — true only for slugs with a `data/authors/` profile,
  which is exactly the lab-member / external-co-author distinction.
- **`/authors/<slug>/` is a taxonomy term page.** Hugo only creates one when
  some content names that slug in its front matter, so People cards linked to
  404s. `content/authors/<slug>/_index.md` stubs force them into existence; the
  profile data still lives in `data/authors/`.
- **`requestAnimationFrame` never runs in a background tab.** The flow-field
  canvases are warmed 300 steps before the loop starts, which also fixes first
  paint and reduced-motion.
- **Canvas: stroke once per colour bucket, not once per particle.** Per-particle
  stroking was >1000 draw calls a frame and dropped the renderer to 0 fps.

## Publications

A publication is a page that declares `publication_types` — *not* one tagged
`Publication`. The BibTeX importer emits the former and never the latter, so
filtering on the tag silently hid every imported paper.

`authors:` is a taxonomy, so the same person spelled two ways gets two pages
and a split publication list. Always run the normaliser after an import:

```
academic import publications.bib content/research/publications/ --compact
python tools/normalize-authors.py content/research/publications/
```

`publications.bib` belongs at the **repo root** for `.github/workflows/import-publications.yml`
to pick it up (that workflow imports to `content/research/publications/`, which
was corrected from the starter's `content/publications/`).

## Open decisions

- **`.hbb-section` padding.** Because of the `blox-_` landmine, every `bf-*`
  block gets 64px of theme padding *on top of* its own spacing, site-wide. The
  fix is `section.hbb-section:has(.bf-block)`, but it tightens spacing on every
  page — deliberately not applied without a look first.
- **`team-showcase` on `/people/`** is stock: rounded corners, shadows, white
  cards. It is the one page that does not match the design. A `bf-people` block
  would fix it.
- **External co-authors** each get a thin author page. HugoBlox's own
  convention, but it scales badly with real papers.
- Content is still placeholder throughout: names, bios, projects, equipment,
  partners and logos, course codes, the NTUA room and map coordinates
  (`TODO` in `params.yaml`), and the lab email. Contact details in
  `data/authors/` read `TODO` — `grep -rn TODO data/authors/`.

## Conventions

- Commits carry no Claude attribution (`attribution` in `~/.claude/settings.json`).
- Work happens on `design/flow-plate`. Pushing `main` triggers `deploy.yml` and
  republishes the live site.
