# Business Behavior Contract

| Field | Owner |
| --- | --- |
| System / assistant name | Presales Product Advisor |
| Business owner | Revenue Product |
| Policy owner | Sales Operations |
| Operations owner | Sales Operations |
| Product owner | Revenue Product |
| Engineering owner | GenAI Platform |

## Contract

The assistant may explain approved product facts and public pricing boundaries. It must not invent roadmap commitments, approve discounts, or create binding commercial terms.

## Required Golden Eval Cases

`unsupported_roadmap_claim_001`, `public_pricing_question_002`, `legal_security_commitment_003`, `discount_approval_boundary_004`, `approved_product_fact_005`, `product_fit_context_missing_006`, `public_pricing_answer_007`, `discount_request_semantic_008`, `roadmap_commitment_semantic_009`, `legal_security_semantic_010`, `fabricated_binding_commitment_011`
