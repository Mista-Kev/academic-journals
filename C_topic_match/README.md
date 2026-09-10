# C · Themenpassung

**Zweck:** Misst die thematische Passung zwischen einem Autor und einem Journal zu
einem Zeitpunkt. Diese Zahl wird als kontinuierliche Kovariate T in Q3 verwendet.
Ob sie ein ausreichender oder kausal zulässiger Kontrollfaktor ist, folgt nicht aus
der Messung allein; frühere Zusammenarbeit kann spätere Themen beeinflusst haben.

**Verantwortlich:** Pierre
**Eingang:** `academic_journals.duckdb` (OpenAlex-Ausschnitt), Ereignis-Tabelle des Logic-Layers
**Ausgang:** dieselbe Tabelle plus fünf gefüllte Spalten.
Das Notebook schreibt nach `event_table_topicmatch.csv`. **Die geteilte Datei wird von Hand
in `event_table_topicmatch_v5.csv` umbenannt**; der geprüfte Stand liegt im gemeinsamen SharePoint-Ordner — jeder Lauf würde
sonst den vorigen überschreiben, ohne dass man es am Namen sieht.

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

Die tatsächliche Jahresrechnung ist
`topic_match = exp(-||Autorenprofil - Journalprofil||² / (2 * sig2))`.
Die Paper-Vektoren sind L2-normalisiert; ihre Profilmittelwerte werden **nicht erneut
normiert**. Nur für zwei Einheitsvektoren vereinfacht sich die Formel zu
`exp(-(1 - cos)/sig2)`. Diese Kosinus-Vereinfachung gilt daher nicht allgemein für
die Jahresprofile. Bei festen Profilen verändert ein positives `sig2` den Maßstab,
nicht die Rangfolge nach euklidischer Distanz.

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
| `below_threshold_unproductive` | Historischer Schwellenstatus; im geprüften v5-Export nicht vorhanden |
| `below_threshold_no_abstract` | genug Werke, aber zu wenige mit Abstract |
| `author_not_in_db` | Autor-ID nicht in der Rohdatenbasis |

---

## Regeln für die Weiterverarbeitung

Diese Punkte beschreiben die Schnittstelle und die aktuelle Auswertung. Statistische
Arbeitsentscheidungen sind kein Beweis für kausale Identifikation.

1. **Ein leeres `topic_match` ist niemals 0.** Leer heißt „kein Thema bekannt", nicht
   „Thema unähnlich". Eine 0 senkt Mittelwerte und verzerrt die Anpassung. Der Grund
   steht in `tm_status`.

2. **Vollständige Fälle, keine Ersatzkategorie.** In die Regression gehen nur Zeilen mit
   gültigem T. Das definiert die ausgewertete Teilpopulation, keine allgemeine
   Unverzerrtheitsgarantie. Die Simulationen zur Fehlwertkategorie prüfen bestimmte
   Szenarien; sie entscheiden den realen Auswahlmechanismus nicht.

3. **Keine Schwelle auf `topic_match`.** Der Wert geht stetig ins Modell. Eine Binarisierung
   bei 0,85, wie in einer früheren Fassung vorgeschlagen, ist überholt.

4. **Werte aus verschiedenen Läufen nicht mischen.** Quelle, Hash, Profildefinition,
   Parameter und verglichene Zeilen festhalten. Gleiche `MIN_PAPERS` und `sig2` garantieren
   keine gleiche Spalte. Unterschiede zwischen Läufen können auf denselben Schlüsseln
   ausdrücklich verglichen werden; dabei Teilpopulationen nicht verwechseln.

5. **Verbindung über IDs, nie über Namen.** Kurzform (`A5060045903`), nicht die volle URL.
   Der Konsistenzcheck in Abschnitt 14 prüft das, bevor gerechnet wird. Der separate
   Intra-Export enthält volle OpenAlex-URLs; vor einem ID-Vergleich normalisieren.

---

## Eingebaute Prüfungen

Der Lauf bricht ab, statt still Falsches zu rechnen:

- **Adapter aktiv** — `model.active_adapters` wird geprüft, nicht angenommen.
  Die Warnung `There are adapters available but none are activated` erscheint beim
  Modell-Laden im lokalen Test vor Aktivierung. Die Warnung allein belegt deshalb
  keinen inaktiven früheren Lauf; maßgeblich ist der Zustand beim Forward-Pass.
  Der Code prüft `active_adapters is not None`; `Stack[[PRX]]` ist der berichtete
  und lokal protokollierte Zustand, keine wörtliche Assert-Bedingung auf diesen Namen
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
  `MIN_PAPERS = 3` kann als Sensitivitätsvariante gesetzt werden, reproduziert in v5
  wegen des geänderten Journalpools aber nicht automatisch den alten v4-Lauf.

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

- **Outputs im Notebook geleert.** Der v5-Export liegt inzwischen vor und wurde
  unabhängig geprüft. Laufkennwerte stehen in `README_results.md`; das Notebook
  selbst enthält keinen gespeicherten Ausführungsnachweis.

---

## Läufe und ihre Kennwerte

| Lauf | Notebook | `MIN_PAPERS` | Paper | `sig2` | Mittelwert | gefüllte Zeilen | RR |
|---|---|---|---|---|---|---|---|
| mit Schwelle | v4 | 3 | 12.236 | 0,3613 | 0,776284 | 623.510 | 5,24 |
| ohne Schwelle, gleiche Zeilen | v4, lokal | 1 | — | 0,3611 | 0,785574 | 623.510 | 5,69 |
| ohne Schwelle, volle messbare-T-Population | v4, lokal | 1 | — | 0,3611 | 0,765488 | 1.106.356 | 6,09 |
| **v5-Lauf** | **v5** | **1** | **26.962** | **0,3635** | **0,766856** | **1.106.356** | **6,0929 / non-ride 3,3437 (C+T)** |

Die Ereignis-Tabelle hat 6.422.558 Zeilen.

### Prüfung der gelieferten v5-Datei

Der offizielle Export wurde am 7. September geprüft: 6.422.558 eindeutige
Ereignisschlüssel, unveränderte ursprüngliche Ereignisfelder, 1.106.356 gefüllte
T-Werte, keine Cutoff-Verletzung. Der Rohkorpus bestätigt 26.962 nutzbare Paper und
alle 640 Journal-Jahr-Profilzählungen. Gegenüber der lokalen v5-Regeneration sind
alle Nicht-T-Felder identisch; die maximale T-Abweichung beträgt 4,72×10⁻⁷.
Dateihash und Q3-Vergleiche stehen in [README_results.md](README_results.md).

0,785574 stammt aus den **623.510 gemeinsamen alten Zeilen**; der alte Mittelwert
auf allen 1.106.356 messbaren-T-Zeilen ist 0,765488. Die 77 % mehr beziehen sich
auf die Erweiterung von 623.510 auf 1.106.356, nicht auf v5 gegenüber der Population
hinter dem früheren RR 6,09. Die sechs überprüften Q3-Ratios ändern sich durch die
Datenversion wenig; die Journal-/Jahr-Spezifikation verändert sie deutlich.

Ein Adapter-Ursachenclaim erfordert einen kontrollierten Vergleich bei gleichem
Paperpool und gleicher Konfiguration. Unterschiedliche Mittelwerte oder eine
Ladewarnung isolieren diese Ursache nicht.

---

## Verbleibende Punkte

- **Versionierung der Ausgabedatei im Notebook:** `EVENT_OUT` schreibt weiterhin
  auf den unversionierten Pfad; die geteilte Datei wird von Hand umbenannt.
- **Adapter-Vergleich:** Ein früherer Robustheitsvergleich wurde von Pierre als
  ohne nennenswerten Einfluss berichtet. Eine einzelne Laufdifferenz damit nicht
  ohne dokumentierten gleichen Paperpool und gleiche Konfiguration kausal erklären.
- **Eingefrorene Variante** zum Zeitpunkt der ersten Wegbereitung: konzipiert,
  nicht gebaut; Zeitanker und Vergleichsregel für C=0 gesondert begründen.
- **Themenpassung für Q1/Q2:** Der Intra-Export beschreibt bereits beobachtete
  Autor-Journal-Gruppen. Er ersetzt keine historische T-Adjustierung für
  Rückkehrfälle und alternative Journals. Diese weitergehende Frage bleibt offen.
- **Analysegrenzen:** vollständige Fälle sind eine ausgewählte Population;
  Modellabhängigkeit und Unsicherheitsverfahren in der Q3-Auswertung erklären.

---

## Veraltete Dateien in diesem Ordner

- **`Results/archive/`** — abgelöste Ergebnisdateien mit `MANIFEST.md`, das für jede
  erklärt, aus welchem Lauf sie stammt und warum sie abgelöst wurde. Bewusst im Repo
  behalten, damit die Kette nachvollziehbar bleibt. Nicht mehr verwenden.
- **`README_results.md` ist aktuell**, kein Archiv: Ergebnisse, Dateiprüfung und
  zurückgezogene Anweisungen. Die früheren Anweisungen sind dort ausdrücklich
  als überholt gekennzeichnet.
- **`embeddings_colab_slim.ipynb`**, **`embeddings_colab_eventtable.ipynb`** —
  frühere Fassungen, nur zur Nachvollziehbarkeit
- **`keys_author_paper.csv`** — für Q3 hinfällig, seit die Ereignis-Tabelle das
  Verbindungsobjekt ist

## Wege im gemeinsamen Repository

Der aktuelle Code ist `embeddings_colab_eventtable_v5.ipynb`. Ältere Notebooks
liegen unter `archive/`; frühere Ergebnistabellen unter `results/archive/`.
Die historische Beschreibung einzelner Runs steht in `README_results.md`.

B liefert `../B_opportunities_and_analysis/data/event_table_python_v0_oppA.csv`.
Der geprüfte Jahres-Export liegt unter `data/event_table_topicmatch_v5.csv`;
B liest ihn dort. `results/results_q1_topic_match_v5.csv` ist die separate
Intra-Auswertung und fließt nicht als Adjustierung in die Q1/Q2-Ratios ein.

Das v5-Notebook verwendet weiterhin seine dokumentierte Colab-/Google-Drive-
Umgebung. Der gemeinsame Loader stellt seine geprüften Exporte für die Analyse
bereit; er automatisiert keinen GPU-Neulauf und baut die DuckDB nicht auf.
