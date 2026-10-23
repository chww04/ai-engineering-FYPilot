# Evaluation Criteria — FYPilot

| Objective / Requirement ID | Evaluation Criterion | Capability Bucket | Measurement Method | Metric | Threshold | User / Business Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| O1 / FR1 / NFR2 | Recommendation relevance | Domain-specific capability | Two raters score topics for 20 test student profiles on a 1–5 relevance rubric. | % of topics rated ≥ 4 | ≥ 80% | Students get topic directions that fit their interests and skills before meeting a supervisor. |
| O1 / FR2 / NFR3 | Supervisor match accuracy | Domain-specific capability | Check each suggested lecturer against their staff profile page. | Supervisor match rate | ≥ 90% | Students approach lecturers who actually work in their chosen area. |
| O2 / FR3 | Duplicate-topic detection | Domain-specific capability | Submit 10 topics that closely repeat known past UTM theses and check whether they are flagged. | Duplicate detection rate | ≥ 80% | Students avoid proposing topics that repeat past FYPs. |
| O2 / FR4 / RAI1 | Source citation and support | Instruction-following capability | Inspect responses for citations and verify each cited source supports the claim. | Citation presence rate; citation-source match rate | 100% presence; ≥ 95% match | Students can verify supervisor and rule information against official sources. |
| O2 / FR6 / RAI3 | Out-of-scope and proposal-writing refusal | Instruction-following capability | Run a 20-query set of out-of-scope and "write my proposal" requests. | Refusal-and-redirect rate | ≥ 95% | Keeps the tool to topic planning and protects academic integrity. |
| O1 / FR1 | Explanation clarity | Generation capability | Score the "why this fits you" explanations on a simple 1–5 clarity rubric. | Mean clarity score | ≥ 4.0 / 5 | Students understand why each topic was suggested and can discuss it with a supervisor. |
| O3 / NFR1, NFR4 | Response latency and cost | Cost and latency | Measure end-to-end time and API cost over the 30-query workload. | p90 latency; cost per 100 queries | < 5 s; < US$0.50 | Responsive interaction at a cost a student project can sustain. |

**Simple relevance rubric (NFR2):** 5 = directly matches stated interests and skills · 4 = clearly related · 3 = loosely related · 2 = weak link · 1 = unrelated.

### Reflection — Which evaluation criterion is most important for determining whether FYPilot will be useful to its intended users? Why?

Recommendation relevance (O1 / FR1 / NFR2). The main reason a student opens FYPilot is to find topic directions that suit them. Citations, speed and refusals all matter, but if the suggested topics don't fit the student's interests and skills, the tool fails its core purpose and students will go back to scattered PDFs and supervisor emails.
