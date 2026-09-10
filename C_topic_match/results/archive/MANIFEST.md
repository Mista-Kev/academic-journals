# Archiv — abgelöste Ergebnisdateien

Diese Dateien sind **nicht mehr zu verwenden**, bleiben aber im Repo, damit
nachvollziehbar ist, welche Zwischenstände es gab und warum sie abgelöst wurden.

Der aktuelle Stand liegt eine Ebene höher in `C_topic_match/results/`.

---

## Übersicht

| Datei | Zeilen | Aus welchem Lauf | Abgelöst durch | Grund |
|---|---|---|---|---|
| `results_q1_topic_match_v4.csv` | 5.307 | v4, `MIN_PAPERS = 3` | `results_q1_topic_match_v5.csv` | Produktivitätsschwelle gefallen |
| `results_topic_match_temporal.csv` | 23.244 | Vorfassung, 5.500 Autoren | kein Nachfolger | Verfahren verworfen |
| `keys_author_paper.csv` | 110.772 | v4-Zeitraum | Ereignis-Tabelle | Integrationsobjekt gewechselt |

---

## results_q1_topic_match_v4.csv

**Was drinsteht:** `author_id, journal_id, n_papers, topic_match_intra, work_ids` —
die mittlere Themenähnlichkeit der Paper eines Autors innerhalb eines Journals.

**Warum abgelöst:** Der Lauf verwendete die Produktivitätsschwelle von drei Papern.
Diese filterte auf einer Größe, die selbst mit Journaleintritten zusammenhängt
(Entscheidung 6), und wirkte zusätzlich bis in die Journalprofile durch.

**Verhältnis zum Nachfolger:** Echte Teilmenge. Alle 5.307 Autor-Journal-Paare sind
in der v5-Fassung enthalten, dort kommen 3.888 weitere hinzu. Die Werte verschieben
sich geringfügig, weil `sig2` sich von 0,3613 auf 0,3635 geändert hat — mittlere
absolute Abweichung 0,0012, maximal 0,0022. Nur 14 der 5.307 Werte sind exakt gleich.

**Wichtig:** Werte aus beiden Fassungen dürfen nicht gemischt werden.

| | v4 | v5 |
|---|---|---|
| Autor-Journal-Zeilen | 5.307 | 9.195 |
| Autoren mit ≥ 2 Papern im selben Journal | 4.366 | 8.254 |
| Mittelwert `topic_match_intra` | 0,756 | 0,767 |
| Standardabweichung | 0,084 | 0,091 |

---

## results_topic_match_temporal.csv

**Was drinsteht:** `author_id, journal_id, t, work_id, topic_match_t` — eine
Ähnlichkeit je **Einzelpaper** gegen das Journal, mit tagesgenauem Zeitstempel.

**Warum verworfen, zwei unabhängige Gründe:**

1. **Einzelpaper statt Profil.** Die Ereignis-Tabelle enthält Zeilen für Journale,
   in die ein Autor nie eingetreten ist. Dort existiert kein Paper, das man
   vergleichen könnte. Nur ein rollendes Autorenprofil ist auf allen 6.422.558
   Zeilen definiert (Entscheidung 1).

2. **Tagesebene statt Jahresebene.** OpenAlex füllt fehlende Tages- und
   Monatsangaben mit dem 1. Januar. In dieser Datei betrifft das **7.353 von
   23.244 Zeilen, also 31,6 %** — die Tagesordnung ist dort zu knapp einem Drittel
   erfunden. Der Logic-Layer rechnet aus demselben Grund auf Jahresebene
   (Entscheidung 3).

**Herkunft:** 5.500 Autoren, das entspricht dem Lauf mit `MIN_PAPERS = 3`. Welches
Notebook sie genau erzeugt hat, ist nicht mehr eindeutig zuzuordnen — kein
aktuelles Notebook schreibt diese Datei.

**Kein Nachfolger.** Die Zeitkomponente steckt heute in `topic_match` selbst: Das
Profil wird aus Papern strikt vor dem Jahr t gebildet.

---

## keys_author_paper.csv

**Was drinsteht:** eine Zeile je Autor und Paper mit Journal, Verlag und
DOAJ-Kennzeichen. 110.772 Zeilen, 19 MB.

**Warum abgelöst:** Der erste Entwurf sah vor, dass der ML-Layer eigene Tabellen
liefert und der Logic-Layer sie anjoint. Seit dem Wechsel des Integrationsobjekts
füllt der ML-Layer nur noch eine Spalte in der Ereignis-Tabelle des Logic-Layers.
Für Q3 ist diese Datei hinfällig, weil ihr die nicht realisierten
Autor-Journal-Kombinationen fehlen — genau die braucht Q3 als Nenner.

**Nicht mit der Q1/Q2-Auswertung verwechseln.** Die arbeitet mit 110.654
Autor-Paper-Paaren aus einer eigenen Ableitung, nicht mit dieser Datei. Die
Zeilenzahlen unterscheiden sich.

---

## Wie man die Kette nachvollzieht

| Schritt | Wo |
|---|---|
| Entstehung und Begründung jeder Fassung | `C_topic_match/README.md`, Abschnitt Versionshistorie |
| Ergebnisse und Übergaberegeln | `C_topic_match/README_results.md` |
| Ausgeführte Läufe mit Ausgaben | `C_topic_match/archive/embeddings_colab_eventtable_v4.ipynb` und `C_topic_match/embeddings_colab_eventtable_v5.ipynb` |
| Festgelegte Entscheidungen mit Datum | `D_results/README.md` |
| Aufbau des Q3-Modells | `D_results/README.md` |

Die Notebooks enthalten die gespeicherten Ausgaben ihrer produktiven Läufe. Wer
prüfen will, aus welchem Lauf eine Zahl stammt, vergleicht `MIN_PAPERS`, `sig2`,
Mittelwert und Zeilenzahl — diese vier Werte werden am Ende jedes Laufs ausgegeben
und identifizieren ihn eindeutig.
