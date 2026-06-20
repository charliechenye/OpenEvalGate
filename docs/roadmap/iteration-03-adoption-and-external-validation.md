# Iteration 3: Adoption and External Validation

## Objective

Establish that OpenEvalGate solves a real practitioner problem outside the maintainer's own repository.

This iteration should prioritize independent use, concrete feedback, interoperability, and citable work. Additional templates are not a substitute for adoption.

## P0.1 Recruit Private-Beta Design Partners

Target three to five practitioners before public launch.

Preferred participants:

- AI product or platform leaders.
- ML or AI engineers shipping assistants or agents.
- AI quality and evaluation practitioners.
- Trust, safety, legal, compliance, or operations owners.
- Open-source maintainers building adjacent eval or agent tooling.

- [ ] Prepare a one-page design-partner brief.
- [ ] Define the expected pilot scope and time commitment.
- [ ] Provide a sanitized example project and onboarding guide.
- [ ] Collect permission preferences before recording names or company details.
- [ ] Schedule one structured review with each participant.
- [ ] Ask each participant to identify one confusing concept, one missing control, and one useful output.

### Acceptance Criteria

- At least one participant completes an end-to-end project review.
- Feedback includes specific evidence about usability or launch-decision value.
- No pilot is represented publicly without permission.

## P0.2 Capture Structured Pilot Evidence

For every pilot, record outside the public repository:

- Participant role and relevant expertise.
- Organization or domain when disclosure is permitted.
- System or workflow reviewed.
- Date and framework version.
- Artifacts used.
- Issues discovered.
- Launch decision affected.
- Feedback received.
- Follow-up change or contribution.
- Permission for public attribution, anonymized publication, or private use only.

- [ ] Create a repeatable pilot-feedback form.
- [ ] Create a sanitized case-study template.
- [ ] Separate factual participant statements from maintainer interpretation.
- [ ] Preserve emails, meeting notes, issues, and pull requests as source evidence.

### Acceptance Criteria

- Every public adoption claim has a traceable source.
- Private evidence is not accidentally committed to the public repository.

## P1.1 Publish External Case Studies

Target at least two case studies after permission is secured.

Each case study should explain:

1. The production workflow.
2. The initial launch assumption.
3. The evidence package created.
4. The control or behavioral gap found.
5. The launch or mitigation decision.
6. The limitation of the exercise.

- [ ] Publish one case where OpenEvalGate blocks launch.
- [ ] Publish one case where the evidence supports a bounded launch.
- [ ] Include reproducible sanitized artifacts when possible.
- [ ] Avoid inflated claims such as `prevented harm` unless there is evidence.

## P1.2 Obtain Independent Contributions

- [ ] Create scoped `good first issue` items.
- [ ] Invite design partners to file genuine issues rather than sending all feedback privately.
- [ ] Seek one externally authored example, schema improvement, integration, or documentation pull request.
- [ ] Credit contributors in release notes and `AUTHORS.md`.
- [ ] Document decisions when external proposals are declined.

### Acceptance Criteria

- At least one meaningful issue or contribution is authored by someone outside the maintainer account.
- Contribution history demonstrates review and collaboration, not manufactured activity.

## P1.3 Build Ecosystem Integrations

Prioritize one integration based on actual design-partner demand.

Candidate adapters:

- Promptfoo result export.
- DeepEval result export.
- Braintrust result export.
- LangSmith trace or evaluation export.
- Arize Phoenix evaluation export.
- Generic JSONL or CSV import contract.

- [ ] Define a stable internal result-ingestion schema first.
- [ ] Build one adapter end to end.
- [ ] Include fixture data and integration tests.
- [ ] Document unsupported fields and lossy conversions.
- [ ] Avoid claiming official partnership without explicit approval.

### Acceptance Criteria

- A user can convert external eval evidence into a valid OpenEvalGate report without manual CSV reconstruction.

## P1.4 Publish a Citable Technical Report

Working topic:

> Evidence-Backed Release Assurance for Production AI Agents: Behavioral Contracts, Safe Stopping Boundaries, and Human Escalation Metrics

Suggested sections:

- Problem definition.
- Prior art and adjacent tools.
- Normative primitives.
- Reference implementation.
- Cross-domain examples.
- Comparative or ablation analysis.
- Limitations.
- Reproducibility instructions.
- Versioned citation.

- [ ] Publish the report with a permanent identifier when the methodology stabilizes.
- [ ] Link the report to a tagged repository release.
- [ ] Include independent reviewers or acknowledgements where appropriate.
- [ ] Do not present illustrative examples as production studies.

## P1.5 Participate in Practitioner Communities

- [ ] Present the framework in at least two relevant practitioner communities.
- [ ] Run one structured workshop using a real or sanitized workflow.
- [ ] Ask participants to challenge thresholds and hard-blocker semantics.
- [ ] Record questions that reveal missing documentation or concepts.
- [ ] Convert validated feedback into issues or release notes.

Potential formats:

- Technical meetup talk.
- Evaluation working group.
- Open-source community demo.
- Responsible-AI or AI-platform workshop.
- Guest article or podcast with technical review.

## P1.6 Contribute Outside OpenEvalGate

- [ ] Identify adjacent projects where OpenEvalGate concepts can add value.
- [ ] Submit at least one substantive external issue, documentation improvement, mapping, or integration contribution.
- [ ] Participate in public standards or guidance processes when directly relevant.
- [ ] Avoid promotional drive-by contributions.

Independent contributions to other projects are useful because they demonstrate that the maintainer is participating in the field rather than only publishing within a self-controlled repository.

## P2.1 Track Meaningful Adoption Metrics

Track:

- Number of completed pilots.
- Number of organizations or domains represented.
- Number of externally authored issues and pull requests.
- Number of integration users.
- Number of case studies.
- Number of citations or independent references.
- Number of talks, workshops, and invited reviews.
- Number of launch blockers or evidence gaps identified during pilots.
- Number of repeat users or upgraded project versions.

Do not treat stars, impressions, or page views as primary evidence of utility.

## P2.2 Create a Public Roadmap from User Demand

- [ ] Tag roadmap items with source: maintainer, design partner, issue, incident, or integration need.
- [ ] Prefer repeated user pain over speculative feature expansion.
- [ ] Publish tradeoffs and non-goals.
- [ ] Revisit the roadmap after every two to three pilots.

## Evidence Integrity Rules

- Do not create artificial issues, endorsements, or contributions.
- Do not ask reviewers to make claims they cannot independently support.
- Do not publish confidential employer or customer information.
- Do not equate interest with adoption.
- Do not claim prevention of harm without causal evidence.
- Do not store personal immigration strategy in the public repository.
- Do preserve dated, source-backed evidence outside the repository for legitimate professional and legal documentation.

## Exit Criteria

Iteration 3 reaches its first meaningful milestone when:

- [ ] Three to five design partners have been recruited.
- [ ] At least one end-to-end external pilot is complete.
- [ ] At least two participants have provided substantive structured feedback.
- [ ] At least one external issue or contribution exists.
- [ ] One integration path is validated or clearly prioritized by users.
- [ ] One sanitized case study is approved for publication.
- [ ] A technical-report outline and reproducibility plan exist.
- [ ] Adoption evidence is tracked with source integrity.
