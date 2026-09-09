# A · Regeln und unabhängige Gegenprüfung

**Verantwortlich:** Lennart (Prolog-Regeln); Kevin (Python-Gegenstücke).
Die Eingabe ist der Korpus in `../data/`. Der Wrapper
`openalex_three_path_prolog.py` und `openalex_three_path_rules.pl` erzeugen die
Publikationspfade pro Autor-Paper-Paar mit strikt früheren Datumsangaben.
Die Ergebnisse und Fakten liegen bei Verwendung der Demo-Befehle unter
`../results/openalex_three_path_v1_0/`.

`check_event_table_parity.py` und `event_table_rules.pl` erzeugen unabhängig
jährliche Autor-Journal-Gelegenheiten einschließlich Nicht-Eintritten. Die Ausgabe
liegt in `../data/event_table_prolog_v0_oppA.csv`. Der Python-Builder und der
Vollvergleich stehen in `../../B_opportunities_and_analysis/`.

[Ausführen und prüfen](../../D_results/DEMO.md) · [Aktuelle Jahresdefinitionen](../../B_opportunities_and_analysis/schemas/event_table.md)
