# Q1–Q3: Eingaben, Berechnungen, Ausgaben und Begründungen

**Q1 und Q2 berücksichtigen beide Themenkategorien im zweiten Vergleichsmodell.**
Die kontinuierliche historische Themenpassung T aus Pierres Event-Tabelle wird
hingegen nur in Q3 verwendet. Die Q1/Q2-Zufallsziehungen erfolgen **mit Zurücklegen**:
Eine Ziehung verändert die Wahrscheinlichkeiten für die nächste Ziehung nicht.

Diese Beschreibung erklärt den implementierten Stand. Eine heute nachvollziehbare
Begründung ist kein Beleg, dass die Gruppe diese Entscheidung ursprünglich gemeinsam
getroffen hat. Die Berichtsposition für Kevins Teil und die vorgeschlagene gemeinsame
Übernahme sind im [Entscheidungslog](decisions.md) getrennt dokumentiert.

## 1. Welche Dateien gehen hinein und was kommt heraus?

Alle Pfade beziehen sich auf den Repository-Root. A steht für `A_data_and_rules/`,
B für `B_opportunities_and_analysis/`, C für `C_topic_match/` und D für `D_results/`.

| Rechnung | Ausführbare Datei | Eingaben | Ausgabe und Verwendung |
|---|---|---|---|
| Q1/Q2 | `B/q1_q2_baselines.ipynb` | `A/data/openalex_ai_semiclean_v1_0.csv`; `A/results/openalex_three_path_v1_0/journal_parent_publishers.csv`; dort auch `pathway_flags.csv` zur Gegenprüfung | Beobachtete Häufigkeiten, simulierte erwartete Häufigkeiten, deren Quotienten und Prüfungen; Notebook-Anzeige bzw. Terminal, Zusammenfassung in D |
| Gelegenheiten für Q3 | `B/build_event_table.py` | Derselbe Paperkorpus, Verlagsmapping und Pfadflags aus A | `B/data/event_table_python_v0_oppA.csv`; zusätzlich `event_table_python_v0_oppB.csv` als Sensitivitätsvariante |
| Unabhängige Jahresprüfung | `A/logic/check_event_table_parity.py` und `event_table_rules.pl` | `A/results/openalex_three_path_v1_0/openalex_three_path_facts.pl` aus dem Pfad-Wrapper | `A/data/event_table_prolog_v0_oppA.csv`; Vergleich mit B durch `B/diff_event_table.py` |
| Historische Themenpassung | `C/embeddings_colab_eventtable_v5.ipynb` | B-Gelegenheiten und Papertexte/-historien in Pierres DuckDB-/Colab-Umgebung | `C/data/event_table_topicmatch_v5.csv` für Q3; separater Q1-Intra-Export unter `C/results/results_q1_topic_match_v5.csv` |
| Q3 | `B/q3_baselines.ipynb` | B-Tabelle A und C-v5-Tabelle; `C/data/event_table_topicmatch_local_min3.csv` nur für den historischen Vergleich in Schritt 8 | Rohe und modellstandardisierte Risikoverhältnisse, Unsicherheit und Sensitivitäten; Notebook-Anzeige bzw. Terminal, Zusammenfassung in D |

A und B sind unterschiedliche Zeileneinheiten: Ein Paper kann mehrere Autor-Paper-
Paare erzeugen. Q1/Q2 verwenden 110.654 solcher Paare. Q3 verwendet 6.422.558
Autor-Journal-Jahr-Gelegenheiten, ausdrücklich auch ohne Publikation im Zieljournal.
Nach dem ersten beobachteten Eintritt endet das Autor-Journal-Paar in der Q3-Tabelle.
Sie ist deshalb keine Rückkehrtabelle für Q1.

Die Notebooks schreiben nicht automatisch eine neue Ergebnis-CSV in SharePoint.
`B/results/q3_v5/model_results.json` ist externe Referenzevidenz aus einem getrennten
Prüfpaket, kein Export des Q3-Notebooks. Der tatsächliche Dateikatalog mit vollständigen
Pfaden und Prüfsummen ist [data-manifest.json](../../data-manifest.json).

## 2. Was wird bei Q1/Q2 beobachtet?

Für jedes Autor-Paper-Paar fragen wir, was der Autor an **strikt früheren Tagen**
im Korpus bereits veröffentlicht hatte. Paper desselben Tages zählen nicht als
Vorgeschichte füreinander. Der Nenner ist jeweils 110.654, einschließlich der
Paare ohne frühere Publikation, die noch keine Wiederkehr sein können.

| Definition | Beobachtete Fälle | Beobachteter Anteil |
|---|---:|---:|
| Q1: früher im selben Journal | 12.325 | 0,1114 |
| Q2 weit: früher beim selben bekannten Mutterverlag, gleiches Journal erlaubt | 15.770 | 0,1425 |
| Q2 eng: früher beim selben Mutterverlag über mindestens ein anderes Journal | 4.919 | 0,0445 |

Q2 eng bedeutet nicht automatisch neues Journal: 1.468 dieser Fälle sind zugleich
Q1-Rückkehrfälle. Es bleiben 3.451 Fälle ohne Q1-Rückkehr. Für diese Teilmenge wurde
kein eigener passender Nullvergleich berechnet. Q2 weit ist stark mit Q1 überlagert.
Unbekannte Verlage erzeugen keinen positiven Verlagsfall; diese Zeilen bleiben im Nenner.

## 3. Wie wird „erwartet“ berechnet?

Im Notebook sind dafür `build_dist` und `null_rates` zuständig.

1. Aus **einmal gezählten Paperzeilen**, nicht Autor-Paper-Paaren, werden
   Journalgewichte gebildet. Null A zählt Paper je Journal und Jahr; Null B
   zählt Paper je Journal, Jahr und OpenAlex-Primärthemenkategorie.
2. Pro Autor bleiben Anzahl der Paper, Daten, Jahre und Kategorien bestehen.
   Jedem Autor-Paper-Platz wird ein Journal gemäß diesen Gewichten zugelost.
3. Die gesamte Journalgeschichte dieses Autors wird so neu aufgebaut. Es wird
   nicht nur das aktuelle Journal gegen die unveränderte reale Vorgeschichte gezogen.
4. Auf dieser simulierten Geschichte werden dieselben Q1/Q2-Regeln angewandt,
   einschließlich der strikten Datumsgrenze und des Verlagsmappings.
5. Das passiert 100-mal je Nullmodell mit festem Zufallsseed 42. Der Mittelwert
   der 100 simulierten Anteile ist der geschätzte erwartete Anteil.
6. Ergebnis: **beobachteter Anteil / mittlerer erwarteter Anteil**. Es ist nicht
   der Mittelwert von 100 einzelnen Quotienten. Weil der Nenner konstant bleibt,
   entspricht dies auch beobachtete Fallzahl / mittlere simulierte Fallzahl.

Beispiel Q1: 0,1114 beobachtet gegenüber ungefähr 0,0361 im Jahr-Nullmodell ergibt
ungefähr 3,09. Die exakte angezeigte Ratio verwendet ungerundete Werte.
Im Jahr-plus-Thema-Modell beträgt der erwartete Anteil ungefähr 0,0501 und die
Ratio 2,22. Die stärkere Konzentration auf passende Kategorien lässt bereits im
Nullmodell mehr Wiederkehr entstehen.

| Auswertung | Ratio: Jahr | Ratio: Jahr + Primärthema |
|---|---:|---:|
| Q1 | 3,09 | 2,22 |
| Q2 weit | 2,02 | 1,69 |
| Q2 eng | 1,16 | 1,11 |

## 4. Mit oder ohne Zurücklegen?

**Mit Zurücklegen, genauer: unabhängige gewichtete Ziehungen aus unveränderten
Wahrscheinlichkeitstabellen.** Im Code wählt `rng.random()` über die kumulierten
Gewichte ein Journal aus. Es gibt keinen Schritt, der das gewählte Journal oder
sein Gewicht aus dem Pool entfernt. Dasselbe Journal kann erneut gewählt werden.

Anschaulich hat ein Topf zwei Lose für Journal A und eines für Journal B.
Bei zwei Ziehungen mit Zurücklegen ist die Wahrscheinlichkeit für dasselbe Journal
`(2/3)² + (1/3)² = 5/9`. Die erste Ziehung ist noch keine Wiederkehr; bei zwei
zeitlich getrennten Publikationsplätzen ist der erwartete Wiederkehranteil daher
`(5/9)/2 = 5/18`. Dieses Beispiel wurde mit den tatsächlichen Notebook-Funktionen
und kontrollierten Zufallswerten geprüft; es ist keine neue Schätzung des Korpus.

Es gibt zwei unterschiedliche Alternativen, die man nicht verwechseln sollte:

- **Jedes Journal höchstens einmal ziehen:** Das würde Wiederkehr verhindern und
  wäre für die Frage nach zufällig entstehender Journalwiederkehr kein sinnvoller Vergleich.
- **Endliche Paper-/Journal-Lose ohne Zurücklegen verteilen:** Das kann weiterhin
  Wiederkehr erlauben, solange mehrere Lose dasselbe Journal tragen. Im Beispiel
  beträgt die Wiederholungswahrscheinlichkeit dann `2/3 × 1/2 = 1/3`.
  Eine passend konstruierte Permutation realer Paperplätze könnte die beobachteten
  Journalgrößen je Jahr/Kategorie exakt erhalten. Das ist eine legitime andere Null,
  nicht die implementierte Rechnung. Ihre Randbedingungen müssten definiert werden.

Der implementierte Vergleich ist nachvollziehbar als Modell unabhängiger
Journalzuweisungen mit festen, aus dem Korpus geschätzten Gewichten. Er benötigt
keine erschöpfbare Zahl verfügbarer Plätze. Damit ist nicht bewiesen, dass reale
Publikationsentscheidungen unabhängig sind oder diese Null die einzig richtige ist.
Journalhäufigkeiten werden in einer Simulation nicht exakt fixiert.

Wichtig für die Modellgrenze: Gewichte stammen aus Paperzahlen, gezogen wird pro
**Autor-Paper-Paar**. Dasselbe gemeinsame Paper kann in den simulierten Geschichten
zweier Koautoren verschiedene Journale erhalten. Der Vergleich simuliert einzelne
Autorenhistorien und kein gemeinsames, konsistentes Publikationsnetz. Er erhält die
Paperzahl pro Autor, aber nicht die gemeinsame Journalzuweisung eines Koautorenpapers.
Eine alternative Null mit einer gemeinsamen Ziehung je Paper wäre eigens zu prüfen.
Es gibt keinen Beleg, dass diese Alternativen früher ausdrücklich abgewogen und
verworfen wurden. Heute können wir die implementierte Null und ihre Grenzen erklären.

## 5. Welche Art von „Thema“ ist wo enthalten?

| Information | Q1/Q2 | Q3 |
|---|---|---|
| OpenAlex-Primärthemenkategorie des Papers | Im zweiten Nullmodell für **beide** Fragen | Nicht gleichbedeutend mit dem kontinuierlichen T |
| Historischer Autor-Journal-Topic-Match T | Nicht verwendet | Kovariate im Modell, sofern berechenbar |
| Pierres `topic_match_intra` | Separate Beschreibung beobachteter Autor-Journal-Gruppen; kein Faktor in der Ratio | Kein Ersatz für historisches T |

Kategorien berücksichtigen grobe thematische Konzentration. Sie messen nicht,
wie gut das frühere Forschungsprofil eines Autors zu einem bestimmten Journal
und dessen Alternativen passt. Die Kategorien können selbst Venue-Information
tragen; die Konditionierung ist deshalb keine Garantie einer kausalen Bereinigung.
Historisches T für Rückkehrfälle und Alternativjournale müsste neu aufgebaut werden.
Q3s vor dem Ersteintritt endende Tabelle und Q1-Intra liefern diesen Vergleich nicht.

## 6. Q3 rechnet einen anderen Vergleich

Zuerst werden jährliche Gelegenheiten konstruiert. C zeigt eine bereits vor Jahr t
bestehende Koautoren-Verbindung zum Zieljournal an. Derselbe frühere Koautor muss
die Verbindung und seine frühere Journalpublikation belegen. Die Eintrittsvariable
F wird aus `entering_work_id` gebildet. Non-ride ist ein Eintritt ohne qualifizierenden
Seed-Koautor auf dem ausgewählten Eintrittspaper; es ist kein allgemeiner direkter Effekt.

Die B- und C-Dateien werden vor der Verbindung auf dieselben Autor-/Journal-/Jahr-
Schlüssel in derselben Reihenfolge geprüft. T muss für seinen Profilinhalt strikt
frühere Jahre verwenden. Fehlendes T bleibt fehlend. Die adjustierten Modelle
verwenden 1.106.356 vollständige Fälle, keine Imputation und keine Nullkodierung.

- **Roh:** Eintrittsanteil unter C=1 geteilt durch Eintrittsanteil unter C=0.
- **C+T:** Logistische Regression mit Konstante, C und kontinuierlichem T.
  Danach wird für jede eingeschlossene Zeile einmal C=1 und einmal C=0 eingesetzt,
  bei gleichem T. Die vorhergesagten Wahrscheinlichkeiten werden je Szenario gemittelt;
  ihr Quotient ist das standardisierte Risikoverhältnis. Das ist nicht einfach
  `exp(beta_C)`, denn das wäre ein Odds Ratio.
- **Non-ride:** `Y = first_entry * (1 - first_entry_ride)` wird auf denselben
  Gelegenheitszeilen modelliert. Beide gemittelten Risiken stammen aus diesem
  einen Modell. Wir teilen nicht einen Non-ride-Zähler durch einen Nenner aus
  einem separat geschätzten All-entry-Modell. Ride-Zeilen bleiben enthalten und
  erhalten für dieses Outcome den Wert 0. „Independent“ bedeutet hier non-ride,
  nicht Unabhängigkeit von Netzwerkeinflüssen.
- **Journal-/Jahressensitivität:** Zusätzlich separate additive Journal- und
  Jahreseffekte. Ein Journal ohne Eintritte wird mit 17.936 Zeilen ausgeschlossen,
  um Separation zu behandeln. Auf denselben verbleibenden 1.088.420 Zeilen wird
  auch C+T erneut gerechnet. Der Ausschluss ist am Outcome orientiert.

| Ergebnis | C+T: vollständige Fälle | C+T: gleiche Sensitivitätszeilen | Zusätzlich Journal und Jahr |
|---|---:|---:|---:|
| Alle Eintritte | 6,09 | 6,01 | 2,27 |
| Non-ride | 3,34 | 3,30 | 1,18 |

Die C+T-Intervalle verwenden eine nach Autoren geclusterte Delta-Methode.
Das weicht vom früheren Bootstrap-Plan ab; für v5 wurden keine neuen
Bootstrap-Refits berechnet. Autoren-Clustering deckt gemeinsame Journal- oder
Paperabhängigkeiten nicht vollständig ab. Die geprüften erweiterten Zweiweg-
Kovarianzen waren nicht positiv semidefinit. Die Risikoverhältnis-Intervalle sind
auch kein Bootstrap-Likelihood-Ratio-Test der früher geplanten Nullhypothese.
Q1/Q2s 100 Nullsimulationen sind dagegen keine Konfidenzintervalle der beobachteten
Ratios. Ein Wert nahe eins beweist keinen fehlenden Zusammenhang.

Warum diese Q3-Schritte? Nicht-Eintritte liefern den benötigten Nenner; das Jahr
legt fest, was als vorher bekannt zählt; T berücksichtigt eine beobachtete thematische
Passung; Journal/Jahr prüfen eine wichtige Modellabhängigkeit. Diese Gründe machen
das Adjustierungsset nicht automatisch ausreichend. T kann zeitlich nach früherer
Zusammenarbeit liegen; vollständige Fälle sind selektiert, und unbeobachtete Faktoren
bleiben möglich. Deshalb berichten wir Zusammenhänge, keinen nachgewiesenen kausalen Effekt.

## 7. Was sollten wir gemeinsam erklären können?

Jeder sollte den Weg von A über B/C nach D nachvollziehen können, auch wenn die
Implementierungsverantwortung aufgeteilt ist. Für die gemeinsame Abstimmung:

1. Welche Zeile zählt bei Q1/Q2, welche bei Q3? Warum braucht Q3 Nicht-Eintritte?
2. Was bleibt im Nullmodell fest, was wird neu gezogen und mit welchen Gewichten?
3. Warum erlauben die Ziehungen Wiederkehr? Welche andere Frage würde eine
   Permutation mit exakt erhaltenen Journalzahlen stellen?
4. Welche Themeninformation ist enthalten und welche stärkere Aussage bleibt offen?
5. Warum verändern Journal/Jahr die Q3-Aussage erheblich?
6. Was zeigen Gegenprüfungen, und welche wissenschaftlichen Annahmen prüfen sie nicht?
7. Welche Berichtsentscheidungen übernehmen wir gemeinsam, und welche sind bisher
   nur für Kevins Teil festgelegt?

Diese Fragen erfordern eine gemeinsame verständliche Darstellung, nicht die
Behauptung einer früheren Abstimmung. Die [Demo-Anleitung](../DEMO.md) enthält die
Befehle. Für die Datenübergabe gilt [shared-data.md](shared-data.md): Dateien laden
und prüfen, lokal rechnen, neue Ergebnisse bewusst freigeben.
