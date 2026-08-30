% event table rules for the frozen openalex ai corpus
% this is the second and independent implementation of the q3 event table
% every rule below follows one sentence of the frozen definitions in data/schemas/event_table.md
%
% expected generated facts are the ones the pathway rules already use
%   work(WorkId, PublicationDate, JournalId, ParentPublisherId)
%   authorship(WorkId, AuthorId)
%
% publication dates are iso atoms whose first four characters are the year
% everything in this file works at year level, never at date level, except the
% tie break that picks the entering paper

:- dynamic paper/4.
:- dynamic corpus_journal/1.
:- dynamic indexes_built/0.

% the year of a paper is the first four characters of its iso date atom
publication_year(Date, Year) :-
    sub_atom(Date, 0, 4, _, YearAtom),
    atom_number(YearAtom, Year).

% paper(A, T, J, W) says author A has corpus paper W in journal J in year T
% it is derived once so that author lookups are first argument indexed
build_paper_facts :-
    forall(
        ( authorship(WorkId, AuthorId), work(WorkId, Date, JournalId, _) ),
        ( publication_year(Date, Year), assertz(paper(AuthorId, Year, JournalId, WorkId)) )
    ).

% the target journals are exactly the journals that occur in the corpus and nothing else
build_corpus_journals :-
    findall(JournalId, work(_, _, JournalId, _), AllJournals),
    sort(AllJournals, Journals),
    forall(member(JournalId, Journals), assertz(corpus_journal(JournalId))).

% the derived facts are built at most once per prolog process
build_indexes :-
    indexes_built,
    !.
build_indexes :-
    build_paper_facts,
    build_corpus_journals,
    assertz(indexes_built).

% active(A, T) holds when A has at least one corpus paper in year T
active(AuthorId, Year) :-
    paper(AuthorId, Year, _, _).

% one solution per active author and year because active succeeds once per paper
active_author_year(AuthorId, Year) :-
    findall(A-T, active(A, T), Pairs),
    sort(Pairs, DistinctPairs),
    member(AuthorId-Year, DistinctPairs).

% entered(A, J, T) holds when A has at least one paper in J in a year strictly before T
entered(AuthorId, JournalId, Year) :-
    paper(AuthorId, PriorYear, JournalId, _),
    PriorYear < Year.

% an opportunity row exists when A is active in T and has not entered J before T
% the pair stops producing rows after its first entry because entered is then true forever
opportunity(AuthorId, JournalId, Year) :-
    active_author_year(AuthorId, Year),
    corpus_journal(JournalId),
    \+ entered(AuthorId, JournalId, Year).

% two authors collaborated before T when they share a corpus paper from a year strictly before T
coauthored_before(AuthorId, Coauthor, Year) :-
    paper(AuthorId, PriorYear, _, WorkId),
    PriorYear < Year,
    authorship(WorkId, Coauthor),
    Coauthor \= AuthorId.

% a coauthor was already in the journal before T when they have a paper in J from a year strictly before T
published_in_before(Coauthor, JournalId, Year) :-
    paper(Coauthor, PriorYear, JournalId, _),
    PriorYear < Year.

% seeded is C and one and the same coauthor must carry both halves of it
seeded(AuthorId, JournalId, Year) :-
    coauthored_before(AuthorId, Coauthor, Year),
    published_in_before(Coauthor, JournalId, Year).

% first entry is F and holds when A publishes in J in year T and never in an earlier year
first_entry(AuthorId, JournalId, Year) :-
    paper(AuthorId, Year, JournalId, _),
    \+ entered(AuthorId, JournalId, Year).

% the entering paper is the earliest year T paper of A in J with ties broken by the smallest work id
% sorting date and work id pairs gives that order because iso date atoms sort chronologically
entering_paper(AuthorId, JournalId, Year, WorkId) :-
    findall(
        Date-Candidate,
        ( paper(AuthorId, Year, JournalId, Candidate), work(Candidate, Date, _, _) ),
        DatedPapers
    ),
    sort(DatedPapers, [_-WorkId|_]).

% ride holds when one single coauthor carries all three facts at once
% the coauthor must be on the entering paper and must be the same one that qualifies the seed
% binding Coauthor from the entering paper first is what keeps the witness shared
ride(AuthorId, JournalId, Year) :-
    entering_paper(AuthorId, JournalId, Year, WorkId),
    authorship(WorkId, Coauthor),
    coauthored_before(AuthorId, Coauthor, Year),
    published_in_before(Coauthor, JournalId, Year).

% a flag is one when the goal has at least one solution and zero otherwise
flag(Goal, 1) :-
    call(Goal),
    !.
flag(_, 0).

% one event table row carries the three flags for the given author journal and year
% ride is only asked on first entry rows because it is defined only there
event_row(AuthorId, JournalId, Year, Seed, Entry, Ride) :-
    flag(seeded(AuthorId, JournalId, Year), Seed),
    flag(first_entry(AuthorId, JournalId, Year), Entry),
    (   Entry =:= 1
    ->  flag(ride(AuthorId, JournalId, Year), Ride)
    ;   Ride = 0
    ).

% the python driver calls this predicate once and formats the csv from the emitted lines
emit_event_table :-
    build_indexes,
    forall(
        opportunity(AuthorId, JournalId, Year),
        (   event_row(AuthorId, JournalId, Year, Seed, Entry, Ride),
            format('ROW|~w|~w|~w|~w|~w|~w~n', [AuthorId, JournalId, Year, Seed, Entry, Ride])
        )
    ).

% emits one named row together with its entering paper so a single case can be checked by hand
emit_case(AuthorId, JournalId, Year) :-
    build_indexes,
    event_row(AuthorId, JournalId, Year, Seed, Entry, Ride),
    (   entering_paper(AuthorId, JournalId, Year, WorkId)
    ->  true
    ;   WorkId = ''
    ),
    format('CASE|~w|~w|~w|~w|~w|~w|~w~n', [AuthorId, JournalId, Year, Seed, Entry, Ride, WorkId]).
