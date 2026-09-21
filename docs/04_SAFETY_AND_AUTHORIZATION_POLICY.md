# YatriSetu Safety and Authorization Policy

## Objective

Prevent an LLM-generated recommendation from directly or indirectly
causing an unsafe database modification.

## Mandatory Gates

1.  A deterministic validation issue exists.
2.  The recommendation is structurally valid.
3.  The recommendation is grounded in the validation report.
4.  Proposed changes have authoritative evidence.
5.  `requires_admin_approval` is `true`.
6.  The proposed change set exactly matches the safety-approved set.
7.  Table and field are allowlisted.
8.  Old and proposed values differ.
9.  Evidence source is present.
10. An administrator explicitly approves the change.
11. The transaction verifies the old value.
12. The transaction verifies the new value.
13. Post-update validation succeeds.
14. The lifecycle is audited.

## Current Allowlists

-   Table: `stops`
-   Fields: `stop_lat`, `stop_lon`

## Approval

The prototype uses an explicit administrator decision such as `APPROVE`,
represented with an administrator ID and timestamp. The LLM cannot
manufacture approval.

## Transaction Safety

The transaction service uses parameterized values, allowlists, old-value
verification, exactly-one-row verification, post-update verification,
and rollback on exceptions.

## Production Rule

Research experiments write only to `DTMS_TEST`; `DTMS` remains outside
the controlled write path.

## Evidence Rule

`28.71797103184126` is controlled experimental evidence, not an official
DTC or government-authoritative coordinate.

## Rejection Behavior

Safety rejection is a successful safety outcome. Unsupported,
ungrounded, stale, or incomplete recommendations must be blocked.
