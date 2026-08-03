# Schema: openalex_ai_semiclean_v1_0.csv

One row per journal article. Produced by `fetch/OpenAlex_AI_Dataset_v1_0.ipynb` (dataset v1.0, frozen 2026-08-01): non-retracted articles 2015-2024 from the frozen population of 64 journals whose primary OpenAlex topic is in the frozen list of 49 AI topics. 27,400 rows. The raw source is `openalex_ai_raw_v1_0.jsonl` (not in git, shared via Teams/OneDrive).

Fields with the `_current` suffix hold today's OpenAlex value, not the value at publication time. OpenAlex caps a work at its first 100 authorships. Abstracts are reconstructed from the OpenAlex inverted index.

| Column | Type | Meaning |
|---|---|---|
| work_id | string | OpenAlex work ID (short form, e.g. W2493916176), unique key |
| doi | string | DOI without the https://doi.org/ prefix, may be empty |
| title | string | article title |
| abstract | string | reconstructed abstract text, empty when OpenAlex has none (coverage 98.4%) |
| publication_year | int | year of publication |
| publication_date | date | publication date, note that missing day/month often defaults to Jan 1 |
| work_type | string | always "article" in v1.0 (reviews excluded by the filter) |
| language | string | OpenAlex language code |
| is_retracted | bool | always false in v1.0 (filtered) |
| cited_by_count | int | citations as of the pull, current value |
| fwci | float | field-weighted citation impact, current value |
| referenced_works_count | int | number of referenced works |
| journal_id | string | OpenAlex source ID of the journal, one of the frozen 64 |
| journal_name | string | journal display name |
| journal_issn_l | string | linking ISSN, may be empty |
| journal_is_oa_current | bool | journal fully OA today |
| journal_is_in_doaj_current | bool | journal in DOAJ today |
| publisher_id_current | string | OpenAlex ID of the journal's host organization today (can be a subsidiary, see host_organization_lineage in the raw file for the parent) |
| publisher_name_current | string | host organization display name today |
| article_is_oa | bool | article available OA |
| article_oa_status | string | OpenAlex OA status (gold, hybrid, ...) |
| article_oa_url | string | best OA URL |
| article_license | string | license of the best OA location |
| apc_list_usd | float | listed article processing charge in USD, empty when unknown (present for 88.8%) |
| apc_paid_usd | float | APC actually paid in USD per OpenAlex, empty when unknown |
| primary_topic_id | string | primary OpenAlex topic, one of the frozen 49 |
| primary_topic_name | string | primary topic display name |
| primary_topic_score | float | topic assignment score |
| primary_subfield_id | string | subfield of the primary topic |
| primary_subfield_name | string | subfield display name |
| author_count | int | number of authorships on the work (capped at 100 by OpenAlex) |
| corresponding_author_count | int | authorships flagged corresponding, 0 when OpenAlex lacks the flag |
| authorships_json | JSON text | list of authorships: author_id, author_name, orcid, position, is_corresponding, countries, institutions (institution_id, institution_name, ror, country_code, type) |
| topics_json | JSON text | all topics of the work: topic_id, topic_name, score, subfield_id, subfield_name |
| keywords_json | JSON text | keywords: keyword_id, keyword_name, score |
| external_ids_json | JSON text | the OpenAlex ids object (openalex, doi, mag, pmid, ...) |
| indexed_in_json | JSON text | indexing sources, e.g. ["crossref","doaj"] |
| openalex_created_date | date | when OpenAlex created the work record |
| openalex_updated_date | datetime | when OpenAlex last updated the work record |
