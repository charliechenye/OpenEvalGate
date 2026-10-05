# Schema maintenance entry point

The removed `golden_eval_case_schema.yaml` duplicated a human design reference
whose `schema_version: 0.1.0` described that reference's revision, not the
current CLI format. Its `must_do`, `must_not_do`, and `scoring` suggestions
were not valid V1 case fields.

Use the maintained [formal V1 JSON schema](../../../../schemas/eval-cases-v1.schema.json)
and [actual validator](../../../../openevalgate/schema.py). Input documents
require exactly `schema_version: "1"` and an `eval_cases` list. The central
[design-reference pointer and migration notes](../../../../schemas/golden_eval_case_schema.yaml)
are documentation, not a schema to execute or a document to pass to the CLI.
