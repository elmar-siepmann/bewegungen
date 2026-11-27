"""Kopiert die Schuelerfassungen der Arbeitsblaetter (Linie S) ins Repository.

Quelle:  Modulordner Bewegung-Simulation im Google Drive (S*.pdf)
Ziel:    content/arbeitsblaetter/

Kopiert werden nur Schuelerfassungen als PDF, nie *-Lehrer.pdf und nie .tex
(die .tex-Dateien enthalten auch die Loesungen). PDFs im Ziel, die es in der
Quelle nicht mehr gibt, werden geloescht.

Aufruf:  python arbeitsblaetter_kopieren.py   (danach committen und pushen)
"""

import filecmp
import shutil
import sys
from pathlib import Path

MODUL = Path("Schule/FK-Mathe/Begabtenförderung/Material/Module/Bewegung-Simulation")
KANDIDATEN = [
    Path.home() / "Google Drive" / MODUL,   # Rechner 1
    Path("G:/Meine Ablage") / MODUL,        # Rechner 2 (Google Drive als Laufwerk)
]
ZIEL = Path(__file__).resolve().parent / "content" / "arbeitsblaetter"


def main():
    quelle = next((k for k in KANDIDATEN if k.is_dir()), None)
    if quelle is None:
        sys.exit("Modulordner nicht gefunden. Gesucht in:\n  " + "\n  ".join(map(str, KANDIDATEN)))

    pdfs = sorted(p for p in quelle.glob("S*.pdf") if not p.stem.endswith("-Lehrer"))
    for p in pdfs:   # zur Sicherheit: zu jedem Blatt muss es eine Lehrerfassung geben
        if not (quelle / f"{p.stem}-Lehrer.tex").exists():
            sys.exit(f"Abbruch: {p.name} hat keine Lehrerfassung. Ist das wirklich eine Schuelerfassung?")

    ZIEL.mkdir(parents=True, exist_ok=True)
    for p in pdfs:
        z = ZIEL / p.name
        if z.exists() and filecmp.cmp(p, z, shallow=False):
            continue
        shutil.copy2(p, z)
        print("kopiert:", p.name)

    namen = {p.name for p in pdfs}
    for z in ZIEL.glob("*.pdf"):
        if z.name not in namen:
            z.unlink()
            print("geloescht:", z.name)
    print("fertig,", len(pdfs), "Arbeitsblaetter in", ZIEL)


if __name__ == "__main__":
    main()
