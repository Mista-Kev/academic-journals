# topic_match — Ergebnisse und Übergabe

Was der ML-Layer liefert, welche Zahlen dabei herauskommen und was die anderen
beiden Layer damit machen. Wie das Notebook arbeitet, steht in [README.md](README.md).

> **Achtung, diese Datei wurde vollständig ersetzt.** Die frühere Fassung
> beschrieb einen Stand vor der Ereignis-Tabelle und enthielt Anweisungen,
> die inzwischen widerlegt sind. Was daraus **nicht mehr gilt**, steht unten
> unter „Zurückgezogene Anweisungen". Bitte kurz lesen, falls ihr danach
> gearbeitet habt.

---

## Was ihr bekommt

**Für Q3:** `C_topic_match/data/event_table_topicmatch_v5.csv` im gemeinsamen
SharePoint-Ordner **Applied AI Group B Data / official-v5-2026-09-07-abcd-v1**.
Die [Anleitung zum Datenzugriff](../D_results/methods/shared-data.md#how-to-use-it)
erklärt Download oder OneDrive-Synchronisierung und die Konfiguration des Loaders.
Er prüft Dateigröße und SHA-256 gegen das Manifest.

> Das Notebook schreibt auf den unversionierten Pfad `event_table_topicmatch.csv`;
> die geteilte Datei wird **von Hand** umbenannt. Der Name allein belegt weder
> Version noch Schwellenstand: Es existieren auch lokale schwellenfreie Exporte
> ohne `_v5`. Vier gerundete Kennwerte sind Plausibilitätschecks, kein eindeutiger
> Dateifingerabdruck. Den offiziellen Export über den unten angegebenen SHA-256 prüfen.

Das ist die Ereignis-Tabelle des Logic-Layers, unverändert in Zeilenzahl und
Reihenfolge, mit fünf zusätzlich gefüllten Spalten. 6.422.558 Zeilen, 15 Spalten.

| Spalte | Bedeutung |
|---|---|
| `topic_match` | Themenpassung Autor zu Journal, 0 bis 1. **Leer, wenn kein Profil existiert.** |
| `n_profile_papers` | Paper des Autors strikt vor t |
| `n_journal_papers` | Paper des Journals strikt vor t — hängt nur am Journal-Jahr, nicht am Autor |
| `profile_cutoff` | letztes Jahr im Autorenprofil (nicht pauschal t−1) |
| `tm_status` | Grund, falls `topic_match` leer ist |

Verbindung immer über IDs, nie über Namen. Die Ereignistabelle nutzt Kurz-IDs
(`A5060045903`); der Intra-Export enthält volle OpenAlex-URLs. Vor einem Vergleich
auf Kurz-IDs normalisieren.

Für Q1 zusätzlich: [results/results_q1_topic_match_v5.csv](results/results_q1_topic_match_v5.csv) — 9.195 Autor-Journal-Zeilen mit
`topic_match_intra`, der mittleren Themenähnlichkeit der Paper eines Autors
innerhalb eines Journals. Die aktuelle Datei liegt unter `results/`.

Abgelöste Fassungen liegen in `results/archive/` mit einem `MANIFEST.md`, das für
jede Datei festhält, aus welchem Lauf sie stammt und warum sie abgelöst wurde.

---

## Die Zahlen

### Lauf mit Schwelle (`MIN_PAPERS = 3`) — Stand `06c39bb`

| Größe | Wert |
|---|---|
| Paper mit nutzbarem Abstract | 12.236 |
| Autoren mit mindestens 3 Papern | 5.500 |
| `sig2` (Maßstab der Ähnlichkeitsfunktion) | 0,3613 |
| Zeilen mit eingebettetem Autor | 1.013.688 |
| **gefüllte Zeilen** | **623.510** von 6.422.558 (9,7 %) |
| Mittelwert / Median `topic_match` | 0,776 / 0,778 |
| eindeutige Journal-Jahr-Kombinationen | 640 |
| Konsistenzverstöße `n_journal_papers` | **0** |

### v5-Lauf (`MIN_PAPERS = 1`, Journalprofile entkoppelt, Adapter belegt aktiv)

| Größe | Wert |
|---|---|
| einbettbare Paper im Bestand | 26.966, davon 4 mit leerem Abstract verworfen |
| eingebettete Paper | 26.962 |
| Autoren mit mindestens 1 einbettbaren Paper | 81.729 |
| `sig2` | **0,3635** |
| **gefüllte Zeilen** | **1.106.356** von 6.422.558 (17,2 %) |
| Mittelwert / Median `topic_match` | 0,767 / 0,765 |
| `active_adapters` | `Stack[[PRX]]` — Proximity-Adapter aktiv |

Statusverteilung dieses Laufs:

| Status | Zeilen | Anteil |
|---|---|---|
| `no_author_history` | 4.989.914 | 77,7 % |
| **`ok`** | **1.106.356** | **17,2 %** |
| `no_author_and_journal_history` | 253.203 | 3,9 % |
| `below_threshold_no_abstract` | 55.822 | 0,9 % |
| `no_journal_history` | 17.263 | 0,3 % |

`below_threshold_unproductive` entfällt bei `MIN_PAPERS = 1`. Neuer Hauptgrund ist, dass
der Autor vor t kein Paper hatte — 81 % der Autoren haben nur ein einziges Paper im Bestand.
`no_journal_history` fällt von 35.910 auf 17.263: Die Entkopplung der Journalprofile wirkt.

Alle eingebauten Prüfungen bestanden: Journalprofil-Vergleich gegen die DB 0 Abweichungen,
`n_journal_papers` 0 Verstöße, keine 0-Kodierung leerer Werte, `profile_cutoff` immer vor t,
Zeilenzahl unverändert.

### Nachprüfung der gelieferten Datei (7. September)

Die offizielle CSV wurde unabhängig geprüft; der ML-Code und die CSV wurden für
diese Dokumentationskorrektur nicht geändert.

```text
SHA-256 event_table_topicmatch_v5.csv
8a9e8a9257f3f00ce39a71f0dcefd09cd10bc1d8200580426ee94346284b2e37
```

Dateigröße: 497.765.187 Bytes. Mittelwert aller gefüllten Zeilen:
**0,7668561703**, Median **0,7651017000**. Alle ursprünglichen Ereignisfelder und
Schlüssel stimmen mit der Basistabelle überein. Die lokale v5-Regeneration stimmt
in sämtlichen Nicht-T-Feldern überein; T weicht maximal um **4,72×10⁻⁷** ab.
Unabhängige Rohkorpuszählung bestätigt 26.962 nutzbare Paper und alle 640
Journal-Jahr-Profilzählungen. `sig2` und Adapterzustand stammen aus Laufmetadaten;
sie stehen nicht in der CSV selbst.

**Die frühere Gegenüberstellung 0,785574 → 0,767 mischte Populationen.**
0,785574 ist der alte schwellenfreie Mittelwert auf 623.510 gemeinsamen Zeilen.
Auf allen 1.106.356 gefüllten Zeilen lag der alte Mittelwert bei 0,7654884008.
Gleiche Populationen getrennt von geänderten Messwerten vergleichen. Ein
Adapter-Ursachenclaim wurde durch diesen Dateivergleich nicht getestet.

### Ältere Läufe — Kevins Messung auf 623.510 gemeinsamen Zeilen

| Größe | mit Schwelle | ohne Schwelle |
|---|---|---|
| `sig2` | 0,3613 | 0,3611 |
| Mittelwert | 0,776284 | 0,785574 |
| Median | 0,777674 | 0,785794 |

Auf den 623.510 gemeinsamen Zeilen: Korrelation **0,951**, mittlere absolute
Abweichung **0,013**, maximale **0,325**.

**Der schwellenfreie Lauf ist maßgeblich** (Entscheidung 6). Die Schwelle filterte
auf einer Größe, die selbst mit Journaleintritten zusammenhängt, und wirkte
zusätzlich bis in die Journalprofile durch.

### Historischer Min-3-Lauf: warum rund 90 Prozent leer waren

| Status | Zeilen |
|---|---|
| `below_threshold_unproductive` | 5.386.995 |
| **`ok`** | **623.510** |
| `no_author_history` | 286.625 |
| `no_author_and_journal_history` | 67.643 |
| `no_journal_history` | 35.910 |
| `below_threshold_no_abstract` | 21.875 |

Kein diffuses Fehlen: 83,9 Prozentpunkte haben **eine** benannte Ursache — Autoren
unter der Produktivitätsschwelle. Genau diese Kategorie holt der schwellenfreie
Lauf zurück. Die Summe der Statuszeilen ergibt exakt 6.422.558.

### Taugt das Maß etwas?

Nachbarschaftsprobe an Ankerpapern:

| Anker | nächster Nachbar | Wert |
|---|---|---|
| A survey of transfer learning | Transfer learning: a friendly introduction | 0,923 |
| State-of-the-art in artificial neural network applications | Comprehensive Review of ANN Applications to Pattern Recognition | 0,906 |
| Survey on deep learning with class imbalance | Effective Class-Imbalance Learning Based on SMOTE and CNN | 0,908 |

Mittlere Ähnlichkeit innerhalb eines Journals über 8.254 Autoren: **0,767**
bei einer Standardabweichung von 0,091 (v4-Lauf: 0,756 über 4.366 Autoren).

Weil der Datensatz nur KI-Paper enthält, sind die absoluten Werte generell hoch.
**Gelesen werden Unterschiede, nicht Niveaus.**

---

## Verwendung in Q3

Die Berechnung und Interpretation gehören zu Kevins Analyse in B. Die
[Beschreibung der Schnittstellen und Rechnungen](../D_results/methods/analysis-interfaces.md)
erklärt, wie C, F und T verwendet werden, wie die Non-ride-Auswertung entsteht und
wie die Unsicherheit berechnet wird. Die [Berichtsentscheidung](../D_results/methods/decisions.md)
hält die Modellvergleiche und ihre Grenzen fest. Damit steht die methodische
Erklärung an einer Stelle; hier bleiben die Topic-Ergebnisse und die Übergabe.

### Q3 auf dem offiziellen v5-Export: lokal nachgerechnet

Die folgenden sechs Fits auf dem offiziellen v5-Export wurden nachgerechnet.
Die Auswertung liegt inzwischen auf `main` im
[Q3-Notebook](../B_opportunities_and_analysis/q3_baselines.ipynb).
Die Tabelle fasst die Verwendung der gelieferten Themenpassung zusammen.

| Outcome / Population | C + T | C + T + separate Journal-/Jahreffekte |
|---|---:|---:|
| Q3_all, alle 1.106.356 messbaren-T-Zeilen | 6,0929 | — |
| Non-ride, dieselben 1.106.356 Zeilen | 3,3437 | — |
| Q3_all, dieselben 1.088.420 Diagnostikzeilen | 6,0058 | 2,2653 |
| Non-ride, dieselben 1.088.420 Diagnostikzeilen | 3,2967 | 1,1826 |

Die Diagnostik schließt Journal `S4210228265` mit 17.936 messbaren-T-Zeilen und
keinem Eintritt wegen Separation aus. Das ist ein **am Outcome bestimmter
Ausschluss**, keine Routinebereinigung. Für den Spezifikationsvergleich deshalb
die beiden Modelle auf derselben Teilpopulation gegenüberstellen. Separate
Journal-/Jahreffekte sind keine Journal×Jahr-Interaktionen. Alle Werte sind
modellbasierte standardisierte Assoziationen, keine identifizierten kausalen Effekte.

Autoren-Delta-Intervalle (95 %) für die volle C+T-Auswertung: Q3_all
[5,7566; 6,4489], Non-ride [3,1188; 3,5847]. Auswahl vollständiger Fälle,
Modellspezifikation und Abhängigkeiten bleiben Einschränkungen.

**77 % mehr gefüllte Zeilen** gilt gegenüber dem alten Min-3-Bestand mit 623.510
Zeilen. Bereits der frühere schwellenfreie RR 6,09 verwendete 1.106.356 Zeilen.
Der v5-Neulauf und die Non-ride-Kennzahl sind daher keine fehlenden Rechnungen mehr.

**Übergabeobjekt ist die CSV.** Reproduktion anhand von Quelle, Konfiguration,
Hash und Vergleichen auf denselben Schlüsseln beurteilen. Gleiche gerundete
Laufkennwerte allein beweisen keine identische Spalte.

---

## Was der Logic-Layer davon braucht

Wenig — die Richtung läuft überwiegend andersherum. Zwei Punkte:

- **`n_journal_papers`** ist ab v4 eine Eigenschaft des Journal-Jahres und für
  **alle** Zeilen gefüllt, auch für die ohne `topic_match`. Als Kontrollgröße für
  Journalgröße nutzbar. Achtung: Ab v5 zählt sie alle einbettbaren Paper des
  Journals, vorher nur die der ausgewählten Autoren — die Bedeutung ändert sich,
  der Spaltenname bleibt.

- **`topic_match_intra`** aus `results_q1_topic_match_v5.csv` beschreibt die
  Ähnlichkeit in bereits beobachteten Autor-Journal-Gruppen. Es beantwortet
  nicht den historischen Rückkehrvergleich gegen alternative Journals und
  ersetzt keine kontinuierliche T-Adjustierung von Q1/Q2.

---

## Zurückgezogene Anweisungen

Die frühere Fassung dieser Datei enthielt vier Punkte, die **nicht mehr gelten**.
Falls ihr danach gearbeitet habt, bitte prüfen:

| Alt | Warum verworfen |
|---|---|
| „Aus dem Thema-Wert ein Ja/Nein machen, Schwelle 0,85" | Willkürliche Grenze, Informationsverlust. T geht stetig ins Modell. |
| „Leere Werte als eigene Gruppe behandeln" | Im untersuchten Simulationsdesign verworfen. Das begründet keine allgemeine Überlegenheit vollständiger Fälle und löst die reale Auswahl durch Profilverfügbarkeit nicht. |
| „`keys_author_paper.csv` ist die Basis für den Logic-Teil" | Überholt. Zentrales Verbindungsobjekt ist die Ereignis-Tabelle. Q3 braucht die nicht realisierten Kombinationen als Nenner; die Publikationstabelle hat sie nicht. |
| „An eure Ereignisse dranjoinen über `work_id`" | Entfällt. Der ML-Layer schreibt direkt in die Ereignis-Tabelle, es gibt keinen Join mehr. |

Ein Punkt aus der alten Fassung gilt weiter und ist wichtiger geworden:
**leere Werte niemals als 0 behandeln.**

---

## Hinweise zur Weiterverwendung

- **Dateinamen im Notebook versionieren**, damit die Umbenennung nicht von Hand passiert.
- **Ausführungsnachweis:** Das v5-Notebook enthält keine gespeicherten Outputs;
  Laufbericht und unabhängiger Exportcheck sind davon zu unterscheiden.
- **Adapter-Vergleich:** Pierre hat für einen früheren Robustheitsvergleich keinen
  nennenswerten Einfluss berichtet. Das wird nicht mehr pauschal als ausstehender
  Test geführt. Für die eindeutige Ursache einer konkreten Laufdifferenz sind
  unveränderter Paperpool, Konfiguration und Vergleichsoutputs zu dokumentieren;
  das ist keine Voraussetzung, den geprüften v5-Export zu nutzen.
- **Unsicherheit und Interpretation** in der Q3-Abgabe konsistent mit den tatsächlich
  ausgeführten Verfahren beschreiben. Keine neue v5-Bootstrap-Rechnung behaupten.
- **Historische kontinuierliche Themenpassung für Q1/Q2** bleibt eine weitergehende
  Analysefrage. Die vorhandenen Jahr/Primärthema-Nullmodelle und der Intra-Export
  beantworten sie nicht vollständig.
