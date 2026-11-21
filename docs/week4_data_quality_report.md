# Week 4 Data Quality & Bias Report — FYPilot

Version: 1.0 · Week 4 · Pathway A (PDF/TXT) · Audit date: 2026-11-21

Labels used: **Observed** = checked directly on the files · **Inferred risk** = plausible, not measured · **N.V.** = Not Verified.

> **Practice data only.** Every finding below is about the three synthetic practice files from Week 3. It does not describe the real UTM documents, which have not been collected yet.

## 1. Project and Data Overview

| Field | Evidence |
| --- | --- |
| Project and purpose | FYPilot: RAG assistant that recommends FYP topics and matching supervisors to UTM FAI undergraduates, with citations and a past-FYP novelty check. |
| Two Topic 2 requirements | **FR2 / NFR3** (suggest lecturers whose documented areas match): needs one clean, citable profile per lecturer. **RAI1** (cite a verifiable source for every claim): needs a source file and version on every chunk. FR3 (past FYPs) is also checked. |
| Pathway and data type | A: PDF/TXT, unstructured and semi-structured text |
| Audited output | Topic 3 Part B: `data/processed/prepared_text.jsonl` |
| Matching manifest | `data/week3_manifest.json` (Part C copies in `data/pipeline_v1/documents_*/pipeline_manifest.json`) |
| Sources | S01 `fai_fyp_guidelines_synthetic.pdf`, S02 `past_fyp_abstracts_synthetic.txt`, S03 `staff_research_profiles_synthetic.txt`; synthetic v1.0, 2026-11-02, FYPilot team; shareable |
| Population and sample | Unit = one chunk. Population = 19 chunks (7 guidelines, 9 past FYPs, 3 staff). All 19 inspected, because fewer than 20 exist. |
| Limitations | Synthetic data, 5 lecturers and 8 past FYPs only. Real-source dates, rights and quality are N.V. |

**Checkpoint A1:** if staff profiles were missing or merged, FR2 (supervisor suggestions) and RAI1 (per-lecturer citation) would fail first.

## 2. Five-Dimension Quality Scorecard

| Dimension | Finding | Sample / evidence | Impact | Decision |
| --- | --- | --- | --- | --- |
| Completeness | Guidelines cover the FYP 1 timeline and FYP 1 weights only; no FYP 2 timeline or weights. `page` is empty in 19 of 19 chunks. | Observed: `fai_fyp_guidelines_synthetic-0005`, `-0006`; `page` field | FR5 questions on FYP 2 must return "not found". Citations point to a document, not a page. | Warning |
| Consistency | All 19 chunks have the same 7 fields. Staff chunks differ in granularity: chunk 0001 = 1 lecturer, chunks 0002 and 0003 = 2 lecturers each. | Observed: STAFF-02 + STAFF-03 in `staff_research_profiles_synthetic-0002`; STAFF-04 + STAFF-05 in `-0003` | A chunk retrieved for one lecturer returns a second lecturer with a different area (FR2, RAI1). | Review |
| Accuracy | Prepared text matches the source exactly. With whitespace removed, guideline chunks = PDF text (2,808 of 2,808 characters); both TXT files = their chunks. | Observed: additional check comparing raw and prepared text | No text lost or changed by preparation. | Pass |
| Timeliness | Guidelines labelled Semester 1 2026/2027. Past FYPs span 2023–2025, none from 2026. Staff records have no last-updated date. | Observed (practice data); real dates N.V. | Outdated staff areas would cause wrong supervisor matches (NFR3). | N.V. (real data) |
| Uniqueness | 0 duplicate texts and 0 duplicate `record_id`s in 19 chunks. PFYP-2025-03 (supervisor matching using text similarity) is close to FYPilot's own idea. | Observed | Not a defect; a useful near-duplicate for evaluation criterion C5. | Pass |

## 3. Validation Findings

| Rule | Risk / requirement | Condition | Items tested | Result | Action |
| --- | --- | --- | --- | --- | --- |
| V1 | Untraceable citation (FR4, RAI1) | `source` not empty AND `source_sha256` equals the SHA-256 of the raw file in `data/raw/` | 19 chunks | **19 pass, 0 fail** | Hard fail if broken. No failures. |
| V2 | One record must be one citable unit (FR2, FR3, RAI1) | Each past-FYP and staff record appears whole in one chunk, and each staff chunk holds no more than one lecturer | 8 past-FYP records, 5 staff records, 3 staff chunks | Past FYPs: **8 of 8** whole, one per chunk. Staff: **5 of 5** whole, but **2 of 3** chunks hold 2 lecturers | Warning: split staff records to one per chunk before indexing; re-run V2. |

## 4. Duplicate, Anomaly and Coverage Findings

**Duplicates:** none (Observed, 19 chunks).

**Anomaly:** two chunks contain the "SYNTHETIC PRACTICE DATA" header. `past_fyp_abstracts_synthetic-0001` holds only the header (191 characters); `staff_research_profiles_synthetic-0001` holds the header plus STAFF-01. If indexed, a disclaimer could be retrieved and cited. Action: strip header blocks in Prepare.

| In-scope category | Expected evidence | Observed evidence / gap | Possible downstream effect |
| --- | --- | --- | --- |
| Research areas in past FYPs | Several past FYPs per FAI area | 8 records: NLP 3, recommender systems 2, computer vision 1, machine learning 1, IoT 1 | Novelty check is weak for areas with 0 or 1 past FYP. |
| Lecturers for matching | Every FAI lecturer, with comparable profiles | 5 lecturers across 4 departments; profile lengths 305–381 characters | Too few lecturers to test supervisor coverage (C10). |

Limits: synthetic set, so coverage of real FAI areas is N.V.

## 5. Bias Assessment

**Source / decision → gap → effect → control**

Chunking configuration C (800 characters) pairs two lecturers in one chunk (**pipeline-induced**) → a lecturer who shares a chunk with a popular area is retrieved more often → supervisor suggestions concentrate on some lecturers, against RAI2 → one lecturer per chunk, coverage count per lecturer during evaluation (C10), and diversity re-ranking.

On real data, lecturers with longer, richer staff pages are likely to match more queries (**representation**, Inferred risk). This is a plausible risk, not measured unfairness.

## 6. Privacy, Rights and Governance

| Question | Finding |
| --- | --- |
| Provenance and version | S01–S03, synthetic v1.0, 2026-11-02, FYPilot team. Source and output SHA-256 in `data/week3_manifest.json`; repeat run reproduced identical checksums. |
| Rights and permissions | Practice data: created by the team, shareable. Real sources: S01 may need UTM login; S02 public abstracts; S03 public pages naming real staff. Rights for real use: **N.V.** |
| Privacy and sensitive data | No student data in any source. Placeholder lecturer names only. Student input is handled by RAI4 (PII stripped before the model call). |
| Consent or collection basis | Not applicable to synthetic data. For real staff pages, use public research-area text only; FYP coordinator permission needed for the guideline site. |
| Ongoing maintenance | Project owner re-runs the pipeline and this audit each semester, or when any source file or the chunking configuration changes. |

**Safeguard:** real staff and guideline files are not committed to the public repo until rights are confirmed; until then they are referenced by URL only.

## 7. Mitigation and Impact on Requirements

| Priority improvement | Who / when | Requirements affected | Remaining risk |
| --- | --- | --- | --- |
| 1. Split staff profiles to one lecturer per chunk and remove disclaimer chunks; re-run V1 and V2 | Project owner, before Topic 5 retrieval work | FR2, NFR3, RAI1, RAI2 | Real profiles may still differ a lot in length. |
| 2. Replace synthetic files with permitted real UTM documents, record rights in the manifest, keep PDF page numbers, repeat this audit | Project owner, before evaluation | FR3, FR5, RAI1, all evaluation criteria | Real staff pages may be outdated; ePrints gives abstracts only. |

## 8. Quality-Gate Decision

**GO WITH CONDITIONS, for the synthetic practice data only.**

- Evidence: V1 passed 19 of 19; prepared text equals source text; lineage reproduced on a repeat run.
- Conditions: improvements 1 and 2 above.
- Residual risks: uneven or outdated real profiles; small past-FYP coverage per area.
- Re-review trigger: any new or changed source file, a change to the chunking configuration, or a V1 / V2 failure.
- Not covered: the real UTM dataset, which stays unverified until condition 2 is met.
