# YatriSetu Admin AI System Architecture

## Logical Flow

``` text
Raw / Existing Transit Data
          |
          v
   Data Profiling
          |
          v
 Deterministic Validation Engine
          |
          v
   Validation Report
          |
          v
   Read-only DB Evidence
          |
          v
 Authoritative Evidence Service
          |
          v
       Qwen3-8B
          |
          v
 Structured Recommendation
          |
          v
 Recommendation Safety Validator
          |
          v
 Explicit Administrator Approval
          |
          v
 Change Authorization
          |
          v
 PostgreSQL Transaction
          |
          v
 Post-update Validation
          |
          v
      Audit Log
```

## Trust Boundaries

-   Deterministic validation detects machine-checkable problems.
-   Evidence services supply database state and verified correction
    evidence.
-   The LLM produces recommendations only.
-   The safety validator decides whether the recommendation is grounded
    and permitted.
-   Authorization requires explicit administrator approval and
    allowlists.
-   Transaction execution accepts only an authorization result.
-   Audit logging records the lifecycle.

## Current Write Allowlist

Table: `stops` Fields: `stop_lat`, `stop_lon`

## Failure Principle

At any safety gate failure, the pipeline stops.
