# Architecture Decisions & Traceability — FYPilot V1

Version: 1.0 · Week 2 · Diagram: [week2_architecture_v1.png](week2_architecture_v1.png)

## Step C1 — Simplest Architecture

**Student → FYPilot Application → Language Model Service → Response**

This simple flow can generate topic ideas from the model's general knowledge, but it cannot meet several requirements:

- It does not know UTM Faculty of AI lecturers, rules or past projects (FR2, FR3, FR5, NFR3).
- It cannot cite sources (FR4, RAI1).
- It cannot reliably refuse proposal-writing or out-of-scope requests, or keep personal data away from the model API (FR6, RAI3, RAI4).
- It gives no way to measure relevance, latency, cost or supervisor coverage (NFR1, NFR2, NFR4, RAI2).

## Step C2 — Architecture Needs from Requirements

| Requirement ID | What does the requirement need? | Architecture Response |
| --- | --- | --- |
| FR1 | The student's interests and skills as input. | Application interface with a student profile form plus chat. |
| FR2 / FR5 / NFR3 | Faculty-specific information about lecturers' research areas and FYP rules. | Faculty knowledge source (FYP guidelines, research groups, staff profiles). |
| FR3 | Comparison of suggested topics against past projects. | Past-project knowledge source with a similarity check. |
| FR4 / RAI1 | Every factual claim must carry a verifiable source. | Source tracking in knowledge access, plus a citation check on the output. |
| FR6 / RAI3 | Out-of-scope and proposal-writing requests must be refused. | Scope / safety control on input and an integrity check on output. |
| RAI4 | Personal data must not reach the external model API. | Privacy filter in the input control, before the model call. |
| NFR1 / NFR4 | Responses must meet latency and cost thresholds. | One model call per request on a short path, with latency and cost logged. |
| NFR2 / RAI2 | Relevance and supervisor coverage must be measured. | Evaluation point that logs responses, ratings, latency, cost and supervisor counts. |

## Step C4 — Architecture Decision Record (ADR)

| Decision | Requirement / Constraint | Alternatives Considered | Selected Option | Trade-off Accepted |
| --- | --- | --- | --- | --- |
| Include faculty knowledge access | FR2, FR5, RAI1 — answers must be grounded in faculty documents and cited | Base model only; hand-written static FAQ; dynamic knowledge access | Dynamic faculty knowledge-access component with source tracking | More components and document parsing work, but grounded, citable answers that update when documents change. |
| Dedicated past-project similarity check | FR3 — flag topics that repeat past FYPs | Let the language model judge novelty; no novelty check; separate similarity component | Separate past-project source + similarity check | Extra index and a similarity threshold to tune; broad topics may be wrongly flagged as duplicates. |
| Explicit scope and privacy control on input | FR6, RAI3, RAI4 — refuse out-of-scope requests, keep personal data from the API | Instructions in the prompt only; explicit control component | Explicit input control before the model call | Possible false refusals and a small amount of added latency. |
| Diversity-aware supervisor ranking | RAI2 — avoid over-recommending lecturers with richer profiles | Pure similarity ranking; diversity-aware re-ranking | Diversity-aware re-ranking | Top suggestion may be slightly less relevant (NFR2) in exchange for a fairer spread across lecturers. |

## Initial Requirements Traceability Matrix

| Objective | Requirement | Evaluation Criterion | Architecture Element | Later Evidence |
| --- | --- | --- | --- | --- |
| O1 | FR1 / NFR2 | Recommendation relevance (≥ 80% rated ≥ 4) | Application interface (profile form) + Language model service | Relevance rubric results on 20 test profiles |
| O1 | FR2 / NFR3 | Supervisor match accuracy (≥ 90%) | Faculty knowledge source + Language model service | Supervisor match check against staff profiles |
| O2 | FR3 | Duplicate-topic detection (≥ 80%) | Past-project knowledge source + similarity check | Results on 10 seeded duplicate topics |
| O2 | FR4 / RAI1 | Source citation and support (100% / ≥ 95%) | Knowledge access with source tracking + Output citation check | Citation audit of test responses |
| O2 | FR6 / RAI3 / RAI4 | Refusal rate (≥ 95%); zero personal-data transmissions | Input scope & privacy control + Output integrity check | Safety / scope and privacy test runs |
| O3 | NFR1 / NFR4 / RAI2 | p90 latency < 5 s; cost < US$0.50 / 100 queries; lecturer share ≤ 15% | Evaluation point | Latency, cost and coverage logs |

## Final Review Checklist

- **Does each major component support a requirement or evaluation need?** Yes — every component in the diagram is tagged with the requirement IDs that justify it.
- **Is any data source, safety control or evaluation point missing?** No — faculty and past-project sources, input and output controls, and an evaluation point are all included.
- **Have I added any technology that is not yet justified?** No — components are labelled by function only; specific models, databases and frameworks will be chosen in later topics.
- **Is there a simpler architecture that still satisfies the requirements?** The faculty and past-project sources could be merged into one knowledge source, but keeping them separate makes the novelty check (FR3) clearer to build and evaluate.

### Reflection — Which architecture decision involved the most important trade-off? Which requirement drove it, and what trade-off did you accept?

Adding faculty knowledge access was the most important decision. It was driven by FR2 and RAI1: without faculty documents the system cannot name real UTM lecturers or cite any source. I accepted more complexity — collecting, parsing and keeping documents up to date, and an extra retrieval step that adds latency — in exchange for grounded, verifiable recommendations.
