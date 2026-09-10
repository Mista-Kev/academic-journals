% Temporal pathway rules for the frozen OpenAlex AI corpus.
%
% Expected generated facts:
%   work(WorkId, PublicationDate, JournalId, ParentPublisherId).
%   authorship(WorkId, AuthorId).
%   focal_pair(FocalWorkId, FocalAuthorId).
%
% Missing parent publishers are written as the atom none. Dates are ISO
% yyyy-mm-dd atoms, so @< gives strict chronological order for this corpus.

known_publisher(PublisherId) :-
    PublisherId \= none.

strictly_prior(PriorWork, FocalWork) :-
    work(PriorWork, PriorDate, _, _),
    work(FocalWork, FocalDate, _, _),
    PriorWork \= FocalWork,
    PriorDate @< FocalDate.

journal_path(
    FocalWork,
    FocalAuthor,
    PriorWork,
    TargetJournal,
    PriorParentPublisher,
    PriorDate
) :-
    focal_pair(FocalWork, FocalAuthor),
    work(FocalWork, _, TargetJournal, _),
    authorship(PriorWork, FocalAuthor),
    work(PriorWork, PriorDate, TargetJournal, PriorParentPublisher),
    strictly_prior(PriorWork, FocalWork).

publisher_path(
    FocalWork,
    FocalAuthor,
    PriorWork,
    PriorJournal,
    TargetJournal,
    ParentPublisher,
    PriorDate
) :-
    focal_pair(FocalWork, FocalAuthor),
    work(FocalWork, _, TargetJournal, ParentPublisher),
    known_publisher(ParentPublisher),
    authorship(PriorWork, FocalAuthor),
    work(PriorWork, PriorDate, PriorJournal, ParentPublisher),
    PriorJournal \= TargetJournal,
    strictly_prior(PriorWork, FocalWork).

coauthor_path(
    FocalWork,
    FocalAuthor,
    Coauthor,
    PriorWork,
    TargetJournal,
    PriorParentPublisher,
    PriorDate
) :-
    focal_pair(FocalWork, FocalAuthor),
    authorship(FocalWork, Coauthor),
    Coauthor \= FocalAuthor,
    authorship(PriorWork, Coauthor),
    work(FocalWork, _, TargetJournal, _),
    work(PriorWork, PriorDate, TargetJournal, PriorParentPublisher),
    strictly_prior(PriorWork, FocalWork).

has_journal_path(FocalWork, FocalAuthor) :-
    journal_path(FocalWork, FocalAuthor, _, _, _, _).

has_publisher_path(FocalWork, FocalAuthor) :-
    publisher_path(FocalWork, FocalAuthor, _, _, _, _, _).

has_coauthor_path(FocalWork, FocalAuthor) :-
    coauthor_path(FocalWork, FocalAuthor, _, _, _, _, _).

truth(Goal, true) :-
    call(Goal),
    !.
truth(_, false).

pathway_flags(FocalWork, FocalAuthor, JournalPath, PublisherPath, CoauthorPath) :-
    focal_pair(FocalWork, FocalAuthor),
    truth(has_journal_path(FocalWork, FocalAuthor), JournalPath),
    truth(has_publisher_path(FocalWork, FocalAuthor), PublisherPath),
    truth(has_coauthor_path(FocalWork, FocalAuthor), CoauthorPath).

% The Python wrapper calls this predicate once. It emits a small, stable
% line-based result format; Python is responsible for CSV formatting.
emit_pathway_results :-
    emit_flags,
    emit_evidence.

emit_flags :-
    findall(
        flag(FocalWork, FocalAuthor, JournalPath, PublisherPath, CoauthorPath),
        pathway_flags(FocalWork, FocalAuthor, JournalPath, PublisherPath, CoauthorPath),
        Rows
    ),
    sort(Rows, SortedRows),
    forall(
        member(flag(FocalWork, FocalAuthor, JournalPath, PublisherPath, CoauthorPath), SortedRows),
        format(
            'FLAG|~w|~w|~w|~w|~w~n',
            [FocalWork, FocalAuthor, JournalPath, PublisherPath, CoauthorPath]
        )
    ).

emit_evidence :-
    findall(
        evidence(FocalWork, FocalAuthor, journal, PriorWork, FocalAuthor, TargetJournal, PriorParentPublisher, PriorDate),
        journal_path(FocalWork, FocalAuthor, PriorWork, TargetJournal, PriorParentPublisher, PriorDate),
        JournalRows
    ),
    emit_evidence_rows(JournalRows),
    findall(
        evidence(FocalWork, FocalAuthor, publisher, PriorWork, FocalAuthor, PriorJournal, ParentPublisher, PriorDate),
        publisher_path(FocalWork, FocalAuthor, PriorWork, PriorJournal, _, ParentPublisher, PriorDate),
        PublisherRows
    ),
    emit_evidence_rows(PublisherRows),
    findall(
        evidence(FocalWork, FocalAuthor, coauthor, PriorWork, Coauthor, TargetJournal, PriorParentPublisher, PriorDate),
        coauthor_path(FocalWork, FocalAuthor, Coauthor, PriorWork, TargetJournal, PriorParentPublisher, PriorDate),
        CoauthorRows
    ),
    emit_evidence_rows(CoauthorRows).

emit_evidence_rows(Rows) :-
    sort(Rows, SortedRows),
    forall(
        member(evidence(FocalWork, FocalAuthor, PathType, PriorWork, PriorAuthor, PriorJournal, PriorParentPublisher, PriorDate), SortedRows),
        format(
            'EVIDENCE|~w|~w|~w|~w|~w|~w|~w|~w~n',
            [FocalWork, FocalAuthor, PathType, PriorWork, PriorAuthor, PriorJournal, PriorParentPublisher, PriorDate]
        )
    ).
