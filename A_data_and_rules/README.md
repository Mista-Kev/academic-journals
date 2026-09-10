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

## Frozen corpus: setup and checks

### Purpose

Create the frozen OpenAlex dataset used by the project.

The notebook applies the fixed filters:

- 64 journals
- 49 selected OpenAlex topics
- publication years 2015–2024
- work type `article`
- `is_retracted:false`
- journal as the primary source

### Run the notebook

1. Open `A_data_and_rules/OpenAlex_AI_Dataset_v1_0.ipynb` with `A_data_and_rules/` as the working directory.
2. Restart the kernel.
3. Run all cells from top to bottom.
4. If the raw JSONL file does not exist, enter an OpenAlex API key when prompted.
5. Wait for the download to finish.
6. Check the final dataset summary.

If the raw JSONL file already exists, the notebook reuses it. No API key is needed in that case.

The key may also be provided through `OPENALEX_API_KEY`.

### Output

The notebook writes these files to `data/` under its working directory, or to
the `OPENALEX_DATA_DIR` override when configured:

- `openalex_ai_raw_v1_0.jsonl`: unchanged OpenAlex work records
- `openalex_ai_semiclean_v1_0.csv`: one row per work with normalized IDs and JSON text fields

The recorded v1.0 run contains 27,400 works from 64 journals and 49 topics.

### Checks

The notebook stops when a blocking check fails. It checks:

- raw records were read successfully
- work IDs exist and are unique
- all works are articles
- no work is retracted
- publication years are within 2015–2024
- only the fixed journals and topics occur
- the written CSV has the expected row count
- duplicate DOIs are reported in the final summary

### Handoff

Both output files are now available to the logic layer. The raw JSONL provides publisher lineage. The semiclean CSV provides work and authorship data.
