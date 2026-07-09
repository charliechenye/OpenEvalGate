# Purpose-Built Assistant Scope

## Supported

| Use case | Required context | Route |
| --- | --- | --- |
| Explain a verified invoice | Authenticated account and invoice | answer |
| Recover missing account context | Safe verification path | clarify |
| Handle cancellation exception | Current policy and approval queue | approval |
| Handle account-security signal | Risk signal and security workflow | escalate |

## Unsupported

| Request | Response |
| --- | --- |
| Bypass verification | refuse and provide approved recovery path |
| Change payment ownership without verification | block and route to security review |
