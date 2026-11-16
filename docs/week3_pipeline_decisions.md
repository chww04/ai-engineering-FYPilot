# Week 3 Pipeline Decisions, Stage Contracts and Traceability — FYPilot

Version: 1.0 · Week 3 · Diagram: [week3_pipeline_diagram.png](week3_pipeline_diagram.png) · Notebook: [`notebooks/week3_pipeline.ipynb`](../notebooks/week3_pipeline.ipynb)

## Summary of decisions

| Item | Decision |
| --- | --- |
| **Topic 2 requirements served** | FR5 (FYP rules), FR3 (past FYPs), FR2 / NFR3 (lecturer expertise), RAI1 (traceable sources) |
| **Selected sources** | S01 FYP guidelines (PDF), S02 past-FYP abstracts (TXT), S03 staff research profiles (TXT) — synthetic practice data; see [data inventory](week3_data_inventory.md) |
| **Pathway** | A — PDF/TXT only. Single modality (documents); pathways B–F not run |
| **Chosen preparation** | Whitespace normalisation → restore a blank line before numbered section headings → paragraph-aware chunks of up to 800 characters |
| **Output** | `data/processed/prepared_text.jsonl` (19 chunks: 7 guidelines, 9 past FYPs, 3 staff), `data/week3_manifest.json`, `data/pipeline_v1/documents_*/` |
| **ETL vs ELT** | **ETL.** Text is extracted, cleaned and chunked before storage, because later retrieval needs clean, citable chunks and the corpus is small. Raw files are kept unchanged in `data/raw/`, so the transform can be re-run if the chunking decision changes. |
| **Batch vs streaming** | **Batch.** FYP guidelines, abstracts and staff profiles change a few times per semester, not continuously. A batch re-run per document update also supports NFR5 (update in < 15 min). |
| **Accepted limitation** | Page numbers are not kept (`page = None`), so citations point to the document, not the page. Chunks are uneven in size (191–708 characters). |
| **Provenance / access caveat** | Practice data is synthetic and shareable. The real guideline site may need a UTM login, and real staff pages name real people — rights must be checked before committing real data to a public repo. |

## Step B3 — Comparison of preparation configurations (same input data)

| Configuration | Guidelines (PDF): chunks / mid-sentence cuts | Past FYPs: chunks / cuts / records split | Staff: chunks / cuts / records split |
| --- | --- | --- | --- |
| A: fixed 500 chars (lab default) | 7 / 6 | 11 / 6 / **8 of 8** | 4 / 3 / 3 of 5 |
| B: paragraph-aware 500 | 8 / 6 | 17 / 8 / **8 of 8** | 6 / 0 / 0 of 5 |
| **C: paragraph-aware 800 + heading breaks (selected)** | **7 / 0** | **9 / 0 / 0 of 8** | **3 / 0 / 0 of 5** |
| D: paragraph-aware 1000 + heading breaks | 5 / 0 | 8 / 0 / 0 of 8 | 2 / 0 / 0 of 5 |

**Observed evidence:** A3 showed the PDF extracts with no blank lines between sections, so B behaved like fixed-size chunking on the guidelines (6 mid-sentence cuts). Each past-FYP record is 540–710 characters, so any 500-character limit split all 8 records.

**Selected: C.** *Benefit:* zero mid-sentence cuts and every past-FYP and staff record stays whole in one chunk, so FR3 / FR2 answers can cite one record as one source (RAI1). *Accepted limitation:* chunks are larger, and D was rejected because it merges several lecturers into one chunk, which weakens per-lecturer citation. The heading-break rule only works for numbered headings; other documents may need a different rule.

## Step C3 — Stage contracts

| Stage | Contract / evidence | Failure response |
| --- | --- | --- |
| Ingest | Chosen source exists at an explicit path under `data/raw` and is permitted (synthetic) | Stop for missing input (`FileNotFoundError`) |
| Inspect | Text is extractable and non-empty; TXT records have the expected fields | Stop and flag the file for OCR (scanned PDF) or invalid structure |
| Prepare | Configuration C produces at least one non-empty chunk per source | Stop or report transformation failure |
| Validate | `prepared_text.jsonl` exists, is non-empty, exported count = records, SHA-256 recorded | Stop for missing / empty output or count mismatch |
| Record lineage | Every source maps to its exact output with source + output SHA-256; Cell 6B and Cell 9 checks pass | Stop / report missing mapping, checksum mismatch, or non-repeatable output |

**Execution evidence (notebook):** Cell 6B `COMMON LINEAGE VALIDATION: PASS` (3 records); Cell 8A `SUCCESS` for 3 document pipelines; Cell 9 `PASS` for all 3 — source fingerprints, prepared outputs and mappings match on rerun.

## Failure points (shown in the diagram)

1. **Inspect — scanned or image-only PDF.** pypdf returns no text. Response: stop with "No extractable text", log the file and flag it for OCR in a later topic.
2. **Prepare — lost paragraph structure.** PDF extraction drops blank lines, so chunks cut mid-sentence and records split. Response: restore heading breaks; the B3 counts (mid-sentence cuts, split records) must be 0 before accepting the output.

## Updated traceability (from Week 2)

| Objective | Requirement | Evaluation criterion | Architecture element | Week 3 evidence |
| --- | --- | --- | --- | --- |
| O1 | FR5 | Answer correctness on FYP rules | Faculty knowledge source | S01 prepared into 7 section-level chunks |
| O2 | FR3 | Duplicate-topic detection (≥ 80%) | Past-project source + similarity check | S02 prepared as 8 whole-record chunks, ready for similarity search |
| O1 | FR2 / NFR3 | Supervisor match accuracy (≥ 90%) | Faculty knowledge source | S03 prepared with one or two lecturers per chunk |
| O2 | RAI1 | Citation presence and support | Knowledge access with source tracking | Every chunk keeps source file + SHA-256; manifests verified by Cells 6B and 9 |
