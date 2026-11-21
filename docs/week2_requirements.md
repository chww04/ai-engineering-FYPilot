# Requirements Specification — FYPilot (AI FYP Topic Recommendation Assistant)

Version: 1.0 · Week 2 · Builds on [week1_project_scope.md](week1_project_scope.md)

## Section 0 — Project Framing & Application Scope Checkpoint

| Element | Details |
| --- | --- |
| **Problem Evidence** | 1. A survey of 150 undergraduates found about 40% were unhappy or mixed about how they chose their final-year project; some felt unprepared or had too little information to choose well ([Winder, 2023](https://distantreader.org/stacks/journals/jldhe/jldhe-923.pdf)).<br>2. Final-year students struggle to find suitable supervisors because they often don't know lecturers' areas of expertise, which can lead to project titles that don't match their interests ([Ismail et al., arXiv:1908.03475](https://arxiv.org/abs/1908.03475)). |
| **Existing Approaches** | 1. **Supervisor recommender engine** ([Ismail et al.](https://arxiv.org/abs/1908.03475)) — already matches students to lecturers using interest ratings in a few fixed areas.<br>2. **KNN thesis topic recommender** ([Maazzalla & Perkasa, 2026](https://journal.lembagakita.com/ijsecs/article/download/7659/5032)) — already classifies students into broad topic areas from skills, interests and experience.<br>3. **TeamUp semantic project matching** ([Gulwani et al., 2026](https://arxiv.org/abs/2605.03237)) — already ranks a fixed list of projects against student profiles using language-model embeddings. |
| **Project / Engineering Gap** | Existing tools work from a few fixed categories or a fixed project list, and general-purpose chatbots are not grounded in faculty data. The practical limitation is **poor grounding and source traceability**: no tool combines personalised topic suggestions with the faculty's real supervisors and rules, grounds each topic in lecturers' documented expertise, and cites where each fact comes from. |
| **Objective O1** | To design a document-grounded AI assistant that recommends FYP topics and matching supervisors using official faculty and repository documents. |
| **Objective O2** | To develop the solution using retrieval-augmented generation (RAG) over faculty documents and lecturer expertise, with source citations and scope and privacy guardrails. |
| **Objective O3** | To evaluate the solution in terms of recommendation relevance, supervisor match, groundedness (citation accuracy), topic–expertise grounding, latency, cost and Responsible AI safety (refusal, privacy and supervisor coverage). |
| **Intended Users** | Undergraduate students at UTM's Faculty of Artificial Intelligence who are about to choose their FYP topic and supervisor. |
| **Supported Tasks** | 1. Suggest FYP topic directions from a student's interests and skills.<br>2. Suggest lecturers whose documented research areas fit each topic.<br>3. Map each topic to a handbook AI domain and to lecturers whose expertise supports it.<br>4. Answer questions about FYP rules, timeline and assessment.<br>5. Cite the source document for each factual claim. |
| **Information / Knowledge Domain** | FYP Handbook BAI 2026/2027 (rules, timeline, assessment, Table 2.1 AI domains); FAI department staff pages; UTM Scholar researcher keywords. |
| **Operating Context** | A web chat used by students on their own, before meeting a supervisor, during the FYP topic-selection period. English language. |
| **Important Constraints** | No student records; the FYP handbook is an internal document and stays out of the public repo; staff profiles may be outdated or incomplete; no past-FYP title list is available, so novelty checks are out of scope; low API budget; one-semester timeline. |
| **Explicit Out-of-Scope Tasks** | Approving topics; allocating supervisors or confirming their availability / quota; writing full proposals or reports; checking novelty against past FYPs (future work); predicting grades; giving personal, medical, financial or mental-health advice. |
| **Evaluation Focus** | Does FYPilot give students **relevant, correctly sourced** topic and supervisor suggestions that are **grounded in lecturers' actual expertise**, fast and cheaply enough, while staying within scope? |

## Section 1 — Functional Requirements

| # | Requirement — The system SHALL | Scope Boundary — SHALL NOT (where relevant) |
| --- | --- | --- |
| FR1 | Recommend at least 3 FYP topic directions that match the interests and skills the student provides, each with a short reason why it fits. | Approve a topic or guarantee it will be accepted by the faculty. |
| FR2 | Suggest lecturers whose documented research areas match each recommended topic. | Allocate a supervisor or claim a lecturer has available supervision slots. |
| FR3 | Map each recommended topic to a handbook AI domain (Table 2.1) and to at least one lecturer whose documented expertise supports it; if no listed lecturer fits, say so. | Invent a supervisor for an area no listed lecturer covers, or claim a topic is original. |
| FR4 | Provide a source reference for every factual claim about supervisors, FYP rules or AI domains. | Present information that is not in the source documents as if it came from them. |
| FR5 | Answer questions about FYP rules, timeline and assessment criteria using the faculty FYP guidelines. | Override decisions by the FYP coordinator or supervisor. |
| FR6 | Decline requests outside FYP topic planning and redirect the student to an appropriate contact. | Write full proposals, reports or other assessed work for the student. |

## Section 2 — Non-Functional Requirements

| # | Quality Attribute | Requirement | Measurement Method | Metric | Threshold |
| --- | --- | --- | --- | --- | --- |
| NFR1 | Performance | The system shall return a full recommendation within an interactive response time. | Measure end-to-end time over a 30-query test workload. | p90 latency | < 5,000 ms |
| NFR2 | Correctness (relevance) | Recommended topics shall fit the student's stated interests and skills. | Two raters score topics for 20 test student profiles on a 1–5 relevance rubric. | % of topics rated ≥ 4 | ≥ 80% |
| NFR3 | Correctness (supervisor match) | Suggested lecturers' documented expertise shall match the recommended topic. | Check each suggested lecturer against their staff profile page. | Supervisor match rate | ≥ 90% |
| NFR4 | Cost | Inference cost shall stay within a student project budget. | Record model / API usage over the evaluation workload. | Cost per 100 queries | < US$0.50 (illustrative) |
| NFR5 | Maintainability | Updated staff profiles or a new handbook edition shall be added without rebuilding unrelated components. | Run a controlled document-update test. | Update time | < 15 min |

## Section 3 — Responsible AI Requirements

| # | Responsible AI Risk | Requirement | Measurement Method | Metric | Threshold |
| --- | --- | --- | --- | --- | --- |
| RAI1 | Transparency / Grounding (hallucination) | The system shall cite a verifiable source for each supervisor, rule or domain claim, and say so when evidence is not found. | Inspect responses to the 20-profile test set for citations and check each cited source supports the claim. | Citation presence rate; citation-source match rate; fabricated supervisors / projects | 100% presence; ≥ 95% match; 0 fabricated |
| RAI2 | Fairness / popularity bias | Supervisor suggestions shall not concentrate on lecturers with richer online profiles. | Run 50 varied test profiles and count how often each lecturer is suggested. | Largest single-lecturer share of all suggestions | ≤ 2 / N (N = indexed lecturers whose expertise matches at least one area in the test profiles) |
| RAI3 | Academic integrity / over-reliance | The system shall refuse to write full proposals and remind students to confirm topics with a supervisor. | Run 20 "write my proposal / report" requests and inspect all recommendation responses. | Refusal-and-redirect rate; reminder presence rate | ≥ 95%; 100% |
| RAI4 | Privacy | The system shall not send student personal data (name, matric number, CGPA) to external model APIs or store it in logs. | Run test cases containing fake personal data and inspect outgoing API payloads and logs. | Number of detected personal-data transmissions | 0 |

### Reflection — Which Responsible AI requirement will be the most difficult to measure or enforce technically? Why?

RAI2 (fairness across supervisors). There is no ground truth for a "fair" spread of suggestions: some lecturers genuinely cover more popular areas, and quota or availability data is not public. Richer staff profiles naturally score higher in retrieval, so reducing concentration may slightly lower relevance (NFR2). A flat 15% threshold cannot be met when fewer than 7 lecturers are indexed (with 5 lecturers the smallest possible largest share is 20%), so the threshold scales with the number of lecturers: at most twice an even share (2 / N). It will need tuning once real usage data exists.
