"""Animation einer Bewegung: entlang einer Linie (1D) oder in der Ebene (2D).

Benutzung im Notebook:

    from animation import animiere

    # Bewegung entlang einer Linie: links der Koerper, rechts das s-t-Diagramm
    animiere(t_folge, s_folge)                 # Feder (Standard)
    animiere(t_folge, s_folge, art="fall")     # s nach unten gemessen
    animiere(t_folge, s_folge, art="wurf")     # s = Hoehe nach oben

    # Bewegung in der Ebene: einfach x und y angeben
    animiere(t_folge, x_folge, y_folge)
    animiere(t_folge, x_folge, y_folge, ziel=(4, 3.05))   # mit Ziel, z. B. Korb

Welche Art gemeint ist, erkennt animiere selbst: Steht an dritter Stelle
eine Liste, ist es eine Bahn in der Ebene. In der Ebene haben beide Achsen
denselben Massstab, damit Winkel und Formen stimmen.

Die Animation laeuft in echter Zeit: Jedes Bild ist genau ein Zeitschritt
dt (wie ein Daumenkino).
"""

import json
import uuid

from IPython.display import HTML, display

_ARTEN = ("feder", "fall", "wurf")


def _als_liste(werte, name):
    try:
        return [float(w) for w in werte]
    except TypeError:
        raise TypeError(f"{name} muss eine Liste oder ein Array von Zahlen sein.") from None


def animiere(t, s, y=None, art=None, zeitlupe=1, ziel=None):
    """Spielt eine Bewegung als Animation ab.

    Entlang einer Linie:  animiere(t, s, art="feder")
    In der Ebene:         animiere(t, x, y)

    t         : Zeiten in s
    s         : Ort in m (bei einer Bahn in der Ebene: x in m)
    y         : nur fuer die Ebene: Hoehe y in m
    art       : nur entlang einer Linie:
                "feder" (Koerper an einer Feder, s nach oben, Standard),
                "fall"  (s wird nach unten gemessen),
                "wurf"  (s ist die Hoehe ueber dem Boden)
    zeitlupe  : 1 = echte Zeit, 2 = halb so schnell, ...
    ziel      : nur fuer die Ebene: Punkt (x, y), der markiert wird
    """
    if isinstance(y, str):              # animiere(t, s, "fall") ist auch erlaubt
        art, y = y, None
    eben = y is not None
    name = "x" if eben else "s"

    t = _als_liste(t, "t")
    s = _als_liste(s, name)
    if len(t) != len(s):
        raise ValueError(f"t und {name} muessen gleich lang sein (t: {len(t)}, {name}: {len(s)}).")
    if len(t) < 2:
        raise ValueError("Es braucht mindestens zwei Werte.")
    if any(t[i + 1] <= t[i] for i in range(len(t) - 1)):
        raise ValueError("Die Zeiten in t muessen wachsen. Steht t an erster Stelle?")

    if not eben:
        if ziel is not None:
            raise ValueError("ziel gibt es nur fuer eine Bahn in der Ebene: animiere(t, x, y, ziel=(...)).")
        art = art or "feder"
        if art not in _ARTEN:
            raise ValueError(f'art muss "feder", "fall" oder "wurf" sein, nicht "{art}".')
        daten = {"t": t, "s": s, "art": art, "zeitlupe": float(zeitlupe)}
        vorlage = _VORLAGE_1D
    else:
        if art is not None:
            raise ValueError("art gibt es nur fuer eine Bewegung entlang einer Linie. "
                             "In der Ebene reicht animiere(t, x, y).")
        y = _als_liste(y, "y")
        if len(y) != len(t):
            raise ValueError(f"t, x und y muessen gleich lang sein (t: {len(t)}, x: {len(s)}, y: {len(y)}).")
        if ziel is not None:
            ziel = [float(ziel[0]), float(ziel[1])]
        daten = {"t": t, "x": s, "y": y, "ziel": ziel, "zeitlupe": float(zeitlupe)}
        vorlage = _VORLAGE_2D

    kennung = "anim_" + uuid.uuid4().hex[:8]
    html = vorlage.replace("KENNUNG", kennung).replace("DATEN", json.dumps(daten))
    display(HTML(html))


# ----------------------------------------------------------------------
# Gemeinsame Teile: Bedienelemente, Anfang des Skripts, Abspielen
# ----------------------------------------------------------------------
_RAHMEN = r"""
<div id="KENNUNG" style="font-family: sans-serif; max-width: 640px;">
  <canvas width="640" height="320" style="width: 100%; border: 1px solid #ccc; background: #fff;"></canvas>
  <div style="margin-top: 6px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
    <button class="start" style="font-size: 16px; min-width: 90px;">&#9654; Start</button>
    <button class="neu" style="font-size: 16px;">&#8635; Von vorn</button>
    <label>Zeitlupe
      <select class="lupe" style="font-size: 15px;">
        <option value="1">1&times; (echte Zeit)</option>
        <option value="2">2&times; langsamer</option>
        <option value="4">4&times; langsamer</option>
        <option value="10">10&times; langsamer</option>
      </select>
    </label>
    <input class="regler" type="range" min="0" value="0" style="flex: 1; min-width: 150px;">
  </div>
</div>
<script>
(function () {
  const D = DATEN;
  const box = document.getElementById("KENNUNG");
  const cv = box.querySelector("canvas"), c = cv.getContext("2d");
  const knopf = box.querySelector(".start"), neu = box.querySelector(".neu");
  const lupe = box.querySelector(".lupe"), regler = box.querySelector(".regler");
  const t = D.t, N = t.length;

  function zahl(v) { return (Math.round(v * 1000) / 1000).toString().replace(".", ","); }
  function schoeneSchrittweite(bereich) {
    const roh = bereich / 5, p = Math.pow(10, Math.floor(Math.log10(roh)));
    for (const f of [1, 2, 5, 10]) if (f * p >= roh) return f * p;
  }
"""

# Erwartet eine Funktion zeichne(n), die das Bild zum Zeitschritt n malt.
_ABSPIELEN = r"""
  // Abspielen in echter Zeit: gezeigt wird immer der letzte Zeitschritt,
  // der schon erreicht ist (kein Glaetten, wie ein Daumenkino).
  regler.max = N - 1;
  for (const o of lupe.options) if (+o.value === D.zeitlupe) o.selected = true;
  let n = 0, laeuft = false, startUhr = 0, startT = 0;
  function bild(jetzt) {
    if (!laeuft) return;
    const tz = startT + (jetzt - startUhr) / 1000 / (+lupe.value);
    while (n < N - 1 && t[n + 1] <= tz) n++;
    zeichne(n);
    if (n >= N - 1) { stopp(); return; }
    requestAnimationFrame(bild);
  }
  function los() {
    if (n >= N - 1) n = 0;
    laeuft = true; startUhr = performance.now(); startT = t[n];
    knopf.innerHTML = "&#10074;&#10074; Pause"; requestAnimationFrame(bild);
  }
  function stopp() { laeuft = false; knopf.innerHTML = "&#9654; Start"; }
  knopf.onclick = () => laeuft ? stopp() : los();
  neu.onclick = () => { n = 0; zeichne(0); if (laeuft) { startUhr = performance.now(); startT = t[0]; } };
  lupe.onchange = () => { if (laeuft) { startUhr = performance.now(); startT = t[n]; } };
  regler.oninput = () => { stopp(); n = +regler.value; zeichne(n); };
  zeichne(0);
})();
</script>
"""

# ----------------------------------------------------------------------
# Entlang einer Linie: links der Koerper, rechts das s-t-Diagramm
# ----------------------------------------------------------------------
_VORLAGE_1D = _RAHMEN + r"""
  const s = D.s;

  // Wertebereich von s
  let smin = Math.min(...s), smax = Math.max(...s);
  if (D.art === "feder") { const m = Math.max(Math.abs(smin), Math.abs(smax)) || 1; smin = -m; smax = m; }
  if (D.art === "wurf") smin = Math.min(0, smin);
  if (smax - smin < 1e-9) { smin -= 1; smax += 1; }
  const rand = 0.08 * (smax - smin); smin -= rand; smax += rand;

  const OBEN = (D.art === "feder") ? 85 : 30, UNTEN = 290;   // Pixelbereich fuer s (Feder: Platz fuer die Aufhaengung)
  const runter = (D.art === "fall");       // bei "fall" zeigt s nach unten
  const yKoerper = v => runter ? OBEN + (v - smin) / (smax - smin) * (UNTEN - OBEN)
                               : UNTEN - (v - smin) / (smax - smin) * (UNTEN - OBEN);
  const yDiagramm = v => UNTEN - (v - smin) / (smax - smin) * (UNTEN - OBEN);
  const GX0 = 250, GX1 = 620, t0 = t[0], t1 = t[N - 1];
  const xDiagramm = z => GX0 + (z - t0) / (t1 - t0) * (GX1 - GX0);
  const KX = 110;                          // x-Position des Koerpers

  function zeichne(n) {
    c.clearRect(0, 0, cv.width, cv.height);
    c.font = "14px sans-serif"; c.lineWidth = 1;

    // Massstab links (s-Werte)
    c.strokeStyle = "#999"; c.fillStyle = "#666";
    c.beginPath(); c.moveTo(40, OBEN); c.lineTo(40, UNTEN); c.stroke();
    const schritt = schoeneSchrittweite(smax - smin);
    for (let w = Math.ceil(smin / schritt) * schritt; w <= smax; w += schritt) {
      const y = yKoerper(w);
      c.beginPath(); c.moveTo(36, y); c.lineTo(44, y); c.stroke();
      c.fillText(zahl(w), 2, y + 5);
    }
    c.fillText(runter ? "s in m ↓" : "s in m", 2, OBEN - 12);

    // Koerper
    const y = yKoerper(s[n]);
    if (D.art === "feder") {
      c.strokeStyle = "#444"; c.lineWidth = 4;
      c.beginPath(); c.moveTo(KX - 40, 8); c.lineTo(KX + 40, 8); c.stroke();
      c.lineWidth = 2; c.beginPath(); c.moveTo(KX, 8);
      const windungen = 12, unten = y - 18;
      for (let i = 1; i < 2 * windungen; i++) {
        c.lineTo(KX + (i % 2 ? 12 : -12), 8 + (unten - 8) * i / (2 * windungen));
      }
      c.lineTo(KX, unten); c.stroke();
      c.strokeStyle = "#bbb"; c.setLineDash([4, 4]); c.lineWidth = 1;
      c.beginPath(); c.moveTo(KX - 40, yKoerper(0)); c.lineTo(KX + 40, yKoerper(0)); c.stroke();
      c.setLineDash([]);
      c.fillStyle = "#c62828"; c.fillRect(KX - 18, y - 18, 36, 36);
    } else {
      if (D.art === "wurf") {
        c.strokeStyle = "#795548"; c.lineWidth = 3;
        c.beginPath(); c.moveTo(KX - 50, yKoerper(0)); c.lineTo(KX + 50, yKoerper(0)); c.stroke();
      }
      c.fillStyle = "#c62828"; c.beginPath(); c.arc(KX, y, 14, 0, 2 * Math.PI); c.fill();
    }

    // Diagramm rechts
    c.strokeStyle = "#999"; c.lineWidth = 1; c.fillStyle = "#666";
    c.beginPath(); c.moveTo(GX0, OBEN); c.lineTo(GX0, UNTEN); c.lineTo(GX1, UNTEN); c.stroke();
    if (smin < 0 && smax > 0) {
      c.strokeStyle = "#ddd"; c.beginPath(); c.moveTo(GX0, yDiagramm(0)); c.lineTo(GX1, yDiagramm(0)); c.stroke();
    }
    c.strokeStyle = "#999";
    for (let w = Math.ceil(smin / schritt) * schritt; w <= smax; w += schritt) {
      const yy = yDiagramm(w);
      c.beginPath(); c.moveTo(GX0 - 4, yy); c.lineTo(GX0, yy); c.stroke();
      c.fillText(zahl(w), GX0 - 8 - c.measureText(zahl(w)).width, yy + 5);
    }
    c.fillText("s in m", GX0 + 6, OBEN - 6); c.fillText("t in s", GX1 - 40, UNTEN + 20);
    c.fillText(zahl(t0), GX0 - 4, UNTEN + 20); c.fillText(zahl(t1), GX1 - 70, UNTEN + 20);
    c.strokeStyle = "#1565c0"; c.lineWidth = 2; c.beginPath();
    for (let i = 0; i <= n; i++) {
      const px = xDiagramm(t[i]), py = yDiagramm(s[i]);
      i ? c.lineTo(px, py) : c.moveTo(px, py);
    }
    c.stroke();
    c.fillStyle = "#c62828"; c.beginPath(); c.arc(xDiagramm(t[n]), yDiagramm(s[n]), 5, 0, 2 * Math.PI); c.fill();

    // Verbindungslinie Koerper -> Diagramm (nur wenn beide gleich ausgerichtet sind)
    if (!runter) {
      c.strokeStyle = "rgba(198,40,40,0.35)"; c.setLineDash([3, 4]); c.lineWidth = 1;
      c.beginPath(); c.moveTo(KX + 20, y); c.lineTo(xDiagramm(t[n]), y); c.stroke();
      c.setLineDash([]);
    }

    c.fillStyle = "#000"; c.font = "15px sans-serif";
    const anzeige = "t = " + zahl(t[n]) + " s     s = " + zahl(s[n]) + " m";
    c.fillText(anzeige, GX1 - c.measureText(anzeige).width, 18);
    regler.value = n;
  }
""" + _ABSPIELEN

# ----------------------------------------------------------------------
# In der Ebene: Bahn mit gleichem Massstab auf beiden Achsen
# ----------------------------------------------------------------------
_VORLAGE_2D = _RAHMEN + r"""
  const X = D.x, Y = D.y;

  // Wertebereich (mit Ziel), etwas Rand
  const xs = X.slice(), ys = Y.slice();
  if (D.ziel) { xs.push(D.ziel[0]); ys.push(D.ziel[1]); }
  let xmin = Math.min(...xs), xmax = Math.max(...xs);
  let ymin = Math.min(...ys), ymax = Math.max(...ys);
  const boden = ymin >= -1e-9;             // alles oberhalb von y = 0: Boden zeichnen
  if (boden) ymin = 0;
  if (xmax - xmin < 1e-9) { xmin -= 1; xmax += 1; }
  if (ymax - ymin < 1e-9) { if (!boden) ymin -= 1; ymax += 1; }
  const rx = 0.06 * (xmax - xmin), ry = 0.08 * (ymax - ymin);
  xmin -= rx; xmax += rx; ymax += ry; if (!boden) ymin -= ry;

  // Gleicher Massstab auf beiden Achsen; die Hoehe des Bildes passt sich an
  const LI = 55, RE = 15, OB = 32, UN = 42, BREITE = cv.width - LI - RE;
  let k = BREITE / (xmax - xmin);
  let hoehe = k * (ymax - ymin);
  if (hoehe > 420) { k = 420 / (ymax - ymin); hoehe = 420; }
  if (hoehe < 160) { ymax = ymin + 160 / k; hoehe = 160; }   // sehr flache Bahn: oben Platz lassen
  cv.height = Math.round(hoehe + OB + UN);
  const x0 = LI + (BREITE - k * (xmax - xmin)) / 2;
  const px = v => x0 + (v - xmin) * k;
  const py = v => OB + (ymax - v) * k;

  function zeichne(n) {
    c.clearRect(0, 0, cv.width, cv.height);
    c.font = "14px sans-serif"; c.lineWidth = 1;

    // Gitter und Beschriftung (gleiche Schrittweite auf beiden Achsen)
    const schritt = schoeneSchrittweite(0.6 * Math.max(xmax - xmin, ymax - ymin));
    c.strokeStyle = "#eee"; c.fillStyle = "#666";
    for (let w = Math.ceil(xmin / schritt) * schritt; w <= xmax; w += schritt) {
      c.beginPath(); c.moveTo(px(w), py(ymin)); c.lineTo(px(w), py(ymax)); c.stroke();
      const txt = zahl(w); c.fillText(txt, px(w) - c.measureText(txt).width / 2, py(ymin) + 18);
    }
    for (let w = Math.ceil(ymin / schritt) * schritt; w <= ymax; w += schritt) {
      c.beginPath(); c.moveTo(px(xmin), py(w)); c.lineTo(px(xmax), py(w)); c.stroke();
      const txt = zahl(w); c.fillText(txt, px(xmin) - 8 - c.measureText(txt).width, py(w) + 5);
    }
    c.fillText("y in m", 4, OB - 12);
    c.fillText("x in m", px(xmax) - c.measureText("x in m").width, py(ymin) + 36);

    // Boden bzw. Achsen durch 0
    if (boden) {
      c.strokeStyle = "#795548"; c.lineWidth = 3;
      c.beginPath(); c.moveTo(px(xmin), py(0)); c.lineTo(px(xmax), py(0)); c.stroke();
    } else {
      c.strokeStyle = "#bbb"; c.lineWidth = 1;
      if (ymin < 0 && ymax > 0) { c.beginPath(); c.moveTo(px(xmin), py(0)); c.lineTo(px(xmax), py(0)); c.stroke(); }
      if (xmin < 0 && xmax > 0) { c.beginPath(); c.moveTo(px(0), py(ymin)); c.lineTo(px(0), py(ymax)); c.stroke(); }
    }

    // Ziel
    if (D.ziel) {
      const zx = px(D.ziel[0]), zy = py(D.ziel[1]);
      c.strokeStyle = "#ef6c00"; c.lineWidth = 3;
      c.beginPath(); c.arc(zx, zy, 9, 0, 2 * Math.PI); c.stroke();
      c.lineWidth = 1;
      c.beginPath(); c.moveTo(zx - 14, zy); c.lineTo(zx + 14, zy); c.moveTo(zx, zy - 14); c.lineTo(zx, zy + 14); c.stroke();
    }

    // Bahn bis jetzt
    c.strokeStyle = "#1565c0"; c.lineWidth = 2; c.beginPath();
    for (let i = 0; i <= n; i++) {
      i ? c.lineTo(px(X[i]), py(Y[i])) : c.moveTo(px(X[i]), py(Y[i]));
    }
    c.stroke();

    // Koerper
    c.fillStyle = "#c62828"; c.beginPath(); c.arc(px(X[n]), py(Y[n]), 8, 0, 2 * Math.PI); c.fill();

    c.fillStyle = "#000"; c.font = "15px sans-serif";
    const anzeige = "t = " + zahl(t[n]) + " s     x = " + zahl(X[n]) + " m     y = " + zahl(Y[n]) + " m";
    c.fillText(anzeige, cv.width - RE - c.measureText(anzeige).width, 18);
    regler.value = n;
  }
""" + _ABSPIELEN
