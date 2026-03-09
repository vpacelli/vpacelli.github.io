#!/usr/bin/env python3
"""
Convert publications.bib to data/publications.yaml for Hugo.

Usage:
    python scripts/bib2yaml.py

Reads:  publications.bib (project root)
Writes: data/publications.yaml
"""

import re
import sys
from pathlib import Path

import yaml
from pybtex.database.input import bibtex


def clean_latex(s: str) -> str:
    """Remove common LaTeX markup from a string."""
    s = s.replace("{", "").replace("}", "")
    s = s.replace("\\\"o", "ö").replace("\\\"u", "ü").replace("\\\"a", "ä")
    s = s.replace("\\&", "&")
    s = s.replace("~", " ")
    s = s.replace("\\,", ",")  # thin space -> comma (for patent numbers etc.)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)  # strip remaining commands
    return s.strip()


def format_authors(persons) -> str:
    """Format pybtex Person list into 'First Last, First Last, ...' string."""
    names = []
    for p in persons:
        first = " ".join(p.first_names + p.middle_names)
        last = " ".join(p.last_names)
        # Use first initials + last name for compactness
        # Handle hyphenated names like "Guan-Horng" -> "G.-H."
        parts = p.first_names + p.middle_names
        initial_parts = []
        for n in parts:
            if not n:
                continue
            if "-" in n:
                initial_parts.append("-".join(seg[0] + "." for seg in n.split("-") if seg))
            else:
                initial_parts.append(n[0] + ".")
        initials = " ".join(initial_parts)
        names.append(f"{initials} {last}")
    return ", ".join(names)


def entry_sort_key(entry: dict) -> tuple:
    """Sort entries: by year descending, then by first-author last name."""
    return (-entry.get("year", 0), entry.get("sort_name", ""))


def main():
    project_root = Path(__file__).resolve().parent.parent
    bib_path = project_root / "publications.bib"
    out_path = project_root / "data" / "publications.yaml"

    if not bib_path.exists():
        print(f"Error: {bib_path} not found.", file=sys.stderr)
        sys.exit(1)

    parser = bibtex.Parser()
    bib_data = parser.parse_file(str(bib_path))

    conferences = []
    journals = []
    preprints = []
    dissertations = []
    patents = []

    for key, entry in bib_data.entries.items():
        fields = entry.fields
        etype = entry.type.lower()

        persons = entry.persons.get("author", [])
        authors_str = format_authors(persons)

        rec = {
            "key": key,
            "title": clean_latex(fields.get("title", "")),
            "authors": clean_latex(authors_str),
            "year": int(fields.get("year", 0)),
            "sort_name": persons[0].last_names[0] if persons else "",
        }

        # Optional fields
        if "doi" in fields:
            rec["doi"] = f"https://doi.org/{fields['doi']}" if not fields["doi"].startswith("http") else fields["doi"]
        if "arxiv" in fields:
            rec["arxiv"] = f"https://arxiv.org/abs/{fields['arxiv']}"
        if "url" in fields:
            rec["url"] = fields["url"]
        if "note" in fields:
            rec["note"] = clean_latex(fields["note"])
        if "pages" in fields:
            rec["pages"] = fields["pages"]

        if etype == "article":
            venue_parts = [clean_latex(fields.get("journal", ""))]
            if "volume" in fields:
                venue_parts.append(f"vol. {fields['volume']}")
            if "number" in fields:
                venue_parts.append(f"no. {fields['number']}")
            if "pages" in fields:
                venue_parts.append(f"pp. {fields['pages']}")
            rec["venue"] = ", ".join(venue_parts)
            journals.append(rec)

        elif etype in ("phdthesis", "mastersthesis"):
            kind = "Ph.D. Dissertation" if etype == "phdthesis" else "M.S. Thesis"
            school = clean_latex(fields.get("school", ""))
            rec["venue"] = f"{kind}, {school}, {rec['year']}"
            dissertations.append(rec)

        elif etype == "misc" and fields.get("entrytype") == "patent":
            rec["venue"] = rec.get("note", "")
            patents.append(rec)

        elif etype == "unpublished":
            # Preprints, in-preparation, or submitted-but-no-venue papers
            # The note field carries the status (e.g., "In Preparation", "Preprint")
            rec["venue"] = rec.get("note", "Preprint")
            preprints.append(rec)

        else:  # inproceedings or fallback
            rec["venue"] = clean_latex(fields.get("booktitle", ""))
            if "pages" in fields:
                rec["venue"] += f", pp. {fields['pages']}"
            conferences.append(rec)

    # Sort each category
    conferences.sort(key=entry_sort_key)
    journals.sort(key=entry_sort_key)
    preprints.sort(key=entry_sort_key)
    dissertations.sort(key=entry_sort_key)
    patents.sort(key=entry_sort_key)

    output = {
        "conferences": conferences,
        "journals": journals,
        "preprints": preprints,
        "dissertations": dissertations,
        "patents": patents,
    }

    # Clean out sort keys before writing
    for category in output.values():
        for rec in category:
            rec.pop("sort_name", None)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    print(f"Wrote {sum(len(v) for v in output.values())} entries to {out_path}")


if __name__ == "__main__":
    main()
