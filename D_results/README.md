# D · Ergebnisse und Interpretation aus A–C

Diese Seite führt die vorhandenen Auswertungen zusammen. Eingaben und exportierte
Resultate bleiben beim erzeugenden Teil in A/B/C. Es gibt keine vierte Analyse D.

| Auswertung | Ergebnis | Zulässige Aussage |
|---|---|---|
| A/B: jährliche Regeln | 6.422.558 Gelegenheiten, 96.819 Eintritte, 1.784 mit Seed, davon 756 Rides | Python und Prolog prüfen dieselben Regeln unabhängig; Übereinstimmung beweist keine Kausalität |
| Q1 | Ratio 3,09 nach Jahr; 2,22 nach Jahr + Themenkategorie | Mehr Journalwiederkehr als unter diesen Vergleichsmodellen |
| Q2 weit | 2,02 / 1,69 | Mehr Verlagswiederkehr einschließlich Journalwiederkehr |
| Q2 eng | 1,16 / 1,11 | 1.468 der 4.919 Fälle sind zugleich Journalwiederkehr; kein isoliertes Verlagssignal |
| C: Q1 Intra | 9.195 Autor-Journal-Gruppen | Thematische Ähnlichkeit innerhalb beobachteter Gruppen, keine historische Rückkehr-Adjustierung |
| Q3_all, C+T | 6,09 [5,76; 6,45] | Modellbasierter Zusammenhang auf 1.106.356 Zeilen mit messbarem T |
| Q3_ind, C+T | 3,34 [3,12; 3,58] | Eintritt ohne qualifizierenden Seed-Koautor auf dem Eintrittspaper; keine allgemeine Unabhängigkeit |
| Q3_all, gleiche 1.088.420 Zeilen | C+T 6,01 → mit Journal und Jahr 2,27 | Deutliche Spezifikationsabhängigkeit |
| Q3_ind, gleiche 1.088.420 Zeilen | C+T 3,30 → mit Journal und Jahr 1,18 | Die kleinere Schätzung gehört neben das T-only-Ergebnis |

Q3 verwendet Pierres offiziellen v5-Export (SHA-256 beginnt `8a9e8a92`). Die
Intervalle der T-adjustierten Modelle verwenden eine nach Autor geclusterte
Delta-Methode. Die Journal-/Jahresmodelle haben separate additive Effekte,
keine Journal×Jahr-Interaktionen. Ein Journal ohne Eintritte wurde dort mit
17.936 Zeilen ausgeschlossen, um Separation zu behandeln. Das ist eine am
Outcome orientierte Einschränkung, keine neutrale Datenbereinigung.

**Noch zu bestätigen:** C+T für Q3_ind als Berichts-Hauptmodell mit Sensitivität
unmittelbar daneben; Umgang mit fehlendem T. Die Tabellen zeigen bewusst beide
Spezifikationen. Ein Rerun ersetzt diese methodische Entscheidung nicht.

Q1/Q2 erhalten keine neue historische T-Adjustierung durch Pierres Intra-Datei.
Mit den vorhandenen Auswertungen können wir die beschreibenden Fragen abschließen,
sofern wir diesen Umfang gemeinsam festhalten. Thematisch unabhängige Treue wäre
eine zusätzliche Fragestellung mit einer neuen Rückkehr-/Alternativen-Tabelle.

[Demo](DEMO.md) · [Vorgehensweise und Entscheidungen](methods/README.md) · [Start](../README.md)
