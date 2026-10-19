# WP2-Kurs Klasse 9: Bewegungen mit Folgen und Python

## Kontext
- Wahlpflichtkurs (WP2), Jahrgang 9, sehr motivierte Schüler.
- Vorwissen: Folgen, Differenzenfolgen, Summenfolgen. Newton wird im Kurs erst eingeführt. Keine Taylorreihen, keine Differential- oder Integralrechnung.
- Ziel ist kein Python-Kurs, sondern Bewegungen analysieren und simulieren. Python ist Werkzeug.
- Schüler arbeiten auf iPads im Browser mit JupyterLite (numpy, matplotlib).

## Technische Umsetzung
- Eigene JupyterLite-Seite auf GitHub Pages, erstellt aus der Vorlage `jupyterlite/demo`. Notebooks und CSV-Dateien liegen im Ordner `content/` und werden automatisch per GitHub Actions gebaut und veröffentlicht.
- Verwaltung durch den Lehrer in VS Code (Jupyter-Erweiterung, Git: Commit + Push).
- Die Seite ist öffentlich: nur Arbeitsmaterial, keine Schülerdaten.
- Änderungen der Schüler werden nur in ihrem Browser gespeichert; Vorlagen bleiben unverändert. Schüler sollen wichtige Notebooks als .ipynb herunterladen.
- Jedes Notebook auch in der fertigen JupyterLite-Seite testen (Pyodide verhält sich anders bei `input()`, Animationen, `time.sleep`, Dateipfaden).
- CSV einlesen: `np.loadtxt("datei.csv", delimiter=",", skiprows=1)`. Achtung: deutsche CSV-Dateien nutzen oft Semikolon und Dezimalkomma; Export mit Dezimalpunkt verwenden (z. B. in phyphox wählbar).

## Konventionen für Notebooks
- Sprache: Deutsch, Niveau Klasse 9.
- Variablennamen wie an der Tafel: `s`, `v`, `a`, `F`, `m`, `dt`, `t`, `D`.
- Startercode kurz halten: Daten, Δt, eine Rechenzeile, ein Plot. Schüler modifizieren vorgegebenen Code, statt von Null zu schreiben.
- Zuerst Schleifen, damit die rekursive Definition der Folge sichtbar ist. `np.diff` (Differenzenfolge) und `np.cumsum` (Summenfolge) erst später als Abkürzung zeigen.
- Zeitachse passend kürzen zeigen (`t[:-1]`), da jede Differenzenfolge ein Glied kürzer ist.
- Simulierte Messdaten: kleines Δt, zunächst ohne Rauschen (zweite Differenzen verstärken Rauschen stark). Rauschen ggf. später als Zusatz.
- Bei jedem Beispiel die Masse angeben, damit F = m·a berechnet werden kann.

## Unterrichtsabfolge
1. **Analyse:** Aus einer Ortsfolge Geschwindigkeit und Beschleunigung als Differenzenfolgen berechnen (Startercode vorgegeben, Schüler erweitern).
2. **Newton einführen:** F = m·a, z. B. „gleiche Kraft, doppelte Masse, halbe Beschleunigung".
3. **Kraft in den Beispielen aus 1 bestimmen.** Analysekette s → v → a → F schließen. Beispiele mit verschiedenen Kraftarten wählen (Fall: konstante Kraft; Federschwingung: F gegen s ergibt fallende Gerade → Federgesetz F = −D·s selbst aus Daten finden).
4. **Erste Simulation:** Konstante Kraft, Summenfolgen in umgekehrter Richtung. Ergebnis mit der Analyse vergleichen.
5. **Federkraft simulieren:** F = −D·s. Hier tritt das Aufschaukeln auf (siehe Numerik) und wird durch Vertauschen zweier Zeilen gelöst.
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
- Didaktisch: Schüler erst Variante A programmieren lassen, Aufschaukeln beobachten, dann Zeilen vertauschen (Aha-Moment).
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
