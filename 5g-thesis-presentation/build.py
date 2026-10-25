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
    }
    # Shell tokens can introduce other tokens, so resolve them in two passes.
    for _ in range(2):
        for key, value in tokens.items():
            page = page.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if unresolved:
        raise ValueError("Segnaposto non risolti: " + ", ".join(sorted(set(unresolved))))
    return page, total


def metadata():
    """Mantieni note, budget e riferimenti coerenti con l'ordine del manifest."""
    rows = []
    for number, item in enumerate(json.loads(read('slides.json')), 1):
        fragment = read(item['file'])
        title = html.unescape(re.search(r'data-title="([^"]+)"', fragment).group(1))
        seconds = int(re.search(r'data-seconds="(\d+)"', fragment).group(1))
        note = html.unescape(re.search(r'<template class="speaker-note">(.*?)</template>', fragment, re.S).group(1)).strip()
        rows.append((number, item, title, seconds, note))
    budget = sum(row[3] for row in rows)
    timing = '# Tempi indicativi — revisione finale\n\nAvanzamento manuale. Ogni divisoria ha un budget di 3 secondi. I tempi includono i passi interni.\n\n| Slide | Titolo | Tempo |\n|---:|---|---:|\n'
    timing += ''.join(f'| {n} | {title} | {sec//60}:{sec%60:02} |\n' for n, item, title, sec, note in rows)
    timing += f'\nTotale indicativo: **{budget//60}:{budget%60:02}**. Da verificare con una prova orale.\n'
    notes = '# Note del relatore — revisione finale\n\nGenerate dai sorgenti canonici. I nomi dei file storici mantengono la vecchia numerazione; l’ordine effettivo è in slides.json.\n\n'
    notes += ''.join(f'## {n}. {title}\n\n{note}\n\n' for n, item, title, sec, note in rows)
    mapping = '# Mappa delle slide\n\nGenerata da slides.json. I prefissi dei file originali restano invariati.\n\n| Slide | Chiave | Sorgente | Collegamento locale |\n|---:|---|---|---|\n'
    mapping += ''.join(f'| {n} | {item["key"]} | {item["file"]} | [Apri](index.html#slide-{n}) |\n' for n, item, title, sec, note in rows)
    return {'tempi-slide.md': timing, 'note-relatore.md': notes, 'mappa-slide.md': mapping}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Controlla se index.html corrisponde ai sorgenti, senza riscriverlo")
    args = parser.parse_args()
    page, total = render()
    outputs = {'index.html': page, **metadata()}
    if args.check:
        stale = [name for name, content in outputs.items() if not (ROOT / name).exists() or read(name) != content]
        if stale:
            parser.exit(1, ', '.join(stale) + ': esegui python build.py\n')
        print(f"HTML, note, tempi e mappa aggiornati: {total} slide.")
    else:
        for name, content in outputs.items():
            (ROOT / name).write_text(content, encoding="utf-8")
        print(f"Creati HTML, note, tempi e mappa: {total} slide. Ora riaprilo o aggiorna il browser.")


if __name__ == "__main__":
    main()

