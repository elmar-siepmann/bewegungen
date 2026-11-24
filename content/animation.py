"""Animation einer Bewegung entlang einer Linie (1D).

Benutzung im Notebook:

    from animation import animiere
    animiere(t_folge, s_folge)                 # Feder (Standard)
    animiere(t_folge, s_folge, art="fall")     # s nach unten gemessen
    animiere(t_folge, s_folge, art="wurf")     # s = Hoehe nach oben

Links bewegt sich der Koerper, rechts wird gleichzeitig das
s-t-Diagramm gezeichnet. Die Animation laeuft in echter Zeit:
Jedes Bild ist genau ein Zeitschritt dt (wie ein Daumenkino).
"""

import json
import uuid

from IPython.display import HTML, display

_ARTEN = ("feder", "fall", "wurf")


def animiere(t, s, art="feder", zeitlupe=1):
    """Spielt die Bewegung s(t) als Animation ab.

    t, s      : Listen oder Arrays gleicher Laenge (Zeit in s, Ort in m)
    art       : "feder" (Koerper an einer Feder, s nach oben),
                "fall"  (s wird nach unten gemessen),
                "wurf"  (s ist die Hoehe ueber dem Boden)
    zeitlupe  : 1 = echte Zeit, 2 = halb so schnell, ...
    """
    t = [float(x) for x in t]
    s = [float(x) for x in s]
    if len(t) != len(s):
        raise ValueError(f"t und s muessen gleich lang sein (t: {len(t)}, s: {len(s)}).")
    if len(t) < 2:
        raise ValueError("Es braucht mindestens zwei Werte.")
    if any(t[i + 1] <= t[i] for i in range(len(t) - 1)):
        raise ValueError("Die Zeiten in t muessen wachsen. Sind t und s vertauscht?")
    if art not in _ARTEN:
        raise ValueError(f'art muss "feder", "fall" oder "wurf" sein, nicht "{art}".')

    daten = json.dumps({"t": t, "s": s, "art": art, "zeitlupe": float(zeitlupe)})
    kennung = "anim_" + uuid.uuid4().hex[:8]
    display(HTML(_VORLAGE.replace("KENNUNG", kennung).replace("DATEN", daten)))


_VORLAGE = r"""
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
  const t = D.t, s = D.s, N = t.length;
  regler.max = N - 1;
  for (const o of lupe.options) if (+o.value === D.zeitlupe) o.selected = true;

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

  function zahl(v) { return (Math.round(v * 1000) / 1000).toString().replace(".", ","); }

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

  function schoeneSchrittweite(bereich) {
    const roh = bereich / 5, p = Math.pow(10, Math.floor(Math.log10(roh)));
    for (const f of [1, 2, 5, 10]) if (f * p >= roh) return f * p;
  }

  // Abspielen in echter Zeit: gezeigt wird immer der letzte Zeitschritt,
  // der schon erreicht ist (kein Glaetten, wie ein Daumenkino).
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
