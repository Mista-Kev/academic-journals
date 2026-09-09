# Gemeinsam vorführen und erklären

Vom Repository-Root aus arbeiten. Einmal Pakete installieren und den eigenen
SharePoint-Download oder synchronisierten Ordner konfigurieren, wie in der
Root-README beschrieben. Kein OpenAlex-Abruf und kein GPU-Neulauf ist nötig,
um die vorhandenen Ergebnisse nachzurechnen.

## Zehn Minuten mit drei Verantwortlichen

1. **Lennart, A:** ein Paper, seine Autoren und einen belegten historischen Pfad
   zeigen. Autor-Paper-Pfade von jährlichen Gelegenheiten unterscheiden.
2. **Kevin, B:** eine Gelegenheit ohne Eintritt erklären. Sie liefert den Nenner.
   Q1/Q2 laufen lassen und sagen, was im Jahr-/Themen-Vergleich gezogen wird.
3. **Pierre, C:** historische Profile vor Jahr t und einen fehlenden T-Wert
   erklären. Den separaten Q1-Intra-Wert von historischem T unterscheiden.
4. **Kevin, B:** Q3 laufen lassen. 3,34 neben 1,18 und 6,09 neben 2,27 zeigen,
   inklusive unterschiedlicher Populationen und Ausschluss im Sensitivitätsmodell.
5. **Gemeinsam, D:** eine Kernaussage und ihre Grenze nennen. Regelparität,
   statistische Berechnung und kausale Gültigkeit sind verschiedene Prüfungen.

```sh
python3 demo.py q1-q2
python3 demo.py q3
```

Diese Befehle führen alle Python-Zellen der jeweiligen Notebooks frisch aus und
geben ihre Ergebnisse im Terminal aus. Sie verändern weder die Statistikzellen
noch die gespeicherten Notebook-Ausgaben. Für die grafische Notebookansicht die
Datei aus B öffnen und B als Kernel-Arbeitsverzeichnis verwenden.

## Regeln prüfen

SWI-Prolog muss installiert sein. Die kleinen Unit-Tests benötigen keine großen
Daten; einige Tests verwenden SWI-Prolog und werden ohne Installation übersprungen.

```sh
TMPDIR=/private/tmp python3 -m unittest discover -s A_data_and_rules/logic/tests -v
python3 project_data.py fetch --group parity
python3 B_opportunities_and_analysis/diff_event_table.py
```

Die zweite Prüfung vergleicht alle Zeilen der freigegebenen Python-/Prolog-
Tabellen. Eine neue Konstruktion beider Tabellen ist ein zusätzlicher Test.
Dafür einen separaten Checkout/Arbeitsordner verwenden, weil die Builder ihre
abgeleiteten Dateien schreiben:

```sh
python3 project_data.py fetch --group corpus
python3 A_data_and_rules/logic/openalex_three_path_prolog.py --data-dir A_data_and_rules/data --out-dir A_data_and_rules/results/openalex_three_path_v1_0
python3 B_opportunities_and_analysis/build_event_table.py
python3 A_data_and_rules/logic/check_event_table_parity.py --fixtures-only
python3 A_data_and_rules/logic/check_event_table_parity.py
python3 B_opportunities_and_analysis/diff_event_table.py
```

Danach `python3 project_data.py verify --group parity` ausführen, um zusätzlich
die eingefrorenen Dateihashes zu prüfen. Unterschiedliche Serialisierung kann bei
Prolog-Ausgaben trotz semantischer Gleichheit einen anderen Hash ergeben; niemals
den Manifest-Hash nur zum Beseitigen eines Fehlers überschreiben.

## Grenzen der Demo

Die Eingabeprüfung und Analysen laufen mit der festen Datenfreigabe offline,
sobald die Dateien geladen wurden. Zugriff als Felix muss mit seinem eigenen
Konto/Download funktionieren; unser Lauf prüft seine Berechtigung nicht.
Der C-Neulauf braucht die im C-README beschriebene DuckDB-/Colab-/GPU-Umgebung.
Ein ausführbares Bayes-Netz ist in dieser Demo nicht enthalten.
