"""python event table for q3. one row per (author, journal, year) where the author could have entered the
journal and either did or did not. lennart's prolog build is the canonical one for the report. this one
exists to give pierre t_first_seed now. parity against the prolog build is still pending, so nothing
here is cross checked by it yet."""

# every history here is internal to the corpus, so 64 journals and 2015 to 2024. n_prior_papers counts
# corpus papers only, co authorship outside these journals is invisible, and a pre 2015 entry cannot be
# seen. whether q3 needs history from outside the corpus is a data question, not one this script settles.

# years, not days. history is the years strictly before t and the outcome is year t. openalex fills a
# missing day and month with january 1, which is 28.6% of this corpus, so finer order would be invented.
# pathway_flags.csv is day level, so these counts land near it rather than on it.

# a row exists for (a, J, t) when a published in year t and had no J paper in an earlier year. a pair
# stops producing rows once it enters. seed C is 1 when an earlier co author of a published in J before t,
# both halves strictly before t. t_first_seed is the min over those co authors of the later of the two
# years. it belongs to the pair and not to the row, so C is 1 exactly when t_first_seed < t. a filled
# t_first_seed is usually the same year as t or later, which is future information sitting on the row, so
# mask it wherever C is 0 before using it predictively. entry F is 1 when a publishes in J in year t and
# never before.
# entering_work_id is the earliest such paper of that year, ties going to the lowest work id as a string.

# first_entry_ride is 1 when the same co author who qualifies the seed is also on the entering paper.
# first_entry_independent is its complement on entry rows, so it is 1 for the entries with no seed at all
# and it only ever means not a ride. the contrast to report is ride against independent within C = 1.

# opportunity set is decision 52 and still open. both get built and neither is preferred. variant a is all
# 64 journals minus the ones already entered. variant b keeps the journals that published one of the
# author's earlier primary topics in year t and falls back to a when the author has no earlier paper.
# 81.9% of author years fall back on this corpus, so b restricts much less than the rule sounds like. b
# also picks journals using year t publications, so it is not an ex ante risk set, and it drops 1,093
# entries and 6 active author years outright. treat it as a sensitivity variant rather than a neutral one.

# the corpus starts in 2015, so no J paper in an earlier year means none since 2015 and the first years
# hold entries that cannot carry a seed. the T anchor and the seed window variant stay open elsewhere.

# two csvs into data/, gitignored. booleans as 1 and 0, topic_match left empty for pierre. stdlib only.

import csv
import json
import os
import sys
from collections import defaultdict

csv.field_size_limit(sys.maxsize)   # the authorships json column is longer than the csv default allows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "data", "openalex_ai_semiclean_v1_0.csv")
PUBLISHERS = os.path.join(ROOT, "results", "openalex_three_path_v1_0", "journal_parent_publishers.csv")
FLAGS = os.path.join(ROOT, "results", "openalex_three_path_v1_0", "pathway_flags.csv")
OUT_A = os.path.join(ROOT, "data", "event_table_python_v0_oppA.csv")
OUT_B = os.path.join(ROOT, "data", "event_table_python_v0_oppB.csv")

COLUMNS = ["author_id", "journal_id", "t", "n_prior_papers", "coauthor_seed", "t_first_seed",
           "first_entry_independent", "first_entry_ride", "entering_work_id", "publisher_id", "topic_match"]

LATER = 9999   # sorts after every real year, so a missing entry means never


def load_corpus():
    """the semiclean csv and the journal to publisher mapping, same conventions as the q1 q2 notebook"""
    works = {}          # work_id to (date, journal, year, topic)
    work_authors = {}   # work_id to author ids without duplicates
    with open(CORPUS, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            w = r["work_id"]
            assert w not in works, f"duplicate work_id {w} in the corpus"
            works[w] = (r["publication_date"], r["journal_id"], int(r["publication_year"]), r["primary_topic_id"])
            seen = set()
            auths = []
            for a in json.loads(r["authorships_json"]):
                if a.get("author_id") and a["author_id"] not in seen:   # some papers list an author twice, keep one
                    seen.add(a["author_id"])
                    auths.append(a["author_id"])
            work_authors[w] = auths

    parent = {}   # journal to parent publisher, empty string for the one unresolved journal
    with open(PUBLISHERS, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            parent[r["journal_id"]] = "" if r["is_unresolved"] == "True" else r["parent_publisher_id"]
    return works, work_authors, parent


def build_index(works, work_authors):
    """the lookups the row loop needs, keyed by author so emission can go one author at a time"""
    papers_of = defaultdict(list)   # author to (year, date, work, journal, topic)
    for w, (d, j, y, tp) in works.items():
        for a in work_authors[w]:   # every author of a paper gets their own history entry
            papers_of[a].append((y, d, w, j, tp))

    jfirst = {}   # author to journal to first year they published there
    ework = {}    # author to journal to the entering paper of that first year
    for a, lst in papers_of.items():
        lst.sort()   # year then date then work id, so the first hit on a journal is the entering paper
        fj = {}
        ew = {}
        for y, d, w, j, tp in lst:
            if j not in fj:
                fj[j] = y
                ew[j] = w
        jfirst[a] = fj
        ework[a] = ew

    coauth = defaultdict(dict)   # author to co author to first year they shared a paper
    for w, (d, j, y, tp) in works.items():
        au = work_authors[w]
        for i, a in enumerate(au):
            for b in au[i + 1:]:
                if coauth[a].get(b, LATER) > y:
                    coauth[a][b] = y
                if coauth[b].get(a, LATER) > y:
                    coauth[b][a] = y

    jbty = defaultdict(set)   # (topic, year) to the journals that published that topic that year
    for w, (d, j, y, tp) in works.items():
        jbty[(tp, y)].add(j)

    return papers_of, jfirst, ework, coauth, jbty


def emit(idx, work_authors, parent, journals, path_a, path_b, want_traces=False):
    """both variants in one pass, sorted throughout so the bytes do not depend on dict order"""
    papers_of, jfirst, ework, coauth, jbty = idx
    st = {"rows_a": 0, "rows_b": 0, "seed_a": 0, "seed_b": 0, "entry_a": 0, "entry_b": 0,
          "entry_seed_a": 0, "entry_seed_b": 0, "entry_nonseed_a": 0, "entry_nonseed_b": 0,
          "ride_a": 0, "ride_b": 0, "ind_a": 0, "ind_b": 0, "pairs_a": 0, "pairs_seeded_a": 0}
    hist = defaultdict(int)   # t_first_seed year to distinct seeded pairs in variant a
    traces = []
    kinds = set()

    with open(path_a, "w", encoding="utf-8", newline="") as fa, \
         open(path_b, "w", encoding="utf-8", newline="") as fb:
        wa = csv.writer(fa, lineterminator="\n")
        wb = csv.writer(fb, lineterminator="\n")
        wa.writerow(COLUMNS)
        wb.writerow(COLUMNS)

        for a in sorted(papers_of):
            fj = jfirst[a]
            ew = ework[a]
            ca = coauth[a]

            tfs = {}   # journal to t_first_seed for this author, the min over co authors of the later of the two years
            for b, cy in ca.items():
                for j, by in jfirst[b].items():
                    v = max(cy, by)
                    if tfs.get(j, LATER) > v:
                        tfs[j] = v

            by_year = defaultdict(list)
            for y, d, w, j, tp in papers_of[a]:
                by_year[y].append(tp)

            prior = 0            # corpus papers of this author in years strictly before t
            pre_topics = set()   # primary topics of this author's papers in years strictly before t
            seen_j = set()       # journals of this author that already produced a row, for the pair histogram

            for t in sorted(by_year):
                allowed = None   # none means fall back to variant a for this year
                if pre_topics:
                    allowed = set()
                    for tp in pre_topics:
                        allowed |= jbty.get((tp, t), set())

                for j in journals:
                    fy = fj.get(j)
                    if fy is not None and fy < t:
                        continue   # the pair already entered so it produces no further rows

                    s = tfs.get(j)
                    c = 1 if s is not None and s < t else 0

                    if fy == t:
                        entering = ew[j]
                        ride = 0
                        if c:
                            for b in work_authors[entering]:   # a qualifying seed co author riding along on the entry
                                if b != a and ca.get(b, LATER) < t and jfirst[b].get(j, LATER) < t:
                                    ride = 1
                                    break
                        ind = 0 if ride else 1
                    else:
                        entering = ""
                        ride = 0
                        ind = 0

                    row = [a, j, t, prior, c, "" if s is None else s, ind, ride, entering, parent[j], ""]
                    wa.writerow(row)
                    st["rows_a"] += 1
                    st["seed_a"] += c
                    st["ride_a"] += ride
                    st["ind_a"] += ind
                    if entering:
                        st["entry_a"] += 1
                        st["entry_seed_a" if c else "entry_nonseed_a"] += 1
                    if j not in seen_j:
                        seen_j.add(j)
                        st["pairs_a"] += 1
                        if s is not None:
                            st["pairs_seeded_a"] += 1
                            hist[s] += 1

                    if allowed is None or j in allowed:
                        wb.writerow(row)
                        st["rows_b"] += 1
                        st["seed_b"] += c
                        st["ride_b"] += ride
                        st["ind_b"] += ind
                        if entering:
                            st["entry_b"] += 1
                            st["entry_seed_b" if c else "entry_nonseed_b"] += 1

                    if want_traces and c and len(traces) < 3:
                        kind = 2 if not entering else (0 if ride else 1)
                        if kind not in kinds:   # one ride entry, one independent entry with a seed, one seeded non entry
                            kinds.add(kind)
                            traces.append((kind, a, j, t, s, entering))

                prior += len(by_year[t])
                pre_topics.update(by_year[t])

    return st, hist, traces


def validate_file(path, label):
    """row level checks, read off the written file rather than off the counters"""
    rows = 0
    entries = 0
    pos = [0, 0, 0]   # t_first_seed strictly prior to t, same year, later
    prev_a = ""
    seen_ty = set()     # (t, journal) inside the current author block, catches duplicate rows
    entered = set()     # journals of the current author that already had their entry row
    prev_t = -1
    with open(path, encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        assert next(rd) == COLUMNS, f"{label} header drifted from the schema"
        for r in rd:
            a, j, t, npp, c, s, ind, ride, ew, pub, tm = r
            t = int(t)
            c = int(c)
            ind = int(ind)
            ride = int(ride)
            if a != prev_a:
                assert a > prev_a, f"{label} author blocks are not sorted, {a} after {prev_a}"
                prev_a = a
                seen_ty = set()
                entered = set()
                prev_t = -1
            assert t >= prev_t
            prev_t = t
            assert (t, j) not in seen_ty, f"{label} has {a} {j} {t} twice"
            seen_ty.add((t, j))
            assert j not in entered, f"{label} row for {a} {j} after the pair entered"
            assert c == (1 if s != "" and int(s) < t else 0), f"{label} seed flag disagrees with t_first_seed at {a} {j} {t}"
            assert not (ind and ride)
            assert (ind or ride) == (1 if ew else 0)
            assert int(npp) >= 0 and tm == ""
            if s:
                pos[0 if int(s) < t else 1 if int(s) == t else 2] += 1
            if ew:
                entries += 1
                entered.add(j)
            rows += 1
    print(f"  {label}, {rows:,} rows read back, all row level asserts pass, {entries:,} entry rows")
    print(f"    t_first_seed sits before t on {pos[0]:,} rows, in year t on {pos[1]:,}, after t on {pos[2]:,}")
    return rows, entries


def distinct_pairs_from_raw():
    """distinct (author, journal) pairs straight off the raw csv, independent of the index above"""
    pairs = set()
    with open(CORPUS, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            for a in {x["author_id"] for x in json.loads(r["authorships_json"]) if x.get("author_id")}:
                pairs.add((a, r["journal_id"]))
    return len(pairs)


def lennart_coauthor_pairs():
    """the author paper pairs his day level coauthor_path fires on"""
    out = set()
    with open(FLAGS, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["coauthor_path"] == "True":
                out.add((r["focal_author_id"], r["focal_work_id"]))
    return out


def year_level_coauthor_pairs(works, work_authors, jfirst):
    """the same thing at year level, someone else on this paper was in the journal in an earlier year"""
    out = set()
    for w, (d, j, y, tp) in works.items():
        au = work_authors[w]
        early = [b for b in au if jfirst[b].get(j, LATER) < y]
        for a in au:
            if any(b != a for b in early):
                out.add((a, w))
    return out


def trace(kind, a, j, t, s, entering, works, work_authors, idx):
    """one row printed end to end with the papers behind it, for checking by hand"""
    papers_of, jfirst, ework, coauth, jbty = idx
    names = {0: "entry with a seed co author on the entering paper, ride",
             1: "entry with a seed but no seed co author on the entering paper, not a ride",
             2: "seed present and no entry this year"}
    qual = []   # co authors whose seed is fully in place before t, the ones the flags actually rest on
    for b, cy in coauth[a].items():
        by = jfirst[b].get(j, LATER)
        if cy < t and by < t:
            qual.append((max(cy, by), b, cy, by))
    qual.sort()
    on_paper = sorted(x[1] for x in qual if entering and x[1] in work_authors[entering])
    v, b, cy, by = next((x for x in qual if x[1] in on_paper), qual[0])   # explain the flag with a co author that drives it
    shared = next(w for y, d, w, jj, tp in papers_of[a] if b in work_authors[w])   # earliest paper carrying both
    print(f"\n  {names[kind]}")
    print(f"    author {a}, journal {j}, t = {t}, t_first_seed = {s}")
    print(f"    seed co author {b}")
    print(f"      earliest shared paper {shared}, year {works[shared][2]}, so they were co authors from {cy}")
    print(f"      that co author's first {j} paper {ework[b][j]}, year {by}")
    print(f"      this co author's seed exists from max({cy}, {by}) = {v}, and {v} < {t} so coauthor_seed = 1")
    if entering:
        print(f"      entering paper {entering}, year {works[entering][2]}, date {works[entering][0]}")
        print(f"      qualifying seed co authors on that paper {on_paper if on_paper else 'none, so it is not a ride'}")
    else:
        print(f"      the author has no {j} paper in {t}, first {j} year is {jfirst[a].get(j, 'never')}, so F = 0")


def same_bytes(p, q):
    """byte compare, chunked so neither file is loaded whole"""
    with open(p, "rb") as f, open(q, "rb") as g:
        while True:
            x = f.read(1024 * 1024)
            y = g.read(1024 * 1024)
            if x != y:
                return False
            if not x:
                return True


def main():
    print("loading the corpus")
    works, work_authors, parent = load_corpus()
    journals = sorted(parent)
    noauth = sum(1 for v in work_authors.values() if not v)
    print(f"  {len(works):,} papers, {len(journals)} journals, "
          f"{sum(1 for v in parent.values() if not v)} without a resolvable parent publisher")
    print(f"  {noauth:,} papers carry no usable author id and drop out of every history")

    print("building the index")
    idx = build_index(works, work_authors)
    papers_of, jfirst, ework, coauth, jbty = idx
    active = sum(len({y for y, d, w, j, tp in lst}) for lst in papers_of.values())
    print(f"  {len(papers_of):,} authors, {sum(len(v) for v in papers_of.values()):,} author paper pairs, "
          f"{active:,} active author year pairs")

    print("writing both variants")
    st, hist, traces = emit(idx, work_authors, parent, journals, OUT_A, OUT_B, want_traces=True)

    print("\nsummary")
    for v in ("a", "b"):
        rows, seed, ent = st["rows_" + v], st["seed_" + v], st["entry_" + v]
        es, en = st["entry_seed_" + v], st["entry_nonseed_" + v]
        ride, ind = st["ride_" + v], st["ind_" + v]
        print(f"variant {v.upper()}")
        print(f"  rows                       {rows:,}")
        print(f"  rows with a seed, C = 1    {seed:,} ({seed / rows:.2%} of rows)")
        print(f"  entries, F = 1             {ent:,} ({ent / rows:.4%} of rows)")
        print(f"  entry rate given C = 1     {es / seed:.4%} ({es:,} of {seed:,})")
        print(f"  entry rate given C = 0     {en / (rows - seed):.4%} ({en:,} of {rows - seed:,})")
        print(f"  within C = 1               {ride:,} ride, {es - ride:,} independent")
        print(f"  first_entry_independent    {ind:,}, which counts the {ent - es:,} entries with no seed too")
    print(f"\npairs in variant A            {st['pairs_a']:,}, of which {st['pairs_seeded_a']:,} "
          f"({st['pairs_seeded_a'] / st['pairs_a']:.1%}) get a seed at some point")
    print("t_first_seed by year, distinct author journal pairs in variant A")
    print("  " + "  ".join(f"{y} {hist[y]:,}" for y in sorted(hist)))

    print("\nchecks")
    rows_a, entries_a = validate_file(OUT_A, "variant A")
    rows_b, entries_b = validate_file(OUT_B, "variant B")
    assert (rows_a, entries_a) == (st["rows_a"], st["entry_a"])
    assert (rows_b, entries_b) == (st["rows_b"], st["entry_b"])

    raw_pairs = distinct_pairs_from_raw()
    print(f"  distinct (author, journal) pairs off the raw csv {raw_pairs:,}, variant A entry rows {entries_a:,}")
    assert entries_a == raw_pairs, "every corpus pair must have exactly one entry row in variant A"
    print(f"  variant B keeps {entries_b:,} of those entries, {entries_b / entries_a:.1%}, "
          f"the rest sit in journals outside the author's pre t topic set")

    print("\ncross check against the day level flags")
    his = lennart_coauthor_pairs()
    mine = year_level_coauthor_pairs(works, work_authors, jfirst)
    print("  author paper pairs where another author of the same paper was in the journal earlier")
    print("  coauthor_path is the riding case, a co author on the paper itself, so the seed stays unchecked")
    print(f"  the seed rule also needs earlier co authorship, which is why rides are only {st['ride_a']:,}")
    print(f"    year level, this script {len(mine):,}")
    print(f"    day level, his flags    {len(his):,}")
    assert not mine - his, "year level fired where the day level flags did not, which cannot happen"
    print(f"  a strict subset of his, and the {len(his - mine):,} in the gap have the co author's journal "
          f"paper earlier inside the same year")

    print("\nthree rows traced by hand")
    for tr in traces:
        trace(*tr, works=works, work_authors=work_authors, idx=idx)

    print("\nrerun")
    # same process, so this catches leftover state in emit rather than hash order. the sorting fixes the bytes
    st2, _, _ = emit(idx, work_authors, parent, journals, OUT_A + ".rerun", OUT_B + ".rerun")
    assert st2 == st, "the two builds disagree on the counts"
    assert same_bytes(OUT_A, OUT_A + ".rerun") and same_bytes(OUT_B, OUT_B + ".rerun"), "the two builds differ in bytes"
    os.remove(OUT_A + ".rerun")
    os.remove(OUT_B + ".rerun")
    print("  built twice, both files byte identical")

    print("\nfiles")
    print(f"  {os.path.relpath(OUT_A, ROOT)}  {rows_a:,} rows, {os.path.getsize(OUT_A) / 1e6:.0f} MB")
    print(f"  {os.path.relpath(OUT_B, ROOT)}  {rows_b:,} rows, {os.path.getsize(OUT_B) / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
