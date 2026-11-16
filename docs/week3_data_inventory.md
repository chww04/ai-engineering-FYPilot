# Week 3 Data Inventory — FYPilot

Version: 1.0 · Week 3 · Pathway A (PDF/TXT) · Notebook: [`notebooks/week3_pipeline.ipynb`](../notebooks/week3_pipeline.ipynb)

> **Synthetic practice dataset.** The real UTM sources could not be downloaded for this lab, so three synthetic documents modelled on them were created by the project team. Results from this data do **not** show how well FYPilot itself performs. Each source lists the real document that will replace it.

## Step A1 — From Topic 2 requirements to data needs

| Requirement ID | Needed information | Candidate source | Why usable / constraint |
| --- | --- | --- | --- |
| FR5: Answer questions about FYP rules, timeline and assessment | FYP rules, deadlines, assessment weights, integrity rules | S01 FYP guidelines (PDF) | Authoritative faculty document; real version may need a UTM login and may change each semester |
| FR3: Show similar past FYPs and flag duplicates | Past FYP title, year, area, abstract | S02 past-FYP abstracts (TXT) | Public abstracts on UTM ePrints; abstracts only, not full theses |
| FR2 / NFR3: Suggest lecturers whose research areas match | Lecturer research areas and supervision interests | S03 staff research profiles (TXT) | Public staff pages; may be outdated or uneven in detail (links to RAI2 fairness) |
| RAI1: Cite a verifiable source for every claim | Source identity and version for each chunk | All three — file name + SHA-256 kept in every record | Checksums prove which file version was used, not that the content is correct |

## Step A4 — Inventory

| Source ID | Filename / URL | Type and purpose | Version / date / owner | Access / rights | Inspection evidence |
| --- | --- | --- | --- | --- | --- |
| S01 | `data/raw/fai_fyp_guidelines_synthetic.pdf` → replaces: FAI FYP Guidelines, [sites.google.com/utm.my/fai-fyp](https://sites.google.com/utm.my/fai-fyp/home) | PDF, unstructured text · FYP rules for FR5, RAI3 | Synthetic v1.0, 2026-11-02, FYPilot team · SHA-256 `5b3722e5a236a7a6…` | Synthetic, shareable. Real: UTM-owned, may need UTM login — rights not verified | 2 pages, 3,313 characters extracted with pypdf. Readable text, but **no blank lines between sections** after extraction (only 2 blank-line paragraphs found) |
| S02 | `data/raw/past_fyp_abstracts_synthetic.txt` → replaces: past thesis abstracts, [eprints.utm.my](https://eprints.utm.my) | TXT, semi-structured records · past FYPs for FR3 | Synthetic v1.0, 2026-11-02, FYPilot team · SHA-256 `77f572abd3755d33…` | Synthetic, shareable. Real: public abstract pages — rights not verified | 5,059 characters, **8 records** separated by blank lines, fields: Record ID, Title, Year, Research area, Abstract. Each record is 540–710 characters |
| S03 | `data/raw/staff_research_profiles_synthetic.txt` → replaces: staff profiles, [people.utm.my](https://people.utm.my) + [fai.utm.my](https://fai.utm.my) | TXT, semi-structured records · lecturer expertise for FR2, NFR3 | Synthetic v1.0, 2026-11-02, FYPilot team · SHA-256 `8e7b124f9b9d81ce…` | Synthetic, shareable; lecturer names are placeholders. Real: public pages naming real staff — check before sharing | 1,872 characters, **5 records**, fields: Staff ID, Name, Department, Research areas, Supervision |

**Representative records inspected** (notebook, Step A3): past-FYP record `PFYP-2023-01` (durian leaf disease detection, 2023, computer vision) and staff record `STAFF-01` (NLP and retrieval-augmented generation).

## Raw vs prepared storage

| Stage | Location | Contents |
| --- | --- | --- |
| Raw | `data/raw/` | The 3 source files above, unchanged |
| Prepared (Part B) | `data/processed/prepared_text.jsonl` | 19 chunks with record ID, text, source, source type, SHA-256, processing method |
| Lineage (Part B) | `data/week3_manifest.json` | 3 source → output entries with source and output checksums |
| Pipeline (Part C) | `data/pipeline_v1/documents_{guidelines,past_fyps,staff_profiles}/` | Prepared chunks + `pipeline_manifest.json` per source |

**Checkpoint A:** each source is tied to a Week 2 requirement (table above), and the notebook shows extracted samples and parsed records, not only "file loaded".
