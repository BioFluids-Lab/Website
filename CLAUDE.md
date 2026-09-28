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
- **A `team-showcase` block naming a group nothing uses renders nothing**, with
  no warning. `/people/` and the homepage each list `user_groups` by name; they
  have to match the `user_groups` in `data/authors/*.yaml`. Removing
  Postdoctoral Researchers from `/people/` left the homepage still asking for
  it, quietly showing three cards in a four-column row.
- **Profiles sort by `weight`, not surname.** Professors, Staff and PhD
  Students all carry `sort_by: weight` so Manopoulos leads and the students
  keep the order the lab gave. A new profile with no `weight` sorts to the
  *top* of its group.
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
was corrected from the starter's `content/publications/`). The workflow now runs
the normaliser itself, between the import and the PR — pushing a new `.bib` to
`main` is enough; the two commands above are only for importing locally.

**`academic import` skips a folder that already exists** unless you pass
`--overwrite`. So a re-import only adds new papers; correcting an entry in the
`.bib` will *not* update the page already built from it, in CI or locally.

The normaliser defaults to the pages the importer *touched*, added or modified.
It once matched only untracked (`??`) paths. That was survivable while the
importer only ever adds folders, but it silently normalises nothing the moment
anyone passes `--overwrite`, or re-runs it locally over committed pages.

### What the committed .bib is not

A fresh Scopus export is not what is in the repo, and re-exporting over it
undoes two deliberate passes:

- **URLs point at `https://doi.org/<doi>`**, not at Scopus. 159 were rewritten;
  23 entries keep a Scopus link only because they have no DOI. Percent-encode
  the DOI into the URL — five Wiley SICI DOIs carry `<`, `>` or `#`, and a raw
  `#` truncates the URL into a 404.
- **Titles are sentence case with no trailing full stop.** Scopus exports
  Title Case, sometimes ALL CAPS. Which words keep a capital was settled from
  the corpus — the abstracts are prose, so a word's mid-sentence form there
  says whether it is ordinary, a name or an acronym.

Re-export when you need new papers or fresh abstracts, then redo both passes
before committing.

### How an author's name is written

**`canonical` in `author-aliases.yaml` is the published name.** What the site
shows is read straight out of that file, not derived. The one exception is a
person with a `data/authors/<slug>.yaml`, who is published under the profile's
given + family name instead — so a profile is the switch that shows someone in
full. Add one and re-run **with `--all`** (their pages are already committed, so
the default "only what the importer touched" filter would skip them).

A profile attaches by matching surname plus first initial, so it finds whoever
the `.bib` called that person. The surname for that comes from the `Last, First`
variant, never from the canonical: `De Nisco, Giuseppe` has a two-word surname
that no last-token rule would find. **Every person needs at least one
`Last, First` variant**, and variants must keep the `.bib`'s exact spelling,
mistakes included — they are what the importer's output is matched against.

Editing a canonical migrates the pages published under the old one, as long as
the old one is still a variant flip. When it is not — a rename to something the
`.bib` never said, or a deleted profile stranding a full name — add the retired
form to that person's `variants`. The normaliser prints every name it does not
recognise at the end of a run, which is how you find one; that list is also the
to-do list after an import brings in new co-authors.

An `authors:` entry that is a profile *slug* rather than a name (the starter's
example pages do this) is left untouched — HugoBlox resolves it itself.

Two people can share a surname. `Chrimatopoulos G.T./C.T.` and
`Stamatelopoulos S.F./K.S.` each appear on the *same paper*, as do
`Tsangaris S./G.` — six such pairs were checked and deliberately left unmerged,
each noted on its own entry in `author-aliases.yaml`. Two spellings of
`Theodorakopoulos` carry a **Greek capital iota** (U+0399) where a Latin I
belongs — the canonical is corrected, but the variants must keep the Greek
character or they match nothing.

## Theses

`theses.bib` sits at the repo root beside `publications.bib`: 196 completed
theses from Zotero, 156 diploma, 17 MSc, 23 doctoral, 1982–2026. Nothing in
progress is recorded there — the page's ongoing rows are hand-written.

**It is not wired to anything yet.** `content/theses/_index.md` still carries
twelve invented placeholder rows inline in its `bf-rows` block.

**`academic import` cannot be used for it** — tested, not assumed. It keeps
title, author, year and keywords, and discards `type` and `note`, which is
where the level and the supervisor live. The route is a script producing
`data/theses.yaml`, plus an optional `data:` key on `bf-rows` so the block
reads site data instead of an inline list.

The field contract, all of it reproducible from Zotero so a re-export does not
undo it:

| BibTeX | Zotero field | Carries |
|---|---|---|
| `type` | Type | `Diploma thesis` / `MSc thesis` / `PhD thesis` |
| `url`, `doi` | URL, DOI | the DSpace@NTUA permalink (109 of 196 have one) |
| `note` | Extra | `Key: value` lines, one block |

`author` and `title` hold the **Greek** name and title — the record as the
university holds it, and what the Greek pages will show. `Author-EN` and
`Title-EN` in the note are what the English pages read, alongside `Supervisor`
and `Research area`; everything below those lines is provenance and is never
rendered. 52 English titles come from DSpace and 144 are translations; 20
names had no Latin form on record. Each says which in its own `-source` line.

Zotero's own export was unusable: every entry typed `@phdthesis` because Type
was empty, the real values split across up to ten repeated `annote` fields
(not valid BibTeX), and the advisor sitting in `keywords`, where a Greek name
split on its own comma into two tags.

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
- **The people are real; everything about them is not.** Ten profiles across
  Professors, Staff and PhD Students, plus the publication record behind them.
  Their bios, contact details, ORCID and LinkedIn are all `TODO`, and the
  interests were read off each person's own papers rather than supplied —
  `grep -rn TODO data/authors/`. Four starter placeholders are kept on purpose
  so the MSc and Alumni groups still render.
- **Projects, theses and lab notes are invented.** Six project cards, twelve
  thesis rows and three homepage news items are written inline in page front
  matter and read as real. They are not labelled as examples, unlike the
  starter's `Example: …` pages, which is the more dangerous of the two.
- Still placeholder: equipment, partners and logos, course codes, the NTUA
  room and map coordinates (`TODO` in `params.yaml`), and the lab email.
- `/news/` has three items, all of them examples.

## Conventions

- Commits carry no Claude attribution (`attribution` in `~/.claude/settings.json`).
- Work happens on `design/flow-plate`. Pushing `main` triggers `deploy.yml` and
  republishes the live site.
