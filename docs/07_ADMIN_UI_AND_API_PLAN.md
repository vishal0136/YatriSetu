# YatriSetu Admin UI and API Plan

## Purpose

Expose the tested backend safety workflow to a human administrator
without bypassing backend controls.

## Planned API

-   `GET /admin/validation/latest`
-   `GET /admin/issues`
-   `GET /admin/agent/recommendation`
-   `POST /admin/agent/approve`
-   `POST /admin/agent/reject`
-   `GET /admin/audit`

## Dashboard

Show dataset status, issue count, severity, affected records, current
value, proposed value, evidence, AI reasoning, risk level, approval
controls, transaction status, post-update validation, and audit history.

## Approval View

``` text
Issue: Invalid latitude
Record: stop_id = 1
Current: 999.0
Proposed: 28.71797103184126
Evidence: YatriSetu Controlled Authoritative Evidence
Risk: HIGH
[ APPROVE ] [ REJECT ]
```

## Enforcement

The UI must never send raw SQL or directly modify PostgreSQL. It must
call the backend authorization and transaction workflow.

## Audit

Every approved correction should record the timestamp, dataset,
validation report, recommendation, safety result, administrator identity
and decision, authorization result, transaction result, and post-update
validation result.
