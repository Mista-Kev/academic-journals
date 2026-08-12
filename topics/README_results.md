# topic_match — Ergebnisse und wie es weitergeht

Ich habe den Embedding-Lauf durchgezogen (SPECTER2 + Kernel), diesmal über alle
Autoren mit mindestens 3 Papern, nicht mehr nur die Stichprobe. Die Ergebnisse
liegen bei mir im Ordner `results/`. Kurz, was drin ist und was ihr damit macht.

topic_match ist einfach eine Zahl zwischen 0 und 1, die sagt, wie gut zwei Paper
(oder ein Autor und ein Journal) thematisch zusammenpassen. 1 = gleiches Thema,
0 = nichts miteinander zu tun.

Bitte immer über die IDs verbinden (work_id, author_id, journal_id), nie über
die Namen — die sind nicht eindeutig, da hatten wir uns ja drauf geeinigt.

## Was ich euch dagelassen habe

Drei Dateien:

- **keys_author_paper.csv** — jede Autor-Paper-Zeile mit allen IDs. Das ist die
  Basis für den Logic-Teil, daraus zieht ihr euch die Fakten selbst.
- **results_q1_topic_match.csv** — pro Autor und Journal, wie ähnlich seine
  Paper dort thematisch sind. Das ist für Q1.
- **results_topic_match_temporal.csv** — das Wichtige für den Bayes-Teil. Pro
  Ereignis steht drin, wie gut das Thema des Autors zum Journal passte, und zwar
  zum jeweiligen Zeitpunkt. Ich rechne das nur aus Papern **vor** dem Zeitpunkt,
  damit wir nichts aus der Zukunft reinziehen (sonst hätten wir ein
  Leakage-Problem in der Defense).

Die Spalten:
- keys: `work_id, year, journal_id, journal_name, publisher_id, in_doaj, author_id, author_name`
- q1: `author_id, journal_id, n_papers, topic_match_intra, work_ids`
- temporal: `author_id, journal_id, t, work_id, topic_match_t`

## Was der Probabilistic-Teil damit machen muss

Ihr braucht vor allem die **temporal**-Datei. Die Spalte `topic_match_t` ist
unser Thema-Wert, also der Knoten T im Bayes-Netz. So würde ich vorgehen:

1. Die temporal-Datei laden. `topic_match_t` ist die Themen-Variable T.

2. An eure Ereignisse aus dem Logic-Teil dranjoinen (über work_id). Der
   Logic-Teil liefert ja pro Ereignis: hat ein Koautor dort schon vorher
   publiziert (C), und ist es der erste Eintritt des Autors (E).

3. Aus dem Thema-Wert ein Ja/Nein machen: über einer Schwelle (ich würde mit
   0,85 anfangen) heißt „Thema passt", darunter nicht. Oder ihr nehmt die Zahl
   direkt als Wahrscheinlichkeit, wenn ihr mit Soft Labels arbeiten wollt.

4. Achtung bei leeren Werten: wenn `topic_match_t` leer ist, war das der erste
   Auftritt (vorher kein Paper, also kein Profil). Das bitte **nicht als 0**
   nehmen — entweder rauslassen oder als eigene Gruppe behandeln.

5. Dann euer Bayes-Netz mit T, C, E bauen und mit dem do-Operator rechnen: wie
   oft tritt jemand ein, wenn ein Koautor gesät hat, gegenüber wenn keiner gesät
   hat — bei gleichem Thema. Die Q3-Zahl ist am Ende P1 durch P0.

## Was noch offen ist

- Der Vergleichswert für Q1 fehlt mir noch (Thema im selben Journal gegen Thema
  bei Journalwechsel). Mache ich als Nächstes.
- Die Schwelle in Schritt 3 sollten wir zusammen festlegen.
- Und wir müssen kurz abgleichen, dass eure Ereignis-Zeitpunkte und mein t
  wirklich dasselbe meinen, sonst passt der Join nicht sauber.

Meldet euch, wenn beim Join was hakt.
