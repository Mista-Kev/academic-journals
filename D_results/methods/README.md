# Methods, history and decisions

Start with the [root README](../../README.md) for the workflow and
[results in D](../README.md) for the findings.

- [Decision record](decisions.md): dated decisions, with proposed team adoption kept separate from confirmed decisions.
- [Q1–Q3 inputs, calculations and outputs](analysis-interfaces.md): the implemented analyses and their limits, including topic categories and sampling with replacement.
- [Shared data](shared-data.md): setup and use of the SharePoint files.
- [Data and calculation checks](validation.md): what was run and what each check establishes.
- [Historical Q3 structure draft](q3-structure.md): the earlier causal argument, with its direct-effect and bound claims explicitly withdrawn. Use the current decision record for interpretation.
- [Plan](plan.md), [research notes](research-notes.md) and [feedback](feedback-log.md): historical requirements and discussion, not evidence of the current implementation.

Q3 uses regression with standardization and is reported as an association.
A causal graph or an earlier plan for Bayes nets in Logtalk is not a runnable
BN system. The repository reorganization does not change that scope.

The current annual event-table schema has 15 columns and is documented in
[B/schemas/event_table.md](../../B_opportunities_and_analysis/schemas/event_table.md).
The column names were checked against the official v5 input. The earlier
paper-level draft is no longer presented as the current schema.
