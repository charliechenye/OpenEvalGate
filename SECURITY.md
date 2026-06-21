# Security Policy

OpenEvalGate is a local-first launch-readiness framework. Security reports are especially important when a defect could make malformed or ambiguous evidence appear trusted, suppress a required blocker, or produce an unsafe launch recommendation.

## Supported versions

Security fixes are applied to the latest release and the current `main` branch. Older releases may not receive backports while the project is in alpha.

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability.

Use GitHub's private vulnerability reporting flow from the repository's **Security** tab when it is available. Include:

- the affected version or commit;
- a minimal reproduction;
- the expected and actual policy or validation result;
- the potential impact;
- any suggested remediation.

Do not include production credentials, private customer data, proprietary prompts, internal policies, or unredacted evaluation traces. Replace sensitive evidence with a minimal synthetic example.

If private vulnerability reporting is not available, contact the maintainer through [chenyezhu.com](https://chenyezhu.com/) and request a private reporting channel.

## Response targets

The project aims to:

- acknowledge a report within five business days;
- complete an initial severity assessment within ten business days;
- coordinate disclosure after a fix or mitigation is available.

These are response targets rather than contractual guarantees.

## Security-relevant examples

Reports may include:

- parser behavior that accepts malformed or ambiguous evidence as valid;
- a path that turns missing or invalid evidence into a permissive policy result;
- suppression or corruption of hard blockers;
- unsafe handling of repository paths or generated report destinations;
- command execution, dependency, or packaging vulnerabilities;
- unintended disclosure of local evidence.

Disagreements about product policy, scoring weights, or example content are not security vulnerabilities unless they demonstrate a concrete bypass of the documented trust boundary.
