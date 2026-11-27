# WP2-Kurs Klasse 9: Bewegungen mit Folgen und Python

## Kontext
- Wahlpflichtkurs (WP2), Jahrgang 9, sehr motivierte Schüler.
- Vorwissen: Folgen, Differenzenfolgen, Summenfolgen. Newton wird im Kurs erst eingeführt. Keine Taylorreihen, keine Differential- oder Integralrechnung.
- Ziel ist kein Python-Kurs, sondern Bewegungen analysieren und simulieren. Python ist Werkzeug.
- Schüler arbeiten auf iPads im Browser mit JupyterLite (numpy, matplotlib).

## Bezug zur Begabtenförderung
- Der Kurs ist zugleich Modul „Linie S: Bewegung und Simulation“ der Begabtenförderung Mathematik (Ordner `G:\Meine Ablage\Schule\FK-Mathe\Begabtenförderung`, dort `Material/Module/Bewegung-Simulation` und die dortige CLAUDE.md).
- Zu jeder Lerneinheit sollen dort zusätzlich Arbeitsblätter (LaTeX) entstehen: Rechnungen von Hand, Begründungen, Sicherung, Lösungen. Lösungen nie in dieses öffentliche Repository.
- Notebooks in diesem Repository bleiben die einzige Fassung der Notebooks.
- **Arbeitsblätter online (seit 27.11.2026):** Die Schülerfassungen (PDF) liegen in `content/arbeitsblaetter/` und erscheinen im Dateibrowser. **Nach jeder Änderung an einem Arbeitsblatt der Linie S immer automatisch** (Anweisung des Nutzers): Blatt im Drive neu setzen, dann `python arbeitsblaetter_kopieren.py` im Repo-Hauptordner, committen, pushen. Das Skript kopiert nur `S*.pdf` ohne `-Lehrer` (nie .tex, die enthalten die Lösungen), löscht PDFs, die es im Drive nicht mehr gibt, und findet den Drive-Ordner auf beiden Rechnern.
- **Rechte:** Die README stellt klar: Material in `content/` © Elmar Siepmann, alle Rechte vorbehalten, Schüler dürfen es für den Unterricht nutzen; `LICENSE` (BSD, Project Jupyter) gilt nur für den Code der Vorlage. Bewusst keine offene Lizenz (Nutzer: „so, dass ich keinen Stress bekommen kann“).
- **Aufgeräumt am 27.11.2026:** Demo-Dateien der Vorlage (javascript, p5, python, `pyodide/`, Demo-Daten), die frühe Skizze `folge.ipynb` und die Übergangslösung `animation_kopieren.ipynb` sind gelöscht. In `content/` liegen nur noch die Kursnotebooks 01–07, `animation.py`, `data/` und `arbeitsblaetter/`.

## Technische Umsetzung
- Eigene JupyterLite-Seite auf GitHub Pages, erstellt aus der Vorlage `jupyterlite/demo`. Notebooks und CSV-Dateien liegen im Ordner `content/` und werden automatisch per GitHub Actions gebaut und veröffentlicht.
- Verwaltung durch den Lehrer in VS Code (Jupyter-Erweiterung, Git: Commit + Push).
- Die Seite ist öffentlich: nur Arbeitsmaterial, keine Schülerdaten.
- Änderungen der Schüler werden nur in ihrem Browser gespeichert; Vorlagen bleiben unverändert. Schüler sollen wichtige Notebooks als .ipynb herunterladen.
- Geänderte Notebooks erreichen Schüler nicht, die das Notebook schon geöffnet oder bearbeitet haben: JupyterLite legt eine Kopie im Browser (IndexedDB) an und gleicht sie nicht mit dem Server ab. Neue Dateien erscheinen dagegen bei allen. **Seit 24.11.2026:** Geänderte Notebooks unter demselben Namen hochladen. Die Schüler löschen ihre Kopie mit dem Knopf „Löschen“ im Dateibrowser (aus `overrides.json`) und laden die Seite neu; vorher bei Bedarf ihre Fassung als .ipynb herunterladen. Früher wurde stattdessen umbenannt (`03_fibonacci_neu`, `06_simulieren_neu`); diese Namen bleiben, neue `_neu`-Dateien sind nicht mehr nötig.
- Vor dem Commit alle Zellausgaben aus den Notebooks löschen (VS Code: „Alle Ausgaben löschen"). Sonst sehen die Schüler Ausgaben und Diagramme vom Testlauf.
- Jedes Notebook auch in der fertigen JupyterLite-Seite testen (Pyodide verhält sich anders bei `input()`, Animationen, `time.sleep`, Dateipfaden).
- **Gelöst (24.11.2026): Einzelnes Notebook auf dem iPad löschen.** Bisher löschen die Schüler über Hilfe die kompletten Browserdaten; Umbenennen (`_neu`) wird auf Dauer unübersichtlich. Der Nutzer will eine vernünftige Lösung. Idee 1, noch zu testen: Datei im Dateibrowser antippen, View → Activate Command Palette → „Delete“, Seite neu laden; dann sollte die Server-Fassung wieder erscheinen. Geht über den Speicher des Dateibrowsers, nicht über den Python-Kern. Ergebnis: Die Befehlspalette bietet das Löschen von Dateien nicht an (nur Delete Cell, Delete Workspace); „Reload Notebook from Disk“ lädt vermutlich nur die Kopie im Browser. Deshalb seit 24.11.2026 `overrides.json` im Hauptordner (wird von `jupyter lite build` automatisch übernommen): Knopf „Löschen“ (`filebrowser:delete`) in der Werkzeugleiste des Dateibrowsers, ergänzt die Standardknöpfe (Zusammenführung nach Namen). **Getestet am 24.11.2026 (PC und iPad): Der Knopf erscheint, das Löschen funktioniert** (auf dem iPad steht der Knopf in einer zweiten Zeile, unproblematisch). Ablauf für Schüler: eigene Fassung bei Bedarf herunterladen, Notebook im Dateibrowser antippen, „Löschen“, Seite neu laden. Danach erscheint wieder die Server-Fassung (vom Nutzer bestätigt). **Umbenennungen mit `_neu` sind deshalb künftig unnötig.** Verworfen: Reparatur-Notebook mit Python, weil der Kern auf iPads keine Dateien sieht (Imports scheiterten).
- CSV einlesen immer mit Notlösung (seit 20.11.2026: Auf einem iPad fand der Kernel trotz normalem Safari und mehrfachem Neuladen keine Datei aus `data/`). Den Dateinamen als Variable schreiben, damit Schüler nur eine Zeile ändern müssen:
  ```python
  datei = "feder.csv"
  try:
      t, s = np.loadtxt("data/" + datei, delimiter=",", skiprows=1, unpack=True)
  except OSError:   # Notlösung: Datei direkt von der Webseite laden
      from pyodide.http import open_url
      t, s = np.loadtxt(open_url("https://elmar-siepmann.github.io/bewegungen/files/data/" + datei), delimiter=",", skiprows=1, unpack=True)
  ```
- **Animation** (seit 24.11.2026): `content/animation.py` mit `animiere(t, s, art="feder"|"fall"|"wurf", zeitlupe=1)`. Seit 24.11.2026 auch in der Ebene: `animiere(t, x, y, ziel=(x, y))`; die Funktion erkennt am dritten Argument selbst, was gemeint ist (Liste = Ebene, Text = art). In der Ebene gleicher Maßstab auf beiden Achsen, Bildhöhe passt sich an, Boden bei y = 0, wenn alle y ≥ 0, sonst Achsen durch 0; `ziel` markiert einen Punkt (Korb). Gedacht für S6 (Wurf) und S7 (Planeten). Nimmt Listen oder Arrays. Ein HTML-Canvas mit JavaScript (kein matplotlib, weil Pyodide sonst jedes Bild einzeln rendert): links der Körper, rechts das mitwachsende s-t-Diagramm auf gleicher Höhe, Abspielen in echter Zeit ohne Glätten (jedes Bild = ein Zeitschritt, grobes dt ruckelt sichtbar). Bei „fall“ zeigt s nach unten. In `06_simulieren_neu` ist sie fest eingebaut (Import mit Notlösung in der ersten Codezelle, nach jeder Simulation eine 🎬-Zelle).
- Format der CSV-Dateien: Komma als Trenner, eine Kopfzeile. Achtung: deutsche CSV-Dateien nutzen oft Semikolon und Dezimalkomma; Export mit Dezimalpunkt verwenden (z. B. in phyphox wählbar).

## Konventionen für Notebooks
- Sprache: Deutsch, Niveau Klasse 9.
- **Versionsdatum** (seit 24.11.2026, Wunsch des Nutzers): In der ersten Zelle jedes Kursnotebooks steht unter der Überschrift `*Stand: TT.MM.JJJJ*`. Bei jeder inhaltlichen Änderung das Datum aktualisieren. So sehen Lehrer und Schüler, welche Fassung jemand im Browser hat. Neue Notebooks dürfen als Beta-Fassung hochgeladen werden; Korrekturen kommen unter demselben Namen (Löschen-Knopf, siehe oben).
- Variablennamen wie an der Tafel: `s`, `v`, `a`, `F`, `m`, `dt`, `t`, `D`.
- Startercode kurz halten: Daten, Δt, eine Rechenzeile, ein Plot. Schüler modifizieren vorgegebenen Code, statt von Null zu schreiben.
- Lücken im Startercode einheitlich mit `??` markieren, dahinter ein Kommentar im Muster `# hier den Quotienten berechnen`. Schleifen und Plot vorgeben, die neue Idee (Länge der Folge, Rechenzeile) bleibt offen. Tipps zum Aufklappen dürfen die Lösung der `??` verraten.
- JupyterLite zeichnet jede Zelle in ein eigenes Diagramm. Soll ein Plot in einer späteren Zelle ergänzt werden (z. B. waagerechte Linie), den Plot dort vorgeben, nicht auf das Diagramm der früheren Zelle verweisen.
- Zuerst Schleifen, damit die rekursive Definition der Folge sichtbar ist. `np.diff` (Differenzenfolge) und `np.cumsum` (Summenfolge) erst später als Abkürzung zeigen.
- Zeitachse passend kürzen zeigen (`t[:-1]`), da jede Differenzenfolge ein Glied kürzer ist.
- Simulierte Messdaten: kleines Δt, zunächst ohne Rauschen (zweite Differenzen verstärken Rauschen stark). Rauschen ggf. später als Zusatz.
- Bei jedem Beispiel die Masse angeben, damit F = m·a berechnet werden kann.

## Unterrichtsabfolge
0. **Einstieg Folgen (rein mathematisch, ohne Physik):** `01_folgen` (explizit/rekursiv berechnen und plotten), `02_geometrische_summe` (Summenfolge, Grenzwert 1/(1−q) selbst finden), `03_fibonacci` (Quotienten → goldener Schnitt). Fibonacci-Folge heißt `f`, nicht `F` (Kraft).
1. **Analyse:** Aus einer Ortsfolge Geschwindigkeit und Beschleunigung als Differenzenfolgen berechnen (Startercode vorgegeben, Schüler erweitern).
2. **Newton einführen:** F = m·a, z. B. „gleiche Kraft, doppelte Masse, halbe Beschleunigung".
3. **Kraft in den Beispielen aus 1 bestimmen.** Analysekette s → v → a → F schließen. Beispiele mit verschiedenen Kraftarten wählen (Fall: konstante Kraft; Federschwingung: F gegen s ergibt fallende Gerade → Federgesetz F = −D·s selbst aus Daten finden).
4. **Erste Simulation:** Konstante Kraft, Summenfolgen in umgekehrter Richtung. Ergebnis mit der Analyse vergleichen.
5. **Federkraft simulieren:** F = −D·s, gleich mit der stabilen Variante B. Danach m, D und Startauslenkung verändern und die Wirkung beschreiben. Das Aufschaukeln (Variante A) ist nur Zusatz (siehe Numerik).
6. **Dämpfung und periodische Stöße:** Reibung dazu, dann Resonanz.

## Numerik: Reihenfolge im Simulationsschritt
- Variante A (einfaches Euler): Ort mit alter Geschwindigkeit fortschreiben → Schwingung schaukelt sich auf, obwohl keine Energie zugeführt wird.
- Variante B (semi-implizites Euler): erst v, dann s mit dem neuen v → stabil. Diese Variante verwenden.
  ```python
  for n in range(N):
      a = -D/m * s
      v = v + a*dt   # zuerst v ...
      s = s + v*dt   # ... dann s mit dem neuen v
  ```
- Didaktisch (Entscheidung vom 23.11.2026): Die Schüler bekommen Variante B vorgegeben und sollen zuerst erleben, dass Simulieren leicht ist. Das Vertauschen der Zeilen (Variante A, Aufschaukeln) ist ein ⭐-Zusatz in `06_simulieren_neu` (am 24.11.2026 umbenannt, damit die Fassung mit Animation alle erreicht).
- Hintergrund für den Lehrer: Variante B ist algebraisch gleichwertig zu Störmer-Verlet. Verlet ist die nach s(n+1) umgestellte zweite Differenzenfolge: s(n+1) = 2·s(n) − s(n−1) + a(n)·Δt². Kann als Querverbindung gezeigt werden, ohne Taylorreihen.
- Gesamtenergie E = ½·m·v² + ½·D·s² nur als Kontrollwerkzeug für den Lehrer, nicht für Schüler.

## Projekt: Resonanz
- Gedämpftes Federpendel plus periodischer Kraftstoß (wie Anschubsen einer Schaukel).
- Dämpfung ist nötig, sonst wächst die Amplitude bei Resonanz unbegrenzt.
- Eigenperiode T₀ nicht per Formel vorgeben, sondern aus freier Schwingung im Diagramm ablesen lassen.
- Stoß wirkt einen Zeitschritt lang; bei Änderung von Δt das Produkt F·Δt konstant halten.
- Entdeckungen: Unterresonanzen bei 2T₀, 3T₀ (jedes zweite/dritte Mal anschubsen); Phase des Stoßes (mit oder gegen die Bewegung).
- Höhepunkt: Resonanzkurve. Äußere Schleife über Stoßperioden, jeweils Endamplitude speichern und auftragen.

## Projekt: Dämpfungskraft aus Messdaten bestimmen
- Aus (simulierten) Daten einer gedämpften Schwingung zuerst das Hookesche Gesetz, dann die Dämpfungskraft bestimmen.
- s-F-Diagramm ist wegen der Dämpfung keine Gerade, sondern eine Spirale um die Hooke-Gerade. D bestimmen über:
  - Ausgleichsgerade durch die Punktwolke, oder
  - nur Umkehrpunkte (v = 0, keine Dämpfungskraft, F = −D·s exakt).
- Restkraft F − (−D·s) gegen v auftragen. Form zeigt Reibungsart: Ursprungsgerade (∝ v), Parabelform (Luftwiderstand ∝ v²), Stufe (Gleitreibung). Verschiedene Datensätze vorbereiten.
- Wichtig: Zeitzuordnung. a aus zweiter Differenz gehört zu Zeitpunkt n, v aus erster Differenz liegt zwischen n und n+1. Für diese Auswertung zentrale Differenz verwenden: v(n) = (s(n+1) − s(n−1)) / (2Δt) („Mittelwert der beiden Nachbargeschwindigkeiten"), sonst entsteht eine Schleife statt einer Geraden.

## Projekt: Fluchtgeschwindigkeit
- Senkrechter Start ohne Luftwiderstand, F = −G·M·m/r² als gegebenes Kraftgesetz einführen.
- Einstieg über Kontrast: Bei konstantem g kommt jede Rakete zurück; erst die mit der Höhe schwächere Anziehung ermöglicht eine Fluchtgeschwindigkeit.
- Startgeschwindigkeiten ausprobieren, Grenze per Intervallhalbierung eingrenzen (Folge von Intervallen). Ergebnis ca. 11,2 km/s.
- Δt etwa 1 bis 10 s, Simulationsdauer einige Tage. Kriterium: wird v negativ → fällt zurück; bleibt v bis zum Ende positiv → entkommen. Unscharfe Grenze als Diskussionsanlass.
- Konsequent in m und s rechnen, erst für die Ausgabe in km/s umrechnen.
- Erweiterung: Mond, Mars (nur Masse und Radius ändern).
- Erweiterung für schnelle Schüler: dynamisches Δt = 0,01 · r / v (pro Schritt höchstens 1 % des Abstands), mit Obergrenze per `min(...)` wegen v ≈ 0 am Umkehrpunkt. Zeit dann pro Schritt aufsummieren und als eigene Liste speichern (wieder eine Summenfolge).
