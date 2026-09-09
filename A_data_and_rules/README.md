# A · Daten und Regeln

**Lennarts Teil:** gemeinsame Paperdaten und nachvollziehbare historische Regeln.
Eine Zeile im Korpus ist ein Paper. Die Publikationspfade beziehen sich dagegen
auf Autor-Paper-Paare. Die jährliche Prolog-Gegenprüfung ist eine zweite Rechnung
mit derselben Gelegenheitendefinition wie B.

| Schritt | Code | Eingang → Ausgang |
|---|---|---|
| Abruf und Aufbereitung | `OpenAlex_AI_Dataset_v1_0.ipynb` | OpenAlex → `data/openalex_ai_raw_v1_0.jsonl`, `data/openalex_ai_semiclean_v1_0.csv` |
| Pfade mit Belegen | `logic/openalex_three_path_prolog.py`, `logic/openalex_three_path_rules.pl` | Paperdaten → `results/openalex_three_path_v1_0/` |
| Jährliche Gegenprüfung | `logic/check_event_table_parity.py`, `logic/event_table_rules.pl` | Prolog-Fakten → `data/event_table_prolog_v0_oppA.csv` |

Für die Demo werden die eingefrorenen Daten verwendet. Ein neuer OpenAlex-Abruf
kann andere Daten ergeben und reproduziert nicht automatisch den alten Korpus.
B verwendet die Paperdaten für Q1/Q2 und den Gelegenheitsnenner von Q3.
C verwendet Titel, Abstracts und historische Zugehörigkeiten für die Profile.

Die Pfade prüfen zeitliche Regeln, keine kausale Wirkung. In Q3 muss derselbe
frühere Koautor sowohl die Verbindung begründen als auch auf dem Eintrittspaper
stehen, damit es ein Ride ist. Details: [Regeln](logic/README.md).

[Vorführen und neu rechnen](../D_results/DEMO.md) · [Gesamtüberblick](../README.md)
