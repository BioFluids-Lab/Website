#!/usr/bin/env python3
"""Normalise author names in publication pages produced by the BibTeX importer.

A Zotero export spells the same person several ways. Because `authors:` is a
Hugo taxonomy, every spelling becomes its own author page and a person's
publication list splits across them silently — the site looks fine and is
wrong. This rewrites each `authors:` entry to the one canonical spelling
declared in tools/author-aliases.yaml, and optionally drops the imported
subject keywords.

Run it after every `academic import`:

    academic import publications.bib content/research/publications/ --compact
    python tools/normalize-authors.py content/research/publications/

Only the `authors:` and `tags:` blocks are touched; the rest of each file is
left byte-for-byte alone, so re-running is safe and produces no diff once the
pages are already normalised.
"""

import argparse
import io
import os
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  python -m pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
ALIASES = os.path.join(HERE, "author-aliases.yaml")

# The importer writes a block list with the dash at column 0:
#   authors:
#   - Christos Manopoulos
#
# The space after the dash is load-bearing. Matching a bare "-" also matches
# the front matter's own closing "---" delimiter, so dropping a tags block that
# sat last would swallow the delimiter and leave an unparseable file.
BLOCK = r"^{key}:\n((?:- [^\n]*\n)+)"


def flip(name):
    """"Manopoulos, C." -> "C. Manopoulos" — the form the importer writes."""
    if "," not in name:
        return name
    last, _, first = name.partition(",")
    return " ".join((first.strip() + " " + last.strip()).split())


def norm(s):
    """Compare names ignoring case, spacing and trailing punctuation."""
    return " ".join(s.lower().replace(".", ". ").split()).rstrip(". ")


def load_aliases(path):
    with io.open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    lookup = {}
    for person in cfg.get("people") or []:
        canonical = person["canonical"]
        for variant in person.get("variants") or []:
            # Accept the .bib form and the flipped form the importer produces,
            # so the alias file stays readable as "Last, First".
            for form in (variant, flip(variant)):
                lookup[norm(form)] = canonical
        lookup[norm(canonical)] = canonical
    return lookup, bool(cfg.get("drop_imported_tags"))


def rewrite(path, lookup, drop_tags):
    with io.open(path, encoding="utf-8") as fh:
        text = fh.read()
    original = text
    changes = []

    m = re.search(BLOCK.format(key="authors"), text, re.M)
    if m:
        out, seen = [], set()
        for line in m.group(1).rstrip("\n").split("\n"):
            name = line[1:].strip().strip("'\"")
            canonical = lookup.get(norm(name), name)
            if canonical != name:
                changes.append(f"{name} -> {canonical}")
            # A merge can make one paper list the same person twice.
            if norm(canonical) not in seen:
                seen.add(norm(canonical))
                out.append("- " + canonical)
        text = text[: m.start()] + "authors:\n" + "\n".join(out) + "\n" + text[m.end() :]

    if drop_tags:
        m = re.search(BLOCK.format(key="tags"), text, re.M)
        if m:
            changes.append(f"dropped {len(m.group(1).strip().splitlines())} tags")
            text = text[: m.start()] + text[m.end() :]

    # The converter still writes a top-level `doi:`, which blox deprecated in
    # favour of a nested id map. It is only a warning today, so migrate it here
    # rather than waiting for a module bump to turn it into an error.
    m = re.search(r"^doi:[ \t]*(\S[^\n]*)\n", text, re.M)
    if m:
        changes.append("doi -> hugoblox.ids.doi")
        text = text[: m.start()] + f"hugoblox:\n  ids:\n    doi: {m.group(1)}\n" + text[m.end() :]

    if text != original:
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return changes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directory", help="directory of publication page folders")
    ap.add_argument("--aliases", default=ALIASES)
    ap.add_argument("--only", nargs="*", help="limit to these folder names")
    ap.add_argument(
        "--all",
        action="store_true",
        help="also rewrite pages that are already committed. Off by default: "
        "hand-written pages live in the same directory as imported ones, and "
        "dropping their tags would strip a curated research area.",
    )
    args = ap.parse_args()

    lookup, drop_tags = load_aliases(args.aliases)
    print(f"{len(lookup)} name forms map to {len(set(lookup.values()))} people")

    # Default to the files the import just created — anything git does not yet
    # track. Without this the pass also rewrites curated pages sitting in the
    # same folder, which is how it stripped the examples' tags the first time.
    fresh = None
    if not args.all and not args.only:
        try:
            out = subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=all", "--", args.directory],
                text=True, stderr=subprocess.DEVNULL)
            fresh = {line[3:].split("/")[3] for line in out.splitlines()
                     if line.startswith("??") and len(line[3:].split("/")) > 3}
            print(f"limiting to {len(fresh)} newly imported folders "
                  f"(pass --all to include committed pages)")
        except (subprocess.CalledProcessError, OSError, IndexError):
            print("could not consult git; processing every folder")

    touched = renames = 0
    for entry in sorted(os.listdir(args.directory)):
        if args.only and entry not in args.only:
            continue
        if fresh is not None and entry not in fresh:
            continue
        path = os.path.join(args.directory, entry, "index.md")
        if not os.path.isfile(path):
            continue
        changes = rewrite(path, lookup, drop_tags)
        if changes:
            touched += 1
            renames += sum(1 for c in changes if "->" in c)
            print(f"  {entry}")
            for c in changes:
                print(f"      {c}")
    print(f"\n{touched} files changed, {renames} author names rewritten")


if __name__ == "__main__":
    main()
