# Vorgehensweise, Historie und Entscheidungen

Der aktuelle Einstieg ist die [Root-README](../../README.md), die Ergebnisse
stehen [in D](../README.md). Für die Begründungen:

- [Entscheidungslog](decisions.md): datierte Entscheidungen; ein Vorschlag ist keine bestätigte Teamentscheidung.
- [Q3-Struktur](q3-structure.md): Variablen, zeitliche Ordnung und Annahmen.
- [Datenzugriff](shared-data.md): verifizierte gemeinsame Eingaben.
- [Plan](plan.md), [Research notes](research-notes.md) und [Feedback](feedback-log.md): historische Anforderungen und Diskussion, kein Beleg des aktuellen Implementierungsstands.

Die aktuelle Umsetzung von Q3 ist Regression mit Standardisierung. Ein kausaler
Graph oder ein alter Plan für Bayes-Netze in Logtalk ist kein ausführbares BN-System.
Die Repo-Umstellung ändert weder diese Implementierung noch den zugesagten Umfang.

Der aktuelle Jahresvertrag mit 15 Spalten steht unter
[B/schemas/event_table.md](../../B_opportunities_and_analysis/schemas/event_table.md).
Er wurde aus dem lokalen Schema-Stand `40be940` übernommen und gegen die
v5-Eingabedatei geprüft. Der frühere paperbezogene Entwurf wird nicht parallel
als aktueller Vertrag geführt.
