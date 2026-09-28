#!/usr/bin/env python3
"""Normalise author names in publication pages produced by the BibTeX importer.

A Zotero export spells the same person several ways. Because `authors:` is a
Hugo taxonomy, every spelling becomes its own author page and a person's
publication list splits across them silently — the site looks fine and is
wrong. This resolves every spelling to one person using tools/author-aliases.yaml,
then decides how that person is written on the page, and optionally drops the
imported subject keywords.

How a name is written
---------------------
`canonical` in the alias file IS the published text, so what the site shows can
be read straight out of that file instead of worked out. The one exception is
a person with a profile in data/authors/, who is published under the profile's
given + family name:

    has a profile in data/authors/   ->  "Christos Manopoulos"
    everyone else                    ->  the canonical, e.g. "J.D. Kakisis"

The profile is the switch. Add data/authors/<someone>.yaml, re-run with --all,
and every paper that person appears on changes to their full name; there is
nothing to edit in the alias file when the People page grows.

A profile is matched on surname plus first initial, so it attaches to whatever
the .bib called that person. The surname for that comes from the .bib's
"Last, First" spelling in the alias file, never from the canonical: "Giuseppe
De Nisco" has a two-word surname that no last-token rule would find.

Run it after every `academic import`:

    academic import publications.bib content/research/publications/ --compact
    python tools/normalize-authors.py content/research/publications/

Only the `authors:` and `tags:` blocks are touched; the rest of each file is
left byte-for-byte alone, so re-running is safe and produces no diff once the
pages are already normalised.
"""

import argparse
import glob
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
PROFILES = os.path.join(os.path.dirname(HERE), "data", "authors")

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


def slugify(name):
    """Approximate Hugo's urlize, to check a profile's name reaches its slug."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def split_name(canonical, variants):
    """Split a canonical into (given, surname).

    The surname is read off the .bib's "Last, First" spelling, taking the
    longest one the canonical actually ends with. Nothing else knows where a
    surname starts: "Giuseppe De Nisco" would otherwise reduce to "G. Nisco",
    and "Maurizio Lodi Rizzini" to "M. Rizzini".
    """
    surname = ""
    lowered = canonical.lower()
    for variant in variants:
        if "," not in variant:
            continue
        last = variant.split(",")[0].strip()
        if last and lowered.endswith(last.lower()) and len(last) > len(surname):
            surname = last
    if not surname:
        parts = canonical.split()
        surname = parts[-1] if len(parts) > 1 else canonical
    return canonical[: len(canonical) - len(surname)].strip(), surname


def name_units(given):
    """Split a given-name field into (text, already_abbreviated) units.

        "D.P."           -> [(D, True), (P, True)]
        "Nikolaos P. E." -> [(Nikolaos, False), (P, True), (E, True)]
        "Ch.Ch."         -> [(Ch, True), (Ch, True)]     digraph, one letter
        "M.-A."          -> [(M.-A., True)]              one hyphenated name
    """
    units = []
    for token in given.split():
        if "-" in token:
            units.append((token.rstrip("."), True))
        elif "." in token:
            units.extend((piece, True) for piece in token.split(".") if piece)
        else:
            units.append((token, False))
    return units


def abbreviate(unit):
    """"Nikolaos" -> "N."   "Ch" -> "Ch."   "M.-A." -> "M.-A." """
    text, already = unit
    if "-" in text:
        return text + "."
    return (text if already else text[0]) + "."


def load_profiles(path):
    """Return ((family, initial) -> (given, family, slug), and every slug).

    Keying on family plus first initial rather than on the full name means a
    profile added later attaches to whatever the .bib calls that person — add
    "Dimitrios Sokolis" and the papers filed under "Sokolis, D.P." find it.
    """
    people, slugs = {}, set()
    for filename in sorted(glob.glob(os.path.join(path, "*.yaml"))):
        data = yaml.safe_load(io.open(filename, encoding="utf-8")) or {}
        slug = data.get("slug") or os.path.splitext(os.path.basename(filename))[0]
        slugs.add(slug)
        name = data.get("name") or {}
        given = (name.get("given") or "").strip()
        family = (name.get("family") or "").strip()
        # The starter ships placeholder profiles reading "[Given Name]".
        if not given or not family or "[" in given + family:
            continue
        if slugify(given + " " + family) != slug:
            print(f"  WARNING: {os.path.basename(filename)} names "
                  f"'{given} {family}', which does not urlize to its slug "
                  f"'{slug}'. Publications will not attach to this profile.")
        people[(family.lower(), given[0].lower())] = (given, family, slug)
    return people, slugs


def build_lookup(path, profiles):
    """Map every known spelling of a person to the one form to publish."""
    with io.open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    lookup, displays, matched = {}, {}, set()
    for person in cfg.get("people") or []:
        canonical = person["canonical"]
        variants = person.get("variants") or []
        given, surname = split_name(canonical, variants)
        units = name_units(given)

        # The canonical is the published form, so nothing is computed for the
        # common case. A profile is the one thing that overrides it, and it is
        # matched on surname plus first initial so that a profile added later
        # attaches to whatever the .bib called that person.
        profile = profiles.get(
            (surname.lower(), abbreviate(units[0])[0].lower() if units else ""))
        if profile:
            display = f"{profile[0]} {profile[1]}"
            matched.add(profile[2])
        else:
            display = canonical

        # Two people publishing under one spelling would merge on the site
        # exactly as two spellings of one person would split it.
        if display in displays and displays[display] != canonical:
            sys.exit(f"ERROR: '{displays[display]}' and '{canonical}' both "
                     f"publish as '{display}'. Give one of them a distinct "
                     f"canonical in tools/author-aliases.yaml before re-running.")
        displays[display] = canonical

        # Accept the .bib spellings, the flipped forms the importer writes and
        # the canonical, so a re-run is a no-op and editing a canonical still
        # migrates the pages published under the old one.
        forms = [canonical, display]
        for variant in variants:
            forms += [variant, flip(variant)]
        for form in forms:
            lookup[norm(form)] = display

    for key, (given, family, slug) in sorted(profiles.items()):
        if slug not in matched:
            print(f"  note: profile '{slug}' ({given} {family}) matches no "
                  f"author in the alias file; nothing to attach to it yet.")
    return lookup, bool(cfg.get("drop_imported_tags"))


def rewrite(path, lookup, drop_tags, slugs=(), unknown=None):
    with io.open(path, encoding="utf-8") as fh:
        text = fh.read()
    original = text
    changes = []

    m = re.search(BLOCK.format(key="authors"), text, re.M)
    if m:
        out, seen = [], set()
        for line in m.group(1).rstrip("\n").split("\n"):
            name = line[1:].strip().strip("'\"")
            # A hand-written page may name a profile by its slug instead of by
            # name — HugoBlox resolves that itself. Leave it exactly as found.
            if name in slugs:
                out.append("- " + name)
                seen.add(norm(name))
                continue
            canonical = lookup.get(norm(name), name)
            if norm(name) not in lookup and unknown is not None:
                unknown.setdefault(name, []).append(os.path.basename(os.path.dirname(path)))
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
    ap.add_argument("--profiles", default=PROFILES,
                    help="directory of data/authors/*.yaml profiles. Anyone "
                         "with one is published under their full name; "
                         "everyone else as an initial plus surname.")
    ap.add_argument("--only", nargs="*", help="limit to these folder names")
    ap.add_argument(
        "--all",
        action="store_true",
        help="also rewrite pages that are already committed — needed after "
        "adding a profile, since those pages predate it. Off by default so a "
        "post-import run only touches what the importer wrote. Imported tags "
        "are never dropped under this flag; curated pages live in the same "
        "directory and their tags are not the importer's to remove.",
    )
    args = ap.parse_args()

    profiles, slugs = load_profiles(args.profiles)
    lookup, drop_tags = build_lookup(args.aliases, profiles)
    print(f"{len(lookup)} name forms map to {len(set(lookup.values()))} people; "
          f"{len(profiles)} of them have a profile and keep their full name")

    # Default to the pages the import just touched. Without this the pass also
    # rewrites curated pages sitting in the same folder, which is how it
    # stripped the examples' tags the first time.
    #
    # "Touched" means added *or* modified. The first import of a paper leaves an
    # untracked folder; a re-import with --overwrite rewrites one that is
    # already committed, which git reports as modified. Matching only "??"
    # therefore misses every page that already exists.
    #
    # Adding a profile changes how an existing page reads, and those pages are
    # committed, so pass --all after editing data/authors/.
    fresh = None
    if not args.all and not args.only:
        try:
            top = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                text=True, stderr=subprocess.DEVNULL).strip()
            out = subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=all", "--", args.directory],
                text=True, stderr=subprocess.DEVNULL)
            root = os.path.abspath(args.directory)
            fresh = set()
            for line in out.splitlines():
                if not set(line[:2]) & set("?MA"):
                    continue
                # Paths are repo-relative, and quoted when they need escaping.
                path = os.path.join(top, line[3:].strip().strip('"'))
                head = os.path.relpath(path, root).replace("\\", "/").split("/")[0]
                if head not in (".", ".."):
                    fresh.add(head)
            print(f"limiting to {len(fresh)} folders the importer touched "
                  f"(pass --all to include every page)")
        except (subprocess.CalledProcessError, OSError, ValueError):
            print("could not consult git; processing every folder")

    # Dropping the imported subject keywords only makes sense for a page the
    # importer just wrote. Outside that, the run is there to restyle names —
    # after adding a profile, say — and the curated pages sitting in the same
    # directory carry hand-picked tags that are not the importer's to remove.
    # Tying this to the selection rather than to a flag means --all cannot
    # quietly strip them.
    drop_here = drop_tags and fresh is not None
    if drop_tags and not drop_here:
        print("not dropping imported tags: only pages the importer just "
              "wrote are eligible, and this run is not limited to those")

    touched = renames = 0
    unknown = {}
    for entry in sorted(os.listdir(args.directory)):
        if args.only and entry not in args.only:
            continue
        if fresh is not None and entry not in fresh:
            continue
        path = os.path.join(args.directory, entry, "index.md")
        if not os.path.isfile(path):
            continue
        changes = rewrite(path, lookup, drop_here, slugs, unknown)
        if changes:
            touched += 1
            renames += sum(1 for c in changes if "->" in c)
            print(f"  {entry}")
            for c in changes:
                print(f"      {c}")
    print(f"\n{touched} files changed, {renames} author names rewritten")

    # Anyone the alias file does not know is published exactly as the .bib
    # spelled them, so they keep a full name while everyone else is reduced,
    # and a second spelling of them would start a second author page. This is
    # the list to work through after an import brings in new co-authors. It
    # also catches a name stranded by deleting a profile: add the full name to
    # that person's `variants` and it reduces again.
    if unknown:
        print(f"\n{len(unknown)} author name(s) not in "
              f"{os.path.relpath(args.aliases)} — left exactly as found:")
        for name in sorted(unknown):
            where = unknown[name]
            shown = ", ".join(where[:3]) + (" …" if len(where) > 3 else "")
            print(f"   {name}   ({len(where)}x: {shown})")


if __name__ == "__main__":
    main()
