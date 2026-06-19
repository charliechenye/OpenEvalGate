# Presales Product Advisor

**Assistant type:** presales
**Launch owner:** Revenue Product Team
**Review date:** 2026-05-23

## Purpose

Help prospective customers understand product fit, integrations, pricing boundaries, and next sales steps without inventing commitments or unsupported roadmap claims.

## Supported Use Cases

| Use case | User intent | Success criteria | Required context | Owner |
| --- | --- | --- | --- | --- |
| Product fit | Prospect asks whether the product supports a workflow. | Assistant answers from approved product facts. | Product catalog and integration matrix. | Revenue Product |
| Pricing boundary | Prospect asks for price or discount. | Assistant routes to sales for non-public pricing. | Public pricing policy and account segment. | Sales Ops |

## Workflow And Capability Allocation

| Workflow or subagent | Job | Risk tier | Model assignment | Mandatory controls | Fallback | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Product fit advisor | Grounded product and integration guidance | medium | adaptive: approved arena pool | Product catalog, integration matrix, output critic | Sales follow-up | Revenue Product |
| Public pricing specialist | Explain published pricing | medium | fixed: balanced-model | Public pricing policy and no discount authority | Pricing approval | Sales Ops |
| Pricing approval | Review discount requests | high | none: human workflow | Approval checkpoint and audit event | Policy block | Sales Ops |
| Legal and security review | Review binding or regulated commitments | high | none: human workflow | Approved collateral and specialist authority | Policy block | Legal and Security |
