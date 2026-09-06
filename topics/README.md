# topics/ — topic_match (ML-Layer)

**Zweck:** Misst die thematische Passung zwischen einem Autor und einem Journal zu
einem Zeitpunkt. Diese Zahl ist der Störfaktor T in Q3 — sie wird herausgerechnet,
sie ist nicht der gesuchte Effekt.

**Verantwortlich:** Pierre
**Eingang:** `academic_journals.duckdb` (OpenAlex-Ausschnitt), Ereignis-Tabelle des Logic-Layers
**Ausgang:** `event_table_topicmatch_v5.csv` — dieselbe Tabelle plus fünf gefüllte Spalten.
**Der Dateiname trägt ab v5 die Fassung**; frühere Läufe schrieben alle auf denselben Pfad.

Der ML-Layer erzeugt **keine** der drei Endkennzahlen. Er füllt eine Spalte.

---

## Was das Notebook tut

`embeddings_colab_eventtable_v5.ipynb`, in Google Colab mit GPU (T4) auszuführen.
Abschnitte der Reihe nach, kein Abschnitt darf übersprungen werden.

| # | Abschnitt | Was passiert |
|---|---|---|
| 3 | Datenbank | DuckDB aus Drive in den lokalen Colab-Speicher kopieren (~233 MB) |
| 4 | Setup | Pakete installieren, Versionen ausgeben, GPU prüfen |
| 5 | Auswahl | Autoren nach `MIN_PAPERS` auswählen; **alle** einbettbaren Paper laden |
| 6 | Abstracts | OpenAlex speichert Abstracts als Wortpositionen — hier wieder zu Text zusammensetzen |
| 7 | Einbettung | SPECTER2 mit Proximity-Adapter, CLS-Vektor, L2-normalisiert, Blöcke à 32 |
| 8 | Ähnlichkeit | Maßstab `sig2` aus 3.000 Stichproben-Papern; gruppenweise Rechnung statt voller Matrix |
| 9 | Testblock | Nachbarschaftsprobe an Ankerpapern, mittlere Ähnlichkeit innerhalb eines Journals |
| 14 | Füllen | Ereignis-Tabelle laden, Profile bilden, `topic_match` und vier Diagnosespalten schreiben |

### Das Verfahren in drei Sätzen

Jedes Paper wird zu einem Vektor mit 768 Zahlen. Das **Autorenprofil** zu einem Jahr t ist
der Schwerpunkt seiner Paper aus den Jahren **strikt vor t**, das **Journalprofil** analog
der Schwerpunkt der Paper dieses Journals vor t. `topic_match` ist die Ähnlichkeit beider
Profile.

Formal ist `topic_match = exp(-(1 - cos)/sig2)` bei Vektoren der Länge 1 — also eine streng
monotone Funktion der Kosinus-Ähnlichkeit. Rangfolgen hängen deshalb nicht von `sig2` ab,
die Zahlenwerte aber schon.

---

## Was herauskommt

Die Ausgabedatei ist die Ereignis-Tabelle mit denselben Zeilen und fünf zusätzlichen Spalten.
Zeilenzahl vor und nach dem Lauf ist identisch.

| Spalte | Typ | Bedeutung |
|---|---|---|
| `topic_match` | float | Themenpassung, 0 bis 1. **Leer, wenn kein Profil existiert.** |
| `n_profile_papers` | Int64 | Paper des Autors strikt vor t (im Embedding-Bestand) |
| `n_journal_papers` | Int64 | Paper des Journals strikt vor t. Eigenschaft des Journal-Jahres, **nicht** der Zeile |
| `profile_cutoff` | Int64 | Tatsächlich letztes Jahr im Autorenprofil — nicht pauschal t−1 |
| `tm_status` | str | Grund, warum ein Wert fehlt |

### Statuscodes

| Code | Bedeutung |
|---|---|
| `ok` | Autor- und Journalprofil vorhanden, Wert gerechnet |
| `no_author_history` | Autor hat vor t kein eingebettetes Paper |
| `no_journal_history` | Journal hat vor t kein eingebettetes Paper |
| `no_author_and_journal_history` | beides fehlt |
| `below_threshold_unproductive` | Autor unter `MIN_PAPERS` Werken insgesamt |
| `below_threshold_no_abstract` | genug Werke, aber zu wenige mit Abstract |
| `author_not_in_db` | Autor-ID nicht in der Rohdatenbasis |

---

## Regeln für die Weiterverarbeitung

Diese fünf Punkte sind nicht verhandelbar. Vier davon sind aus Fehlern entstanden.

1. **Ein leeres `topic_match` ist niemals 0.** Leer heißt „kein Thema bekannt", nicht
   „Thema unähnlich". Eine 0 senkt Mittelwerte und verzerrt die Anpassung. Der Grund
   steht in `tm_status`.

2. **Vollständige Fälle, keine Ersatzkategorie.** In die Regression gehen nur Zeilen mit
   gültigem T. Eine dritte Kategorie „fehlt" wurde per Simulation getestet (400.000 Zeilen,
   drei Fehlmechanismen) und verworfen — sie bringt den Störfaktor ins Modell zurück.

3. **Keine Schwelle auf `topic_match`.** Der Wert geht stetig ins Modell. Eine Binarisierung
   bei 0,85, wie in einer früheren Fassung vorgeschlagen, ist überholt.

4. **Werte aus verschiedenen Läufen nicht mischen.** Zwei Läufe sind nur vergleichbar, wenn
   `MIN_PAPERS` **und** `sig2` übereinstimmen. Die Korrelation zwischen dem Lauf mit und ohne
   Schwelle liegt bei 0,951, die maximale Abweichung je Zeile aber bei 0,325.

5. **Verbindung über IDs, nie über Namen.** Kurzform (`A5060045903`), nicht die volle URL.
   Der Konsistenzcheck in Abschnitt 14 prüft das, bevor gerechnet wird.

---

## Eingebaute Prüfungen

Der Lauf bricht ab, statt still Falsches zu rechnen:

- **Adapter aktiv** — `model.active_adapters` wird geprüft, nicht angenommen.
  Die Warnung `There are adapters available but none are activated` erscheint beim
  Modell-Laden **vor** `load_adapter` und ist ein Fehlalarm; maßgeblich ist die Ausgabe
  von `active_adapters` danach
- **Buchhaltung der Abstracts** — `len(titles) + n_dropped == len(rows)`
- **GPU vorhanden** — sonst dauert der Lauf Stunden
- **ID-Überlappung** zwischen Embeddings und Ereignis-Tabelle
- **Journalprofile** gegen eine unabhängige DuckDB-Zählung (Stichprobe 200 Journale).
  Die bekannte Differenz durch leere Abstracts wird abgezogen, **nicht** dadurch umgangen,
  dass die Vergleichszählung aus `meta` gebaut wird — das wäre ein Vergleich von `meta`
  mit sich selbst und würde immer bestehen
- **`n_journal_papers`** je Journal-Jahr eindeutig — erwartet: 0 Verstöße
- **kein leeres `topic_match`** als 0 kodiert
- **`profile_cutoff` < t** in jeder Zeile
- **Zeilenzahl** unverändert

---

## Versionshistorie

| Fassung | Commit | Was sich geändert hat und warum |
|---|---|---|
| `embeddings_colab_slim` | — | Erster Entwurf. Lieferte `keys_author_paper.csv` und eine Q1-Ähnlichkeit je Autor-Journal. Gemittelt wurde über **alle** Paper eines Autors, auch spätere. |
| v1 → v2 | `6e58c5e` | **Wechsel des Integrationsobjekts.** Statt eigener Tabellen füllt der ML-Layer nur noch eine Spalte in der Ereignis-Tabelle des Logic-Layers. Grund: Q3 braucht die nicht realisierten Autor-Journal-Kombinationen als Nenner; die Publikationstabelle hat sie nicht. |
| v2 → v3 | `477dff1` | **Diagnosespalten und Int64-Fix.** Rund 90 % der Zeilen hatten keinen Wert — ohne Erklärung ein Alarmsignal. Seither trägt jede Zeile ihren Grund in `tm_status`. Zusätzlich: pandas wandelt Ganzzahlspalten mit Fehlwerten still in float um (2020 → 2020.0), was `t_first_seed` als Verknüpfungsschlüssel unbrauchbar machte. |
| v3 → v4 | `c0eff3e` | **Zwei Schnittstellenfehler.** `n_journal_papers` wurde nur für Zeilen mit zugeordnetem Autor geschrieben — eine Journal-Eigenschaft hing damit vom Autor ab. Und wo kein Profil existierte, stand eine 0 statt `pd.NA`. |
| v4 (Notebook) | `06c39bb` | Notebook-Stand mit `MIN_PAPERS = 3`. **Die Commit-Nachricht bezeichnet ihn fälschlich als schwellenfrei.** Erkennbar an den Outputs: `sig2` 0,3613, Mittelwert 0,776, 623.510 gefüllte Zeilen — das ist der Lauf hinter der relativen Risikozahl 5,24. |
| v4 → v5 | *dieser Stand* | Siehe unten. |

### Was v5 ändert

- **`MIN_PAPERS = 1`.** Die Drei-Paper-Schwelle fällt (Entscheidung 6). Sie filterte auf einer
  Größe, die selbst schon mit Journaleintritten zusammenhängt, und schnitt 83,9 % der Zeilen ab.
  `MIN_PAPERS = 3` reproduziert den alten Lauf und ist nur noch Sensitivitätsvariante.

- **Journalprofile von der Schwelle entkoppelt.** Bis v4 lief die Kette
  `MIN_PAPERS → chosen_ids → work_ids → meta → journal_pairs`, das Journalprofil hing also an
  der Autorenauswahl — dieselbe Fehlerklasse wie bei `n_journal_papers`, eine Ebene tiefer.
  Ab v5 werden alle einbettbaren Paper geladen. Die **Autoren**profile bleiben über
  `author_works` auf `chosen_ids` beschränkt; dort ist die Auswahl richtig.

- **Adapter-Status wird geprüft.** Der v4-Lauf meldete trotz `set_active=True` eine Warnung,
  dass kein Adapter aktiv sei — im selben Lauf war die Paketinstallation abgebrochen.
  v5 gibt die Paketversionen aus und bricht ab, wenn kein Adapter aktiv ist.

- **Ein Join statt einer Abfrage je Autor.** Die Autor-Werk-Schleife hätte bei
  `MIN_PAPERS = 1` rund 82.000 Einzelabfragen an DuckDB gestellt.

- **Zwei zusätzliche Prüfungen** am Ende des Laufs (kein leeres `topic_match` als 0,
  `profile_cutoff` strikt vor t).

- **Tote Variable `N_AUTHORS = 150` entfernt.** Sie wurde vom Code ohnehin überschrieben,
  las sich aber wie eine Stichprobenbegrenzung.

- **Outputs geleert.** Der Lauf steht noch aus.

---

## Läufe und ihre Kennwerte

| Lauf | Notebook | `MIN_PAPERS` | Paper | `sig2` | Mittelwert | gefüllte Zeilen | RR |
|---|---|---|---|---|---|---|---|
| mit Schwelle | v4 | 3 | 12.236 | 0,3613 | 0,776284 | 623.510 | 5,24 |
| ohne Schwelle, gleiche Zeilen | v4, lokal | 1 | — | 0,3611 | 0,785574 | 623.510 | 5,69 |
| ohne Schwelle, volle Population | v4, lokal | 1 | — | 0,3611 | 0,785574 | — | 6,09 |
| **v5-Lauf** | **v5** | **1** | **26.962** | **0,3635** | **0,767** | **1.106.356** | offen |

Die Ereignis-Tabelle hat 6.422.558 Zeilen.

### Abnahmekriterium: nicht erfüllt

Geprüft wurde, ob v5 den schwellenfreien Lauf reproduziert (`sig2 = 0,3611`, Mittelwert
`0,785574`). **Tut es nicht:** 0,3635 und 0,767, eine Abweichung von 0,7 % beziehungsweise
2,4 %. Die gefüllte Population liegt zudem 77 % höher.

**v5 ist damit nicht die Quelle der Zahlen 5,69 und 6,09.** Diese stammen aus einem lokalen
Lauf mit v4-Code, der nicht im Repo liegt.

Wahrscheinlichste Ursache: der Proximity-Adapter. v5 belegt mit `active_adapters` = `Stack[[PRX]]`,
dass er aktiv ist. Für die früheren Läufe ist das offen — dort war die Paketinstallation
abgebrochen, es lief eine vorinstallierte `adapters`-Version. Andere Vektoren bedeuten anderes
`sig2` und andere Werte.

**Test:** v5 einmal ohne aktiven Adapter laufen lassen (Zeile `load_adapter` und den `assert`
in Abschnitt 7 auskommentieren). Ergibt das `sig2 ≈ 0,3611`, ist die Abweichung erklärt.

---

## Offene Punkte

- **Adapter-Test:** v5 ohne aktiven Adapter laufen lassen, um die Abweichung zu 0,3611 zu erklären
- **Kevin muss Q3 neu rechnen** — die gefüllte Population ist von 623.510 auf 1.106.356 gewachsen
- **Eingefrorene Variante** von `topic_match` zum Zeitpunkt der ersten Wegbereitung —
  konzipiert, nicht gebaut. Muss ohne Schwelle gebaut werden, sonst nicht vergleichbar
- **Adapter-Vergleich** als Robustheitsprüfung dokumentieren
- **Themenpassung für Q1 und Q2** — Anfrage aus der Besprechung mit dem Professor.
  `topic_match_intra` liegt bereits vor (5.307 Autor-Journal-Zeilen, Mittelwert 0,756,
  Standardabweichung 0,084), ist aber nicht ausgewertet

---

## Veraltete Dateien in diesem Ordner

- **`README_results.md`** — beschreibt den Stand vor der Ereignis-Tabelle. Enthält
  überholte Anweisungen: Binarisierung von `topic_match` bei 0,85 und Fehlwerte
  „als eigene Gruppe behandeln". Beides wurde später verworfen. Nicht mehr befolgen.
- **`embeddings_colab_slim.ipynb`**, **`embeddings_colab_eventtable.ipynb`** —
  frühere Fassungen, nur zur Nachvollziehbarkeit
- **`keys_author_paper.csv`** — für Q3 hinfällig, seit die Ereignis-Tabelle das
  Verbindungsobjekt ist
