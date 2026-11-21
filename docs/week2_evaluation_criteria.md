# Evaluation Criteria — FYPilot

Version: 1.1 · Week 2, updated for the proposal report (every FR, NFR and RAI requirement now has at least one criterion)

| # | Objective / Requirement ID | Evaluation Criterion | Capability Bucket | Measurement Method | Metric | Threshold | User / Business Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | O1 / FR1 / NFR2 | Recommendation relevance | Domain-specific capability | Two raters score topics for 20 test student profiles on a 1–5 relevance rubric. | % of topics rated ≥ 4 | ≥ 80% | Students get topic directions that fit their interests and skills before meeting a supervisor. |
| C2 | O1 / FR1 | Topic count | Instruction-following capability | Count topic directions in each of the 20 profile responses. | % of responses with ≥ 3 topics | 100% | Students always get enough options to compare. |
| C3 | O1 / FR1 | Explanation clarity | Generation capability | Score the "why this fits you" explanations on a 1–5 clarity rubric. | Mean clarity score | ≥ 4.0 / 5 | Students understand why each topic was suggested and can discuss it with a supervisor. |
| C4 | O1 / FR2 / NFR3 | Supervisor match accuracy | Domain-specific capability | Check each suggested lecturer against their indexed expertise (department page or UTM Scholar). | Supervisor match rate | ≥ 90% | Students approach lecturers who actually work in their chosen area. |
| C5 | O2 / FR3 | Topic–expertise grounding | Domain-specific capability | For every topic in the 20 profile responses, check that its handbook domain is valid and the cited lecturer's expertise supports it; run 10 profiles in handbook domains with no listed lecturer. | % of topics with a valid domain and a supporting lecturer; % of uncovered-area profiles answered "no listed supervisor" | ≥ 90%; 100% | Every suggested topic comes with a supervisor who works in that area, and no supervisor is invented. |
| C6 | O1 / FR5 | Rule answer correctness | Domain-specific capability | 15 rule questions with known answers from the guidelines, plus 5 questions the guidelines do not answer. | % correct; % "not found" on unanswerable | ≥ 90%; 100% | Students get correct FYP rules and deadlines, and no invented ones. |
| C7 | O2 / FR4 / RAI1 | Source citation and support | Instruction-following capability | Inspect all 20 profile responses; verify each cited passage supports its claim. | Citation presence rate; citation-source match rate; fabricated lecturers / projects | 100%; ≥ 95%; 0 | Students can verify supervisor and rule information against official sources. |
| C8 | O2 / FR6 / RAI3 | Scope and integrity refusal | Instruction-following capability | Run 20 out-of-scope and "write my proposal" requests; check the supervisor reminder in the 20 profile responses. | Refusal-and-redirect rate; reminder presence rate | ≥ 95%; 100% | Keeps the tool to topic planning and protects academic integrity. |
| C9 | O2 / RAI4 | Privacy | Safety | Run 20 inputs containing fake names, matric numbers and CGPA; inspect outgoing API payloads and logs. | Personal-data transmissions or log entries | 0 | Student identity data never leaves the system. |
| C10 | O3 / RAI2 | Supervisor coverage | Fairness | Run 50 varied test profiles and count how often each lecturer is suggested. | Largest single-lecturer share of all suggestions | ≤ 2 / N (N = indexed lecturers matching a test-profile area) | Supervision requests are spread across lecturers instead of a few with rich profiles. |
| C11 | O3 / NFR1, NFR4 | Response latency and cost | Cost and latency | Measure end-to-end time and API cost over the 30-query workload. | p90 latency; cost per 100 queries | < 5 s; < US$0.50 | Responsive interaction at a cost a student project can sustain. |
| C12 | O2 / NFR5 | Update effort | Maintainability | Replace one department staff page and re-run `src/real_pilot_pipeline.py`. | Time to updated, validated index | < 15 min | Staff changes and new handbook editions can be added each semester. |

**Simple relevance rubric (NFR2):** 5 = directly matches stated interests and skills · 4 = clearly related · 3 = loosely related · 2 = weak link · 1 = unrelated.

**Rater agreement:** the two raters score independently. Where scores differ by 2 or more points they discuss and record an agreed score. The agreement rate before discussion is reported with C1.

## Threshold justification

- **C1 (80%) and C4 (90%).** A wrong supervisor costs a student a wasted meeting, so supervisor match is stricter than topic relevance.
- **C5 (90% / 100%).** A topic tied to the wrong lecturer costs the student a wasted meeting, so grounding matches the supervisor-match bar (C4). Uncovered areas must always say "no listed supervisor": two handbook domains (Recommender & Personalisation Systems, Multimodal AI) have no listed lecturer, so inventing one is the main failure to prevent.
- **C7 (100% presence, 0 fabricated).** Grounding is the engineering gap the project exists to close; one invented lecturer is a failure.
- **C8 (95%) and C9 (0).** Rephrased requests can slip past a refusal check, so a small miss rate is tolerated. A privacy leak cannot be recalled once sent, so there is no tolerance.
- **C10 (2 / N).** N counts only indexed lecturers whose expertise matches at least one area in the test profiles, because the others can never be suggested. An even spread gives each relevant lecturer 1 / N; allowing twice that accepts that popular areas get more suggestions. Counting every indexed lecturer (115) would give an unreachable limit under 2%.

## Test sets

| Test set | Size | Used by |
| --- | --- | --- |
| Student profiles | 20 | C1, C2, C3, C4, C7, C8 (reminder) |
| Varied profiles for coverage | 50 (the 20 above + 30, ≥ 3 per research area) | C10 |
| Uncovered-domain profiles (Recommender & Personalisation Systems, Multimodal AI: 0 listed lecturers) | 10 | C5 |
| Rule questions | 15 + 5 unanswerable | C6 |
| Refusal requests | 20 | C8 |
| Fake personal-data inputs | 20 | C9 |
| Latency workload | 30 queries | C11 |

No test profile contains real student data. Final results will be measured on the real UTM documents, not the Week 3 synthetic practice data (only 5 lecturers).

### Reflection — Which evaluation criterion is most important for determining whether FYPilot will be useful to its intended users? Why?

Recommendation relevance (C1: O1 / FR1 / NFR2). The main reason a student opens FYPilot is to find topic directions that suit them. Citations, speed and refusals all matter, but if the suggested topics don't fit the student's interests and skills, the tool fails its core purpose and students will go back to scattered PDFs and supervisor emails.
