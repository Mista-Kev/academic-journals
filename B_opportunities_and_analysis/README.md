# B · Gelegenheiten und Analyse

**Kevins Teil:** Vergleichsgruppen und Nenner erklären, Auswertungen rechnen,
Ergebnisse gegen die Regeln prüfen und ihre Grenzen benennen.

| Frage / Schritt | Datei | Eingaben → Ergebnis |
|---|---|---|
| Q1/Q2 | `q1_q2_baselines.ipynb` | A-Paperdaten, Verlagszuordnung, Pfad-Gegenprüfung → beobachtete Wiederholungen / erwartete Wiederholungen |
| Q3-Gelegenheiten | `build_event_table.py` | A-Paperdaten → `data/event_table_python_v0_oppA.csv`, Variante B als Sensitivität |
| Vollständige Gegenprüfung | `diff_event_table.py` | Python-Tabelle aus B + Prolog-Tabelle aus A → Abweichungsbericht |
| Q3 | `q3_baselines.ipynb` | B-Gelegenheiten + C-Tabelle mit T + historischer Min-3-Vergleich → rohe und standardisierte Risikoverhältnisse |

Eine Q3-Zeile ist **Autor, bisher unbekanntes Journal, Jahr**. Nicht-Eintritte
gehören ausdrücklich dazu. Nach dem ersten beobachteten Eintritt endet das Paar.
Deshalb eignet sich diese Tabelle nicht für Q1-Rückkehranalysen.

Q1/Q2 vergleichen mit Ziehungen nach Jahr und zusätzlich nach Jahr und primärer
Themenkategorie. Das ist keine Kontrolle der kontinuierlichen historischen
Themenpassung T. Ein Ratio über eins bedeutet mehr Wiederholung als unter dem
jeweiligen Vergleichsmodell, keine nachgewiesene themenunabhängige Bindung.

Q3 berichtet sowohl C+T als auch die deutlich kleinere Journal-/Jahressensitivität.
Fehlendes T bleibt fehlend. Die vollständigen Fälle sind eine ausgewählte Population;
die Koeffizienten begründen keine kausale Aussage. Der lokale Abschluss legt
C+T als ursprünglichen Hauptvergleich mit verpflichtender Journal-/Jahressensitivität
fest. Complete Cases sind die explizite Analysepopulation; fehlendes T wird nicht
ersetzt. Begründungen stehen im [Entscheidungslog](../D_results/methods/decisions.md).

Start im Repo: `python3 demo.py q1-q2` bzw. `python3 demo.py q3`.
Alternativ Notebooks mit diesem Ordner als Arbeitsverzeichnis ausführen.
[Ergebnisse](../D_results/README.md) · [Demo](../D_results/DEMO.md)
