# topic_match — Ergebnisse und Übergabe

Was der ML-Layer liefert, welche Zahlen dabei herauskommen und was die anderen
beiden Layer damit machen. Wie das Notebook arbeitet, steht in `README.md`.

> **Achtung, diese Datei wurde vollständig ersetzt.** Die frühere Fassung
> beschrieb einen Stand vor der Ereignis-Tabelle und enthielt Anweisungen,
> die inzwischen widerlegt sind. Was daraus **nicht mehr gilt**, steht unten
> unter „Zurückgezogene Anweisungen". Bitte kurz lesen, falls ihr danach
> gearbeitet habt.

---

## Was ihr bekommt

**Eine Datei:** `event_table_topicmatch_v5.csv`, geteilt über Teams.

> Das Notebook schreibt auf den unversionierten Pfad `event_table_topicmatch.csv`;
> die geteilte Datei wird **von Hand** umbenannt. Achtet deshalb auf den Namen:
> eine Datei ohne `_v5` ist der alte Stand **mit** Schwelle und nicht mehr zu verwenden.
> Im Zweifel die vier Kennwerte unten prüfen — die sind eindeutig.

Das ist die Ereignis-Tabelle des Logic-Layers, unverändert in Zeilenzahl und
Reihenfolge, mit fünf zusätzlich gefüllten Spalten. 6.422.558 Zeilen, 15 Spalten.

| Spalte | Bedeutung |
|---|---|
| `topic_match` | Themenpassung Autor zu Journal, 0 bis 1. **Leer, wenn kein Profil existiert.** |
| `n_profile_papers` | Paper des Autors strikt vor t |
| `n_journal_papers` | Paper des Journals strikt vor t — hängt nur am Journal-Jahr, nicht am Autor |
| `profile_cutoff` | letztes Jahr im Autorenprofil (nicht pauschal t−1) |
| `tm_status` | Grund, falls `topic_match` leer ist |

Verbindung immer über die IDs in Kurzform (`A5060045903`), nie über Namen.

Für Q1 zusätzlich: `results_q1_topic_match_v5.csv` — 9.195 Autor-Journal-Zeilen mit
`topic_match_intra`, der mittleren Themenähnlichkeit der Paper eines Autors
innerhalb eines Journals.

Abgelöste Fassungen liegen in `Results/archive/` mit einem `MANIFEST.md`, das für
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

> **v5 reproduziert die Läufe unten nicht.** `sig2` 0,3635 gegen 0,3611, Mittelwert 0,767
> gegen 0,785574. Die Zahlen 5,69 und 6,09 stammen aus einem lokalen v4-Lauf, der nicht im
> Repo liegt. Wahrscheinlichste Ursache ist der Adapter — Test ausstehend, siehe `README.md`.

### Ältere Läufe — Kevins Messung

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

### Warum 90 Prozent leer sind

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

## Was der Probabilistic-Layer damit macht

1. **`event_table_topicmatch_v5.csv` laden.** C und F stehen schon drin, T ist die
   Spalte `topic_match`. Kein Join nötig, es ist dieselbe Tabelle.

2. **`topic_match` stetig verwenden.** Keine Schwelle, keine Binarisierung.
   Der Wert geht als reelle Zahl ins Modell.

3. **Nur Zeilen mit gültigem T.** Vollständige Fälle. Zeilen mit leerem
   `topic_match` fallen aus der Regression heraus — sie werden nicht ersetzt und
   nicht als eigene Kategorie geführt.

4. **Modell `F ~ C + T` schätzen**, dann zweimal auf **dieselben** Zeilen anwenden:
   einmal mit C = 1, einmal mit C = 0, bei jeweils unverändertem realen T. Die
   beiden gemittelten Risiken teilen.

   ```
              Mittelwert über T von P(F = 1 | C = 1, T)
   RR   =   ---------------------------------------------
              Mittelwert über T von P(F = 1 | C = 0, T)
   ```

5. **Die vereinbarte Kennzahl** nimmt im Zähler nur die eigenständigen Eintritte
   (`first_entry_independent`), im Nenner alle. Unter C = 0 ist jeder Eintritt
   ohnehin eigenständig, dort braucht es keine Aufteilung.

6. **Aufteilen, nicht filtern.** Zeilen mit gemeinsamem Eintritt
   (`first_entry_ride`) bleiben im Datensatz. Ob der Wegbereiter auf dem
   Eintrittspaper landet, ist selbst eine Folge von C — ein Filter darauf würde
   nach der Behandlung auswählen.

7. **Konfidenzintervall über einen Bootstrap über Autoren**, nicht über Zeilen.
   623.510 Zeilen sind keine 623.510 unabhängigen Beobachtungen; ein Autor
   erzeugt viele davon. Rechnet man mit der Zeilenzahl, wird das Intervall zu eng.

**Bisheriger Stand:** 5,24 mit Schwelle, 5,69 ohne Schwelle auf denselben Zeilen,
6,09 ohne Schwelle auf der vollen Population. Die Kennzahl für eigenständige
Eintritte fehlt noch.

**Achtung, diese Zahlen sind zu erneuern.** Der v5-Lauf füllt 1.106.356 Zeilen statt
623.510 — 77 % mehr. Q3 ist auf der neuen Spalte neu zu rechnen.

**Übergabeobjekt ist die CSV, nicht das Notebook.** Der ML-Layer erzeugt
`event_table_topicmatch.csv`, der Probabilistic-Layer liest sie. Ein Nachrechnen der
Embeddings auf einer anderen Maschine erzeugt andere Werte, wie der Vergleich oben zeigt.
Zur Prüfung gibt der Lauf am Ende vier Kennwerte aus — `MIN_PAPERS`, `sig2`, Mittelwert
und Zeilenzahl. Stimmen die mit der gelieferten Datei überein, ist es dieselbe Spalte.

---

## Was der Logic-Layer davon braucht

Wenig — die Richtung läuft überwiegend andersherum. Zwei Punkte:

- **`n_journal_papers`** ist ab v4 eine Eigenschaft des Journal-Jahres und für
  **alle** Zeilen gefüllt, auch für die ohne `topic_match`. Als Kontrollgröße für
  Journalgröße nutzbar. Achtung: Ab v5 zählt sie alle einbettbaren Paper des
  Journals, vorher nur die der ausgewählten Autoren — die Bedeutung ändert sich,
  der Spaltenname bleibt.

- **`topic_match_intra`** aus `results_q1_topic_match_v5.csv` beantwortet die Frage,
  ob Journaltreue thematisch getrieben ist. Noch nicht ausgewertet.

---

## Zurückgezogene Anweisungen

Die frühere Fassung dieser Datei enthielt vier Punkte, die **nicht mehr gelten**.
Falls ihr danach gearbeitet habt, bitte prüfen:

| Alt | Warum verworfen |
|---|---|
| „Aus dem Thema-Wert ein Ja/Nein machen, Schwelle 0,85" | Willkürliche Grenze, Informationsverlust. T geht stetig ins Modell. |
| „Leere Werte als eigene Gruppe behandeln" | Per Simulation widerlegt (400.000 Zeilen, drei Fehlmechanismen). Eine Kategorie „fehlt" korreliert mit dem Ergebnis und bringt den Störfaktor zurück ins Modell. Vollständige Fälle gewinnen in allen Szenarien. |
| „`keys_author_paper.csv` ist die Basis für den Logic-Teil" | Überholt. Zentrales Verbindungsobjekt ist die Ereignis-Tabelle. Q3 braucht die nicht realisierten Kombinationen als Nenner; die Publikationstabelle hat sie nicht. |
| „An eure Ereignisse dranjoinen über `work_id`" | Entfällt. Der ML-Layer schreibt direkt in die Ereignis-Tabelle, es gibt keinen Join mehr. |

Ein Punkt aus der alten Fassung gilt weiter und ist wichtiger geworden:
**leere Werte niemals als 0 behandeln.**

---

## Offen

- **Adapter-Test.** v5 ohne aktiven Adapter laufen lassen und prüfen, ob `sig2`
  auf 0,3611 fällt. Damit wäre die Abweichung zu den früheren Läufen erklärt.
- **Q3 neu rechnen** auf der v5-Spalte. Die Population ist 77 % größer.
- **Dateinamen im Notebook versionieren**, damit die Umbenennung nicht von Hand
  passieren muss.
- **Kennzahl für eigenständige Eintritte** rechnen. Das ist die vereinbarte
  Kopfzahl, nicht 6,09.
- **Bootstrap über Autoren** für das Konfidenzintervall.
- **Adapter-Vergleich** als Robustheitsprüfung dokumentieren.
- **Themenpassung für Q1 und Q2** — Anfrage aus der Besprechung mit dem Professor.
  `topic_match_intra` liegt vor, ist aber nicht ausgewertet.
