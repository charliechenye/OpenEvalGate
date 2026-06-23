# Provenance v1 Conformance Fixtures

These fixtures define expected classifications for the Eval-Run Provenance Contract v1.

They are design fixtures for the contract PR, not yet executable OpenEvalGate inputs. Each YAML file contains:

- a representative manifest or an explicit absence state;
- an optional artifact index;
- verification facts that a future implementation would obtain from local files;
- the expected independent classifications;
- expected authorization outcomes;
- expected finding identifiers.

The parser and enforcement PRs should materialize equivalent file trees and use these expectations as test oracles.

## Fixtures

| Fixture | Purpose |
| --- | --- |
| `valid-current-human.yaml` | Complete, verified, current human-reviewed run that may support controlled launch. |
| `stale-policy-input.yaml` | Structurally valid run whose review-policy bytes changed after evaluation. |
| `invalid-run-identity.yaml` | Manifest, result, and artifact identities disagree. |
| `legacy-no-manifest.yaml` | Pre-contract evidence without a manifest; readable but not launch-authorizing. |

## Classification dimensions

Fixtures report separate values for:

- manifest presence;
- validity;
- freshness;
- recency;
- assurance;
- lifecycle.

Do not collapse these into one status. In particular, `invalid` is not equivalent to `legacy_absent`, and `stale` is not equivalent to `expired`.

## Authorization rule

Only evidence that is present, valid, complete, verified, current, and not expired may support controlled launch. Legacy evidence may support documentation review and bounded shadow analysis with an explicit warning.
