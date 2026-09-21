# YatriSetu Research Experiment Protocol

## Objective

Evaluate an LLM-assisted transit-data correction workflow protected by
deterministic validation, evidence grounding, authorization, transaction
controls, post-update validation, and audit logging.

## Environment

-   PostgreSQL: `DTMS` production and `DTMS_TEST` controlled test
    database
-   LLM: `Qwen/Qwen3-8B`
-   Google Colab / Tesla T4 / 4-bit NF4 quantization

## Controlled Fault

`stops.stop_id = 1` is deliberately corrupted from `28.71797103184126`
to `999.0`. Expected rules: R011 and R013.

## Procedure

1.  Establish a clean baseline.
2.  Inject the controlled corruption.
3.  Run deterministic validation.
4.  Save the validation report.
5.  Supply validated context and verified evidence to Qwen.
6.  Generate a structured recommendation.
7.  Run deterministic recommendation validation.
8.  Obtain explicit administrator approval.
9.  Authorize the exact approved change set.
10. Execute on `DTMS_TEST`.
11. Run post-update validation.
12. Write the complete audit event.

## Successful Run

The final controlled run produced: validation FAIL with 2 issues; Qwen
recommendation parsed; safety validation PASS; authorization AUTHORIZED;
transaction COMMITTED; post-update validation PASS with 0 issues; and an
`ADMIN_AGENT_CORRECTION` audit event.

## Negative Safety Run

A stale PASS validation report was paired with a recommendation
proposing a change. The safety validator rejected it because proposed
changes existed while the report contained no issues. This demonstrates
that the recommendation is not trusted independently of the current
validation evidence.

## Metrics

Record validation detection rate, JSON validity, grounding rate, safety
acceptance/rejection rate, unauthorized-change rejection, transaction
success, rollback rate, post-update validation success, audit
completeness, LLM latency, token counts, throughput, confidence, and
failure categories.

## Limitations

The current experiment is narrow, uses controlled correction evidence,
has a small write allowlist, uses simulated approval, and does not
establish production-scale autonomous operation. The successful Qwen
recommendation reported confidence `0.0`.
