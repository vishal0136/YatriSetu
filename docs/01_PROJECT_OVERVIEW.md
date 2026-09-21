# YatriSetu --- Project Overview

## Purpose

YatriSetu is a Delhi public-transit management and travel platform
focused on DTC bus operations, with future Delhi Metro integration. The
current research prototype focuses primarily on an Admin AI Agent /
Transit Operations Intelligence System.

## Research Focus

The system investigates whether an LLM can assist administrators in
interpreting transportation-data quality issues and proposing
evidence-grounded corrections while deterministic controls prevent
unsafe database modifications.

## Core Principle

`Detect → Recommend → Validate → Approve → Authorize → Execute → Verify → Audit`

The LLM is a recommendation component, not an autonomous database
administrator. It must never directly execute SQL against the production
database.

## Current Technology

-   Python
-   PostgreSQL
-   Qwen/Qwen3-8B for the controlled LLM experiment
-   Pandas / NumPy / Pandera
-   SQLAlchemy / psycopg
-   Pytest
-   Git / GitHub
-   FastAPI API layer planned
-   Kotlin + Jetpack Compose for the future passenger application

## Database Environments

-   `DTMS`: production database; research experiments must not write to
    it.
-   `DTMS_TEST`: controlled research database used for corruption,
    correction, rollback, and validation experiments.

## Current Controlled Experiment

`stops.stop_id = 1` was deliberately corrupted from `28.71797103184126`
to `999.0`. Expected findings were R011 and R013. The correction value
is controlled experimental evidence and is not claimed to be an official
DTC coordinate.

## Current Result

The controlled pipeline has passed validation, Qwen recommendation
generation, deterministic recommendation validation, explicit approval,
authorization, PostgreSQL transaction, post-update validation, and audit
logging.

## Scope Boundary

This is a controlled research prototype, not evidence of unrestricted
production-ready autonomous transportation-data modification.
