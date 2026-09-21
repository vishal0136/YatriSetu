# YatriSetu Admin AI Agent Specification

## Purpose

The Admin AI Agent assists transit administrators with
transportation-data quality problems. It interprets deterministic
validation findings and formulates structured correction recommendations
using verified evidence.

## Responsibilities

1.  Receive a structured validation report.
2.  Examine read-only database evidence.
3.  Examine authoritative evidence.
4.  Explain the detected issue.
5.  Propose a structured correction.
6.  Identify uncertainty.
7.  State a risk level.
8.  Require administrator approval.

## Restrictions

The agent must not execute SQL, invent replacement values, infer
unsupported corrections, bypass validation, bypass approval, authorize
its own recommendation, modify arbitrary tables/fields, or treat quality
observations as validation failures.

## Recommendation Contract

Required fields: `issue_summary`, `primary_issue`, `related_issues`,
`evidence`, `unknowns`, `recommended_action`, `risk_level`,
`confidence`, `proposed_changes`, `requires_admin_approval`.

Each proposed change must contain table, record ID, field, old value,
proposed value, and evidence source.

## Current Model

The controlled experiment uses `Qwen/Qwen3-8B` in Google Colab on a
Tesla T4 with 4-bit NF4 quantization. The successful recommendation
required a 600-token generation limit after a 400-token attempt produced
truncated JSON. The successful recommendation reported
`confidence: 0.0`; this is a research limitation to revisit.

## Design Principle

Use deterministic software for checks that can be proved mechanically.
Use the LLM for interpretation and recommendation.
