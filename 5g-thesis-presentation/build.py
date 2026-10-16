#!/usr/bin/env python3
"""Ricomponi index.html dai sorgenti. Richiede solo Python 3, senza pacchetti aggiuntivi."""
from pathlib import Path
import argparse
import html
import json
import re

ROOT = Path(__file__).resolve().parent


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def render():
    manifest = json.loads(read("slides.json"))
    total = len(manifest)
    sections, outline = [], []
    for number, item in enumerate(manifest, 1):
        fragment = read(item["file"])
        for key, value in {"N": number, "NN": f"{number:02}", "TOTAL": total}.items():
            fragment = fragment.replace("{{" + key + "}}", str(value))
        title = html.unescape(re.search(r'data-title="([^"]+)"', fragment).group(1))
        # Navigation state belongs to the assembled page, not to the source fragment.
        fragment = re.sub(r'<section\b([^>]*)>', lambda m: '<section' + m.group(1) +
                          f' data-slide-key="{html.escape(item["key"], quote=True)}"' +
                          (' aria-hidden="false"' if number == 1 else ' aria-hidden="true" hidden') + '>', fragment, count=1)
        if number == 1:
            fragment = fragment.replace('class="slide"', 'class="slide active"', 1)
        sections.append(fragment)
        outline.append(f'<li><button type="button" data-go="{number-1}"><span>{number:02}</span>{html.escape(title)}</button></li>')
    page = read("templates/page.html")
    tokens = {
        "SLIDES": "\n".join(sections),
        "OUTLINE": "\n".join(outline),
        "TOTAL": str(total),
        "DIALOGS": read("templates/dialogs.html"),
        "OPENAPI_EXAMPLE": html.escape(read("esempi/openapi-esempio.yaml").rstrip()),
        "UPF_REPORT": html.escape(read("data/reports/upf_teid_uniqueness/report.json")),
        "AMF_RULE": html.escape(read("data/regole/amf_sync_failure_case_b_sequence.dsl")),
        "RESSTAR_RULE": html.escape(read("data/regole/resstar_verification_failure.dsl")),
    }
    temporal = re.search(r'MFOTL CASE B\s+""".*?"""', read("data/regole/amf_sync_failure.dsl"), re.S)
    if temporal:
        tokens["AMF_TEMPORAL_RULE"] = html.escape(temporal.group(0) + "\n")
    # Shell tokens can introduce other tokens, so resolve them in two passes.
    for _ in range(2):
        for key, value in tokens.items():
            page = page.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if unresolved:
        raise ValueError("Segnaposto non risolti: " + ", ".join(sorted(set(unresolved))))
    return page, total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Controlla se index.html corrisponde ai sorgenti, senza riscriverlo")
    args = parser.parse_args()
    page, total = render()
    output = ROOT / "index.html"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != page:
            parser.exit(1, "index.html va ricomposto: esegui python build.py\n")
        print(f"index.html aggiornato: {total} slide.")
    else:
        output.write_text(page, encoding="utf-8")
        print(f"Creato index.html: {total} slide. Ora riaprilo o aggiorna il browser.")


if __name__ == "__main__":
    main()
