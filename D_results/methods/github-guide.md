# Änderungen gemeinsam übergeben

Ein Repository, eine Root-README und A/B/C als Arbeitsbereiche. D führt die
Ergebnisse und Begründungen zusammen. Code und Dokumentation werden über einen
Branch und einen geprüften PR veröffentlicht.

| Inhalt | Ort |
|---|---|
| Abruf und Prolog | A_data_and_rules/ |
| Gelegenheitstabelle und Q1/Q2/Q3 | B_opportunities_and_analysis/ |
| Themenprofile und Intra-Auswertung | C_topic_match/ |
| Ergebnisse, Ablauf und Entscheidungen | D_results/ |
| Große Daten und neue Exporte | SharePoint, mit den A/B/C-Pfaden des Manifests |

Vor einer Änderung auf `git status` achten und eigene oder fremde lokale Arbeit
bewahren. Für die laufende Umstellung einen eigenen Worktree verwenden. Keine
historischen Branches ungeprüft über die neuen Pfade schreiben.

Die großen Eingaben werden nicht in Git aufgenommen. Bereits versionierte
Referenzausgaben bleiben bei dieser Umstellung erhalten; die Git-Historie wird
nicht umgeschrieben. Neue geprüfte Datenfreigaben erhalten einen abgestimmten
Manifest-Eintrag und werden über `project_data.py stage` vorbereitet.
[Anleitung](shared-data.md).

Zugangsdaten und `.shared-data.local.json` bleiben lokal. Vor einem PR die
betroffenen Demo-Befehle und `git diff --check` ausführen. Ein erfolgreicher
Daten-/Code-Test ist keine Zustimmung des Teams zu einer Methodenentscheidung.
