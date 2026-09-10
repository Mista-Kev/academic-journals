# A · Data and rules

### Purpose

Create the frozen OpenAlex dataset used by the project.
[Run the publication rules](logic/README.md) · [Corpus columns](data/schemas/openalex_ai_semiclean_v1_0.md)

B uses the corpus for Q1/Q2 and entry opportunities; C uses its texts and histories
for topic profiles. Use the shared release for reproduction: a new download can differ.

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
