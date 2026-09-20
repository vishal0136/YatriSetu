# YatriSetu

## Transit Operations Intelligence System for Delhi Public Transport

YatriSetu is a proposed intelligent public-transport management platform focused on improving Delhi's DTC bus transportation through centralized transit data management, validation, route information, and AI-assisted transportation operations.

The current research prototype focuses primarily on the **Admin AI Agent**, designed to assist transportation administrators in detecting data-quality problems, interpreting validation results, evaluating evidence, and preparing safe database-change recommendations under explicit human approval.

> **Research prototype:** The current implementation focuses on the data-validation and Admin AI Agent pipeline. It does not yet represent a production DTC deployment.

---

## Current Research Focus

The primary research component is the **YatriSetu Transit Operations Intelligence System**.

The system is designed around the following principle:

```text
Raw Transit Data
      ↓
Data Profiling
      ↓
Deterministic Validation
      ↓
Validation Report
      ↓
Admin AI Agent
      ↓
Evidence Verification
      ↓
Safety Validation
      ↓
Administrator Approval
      ↓
Controlled Database Transaction
      ↓
Post-Update Validation
      ↓
Audit Log
```

The LLM is **not given unrestricted permission to modify PostgreSQL**.

The intended architecture separates:

* deterministic validation
* AI-based interpretation and recommendation
* authoritative evidence
* safety policy
* administrator authorization
* database transactions
* post-update verification

---

## Main Objectives

* Centralize DTC transit data.
* Detect data-quality and consistency problems.
* Validate GTFS-style transportation datasets.
* Identify invalid, missing, duplicate, inconsistent, and orphaned records.
* Provide administrators with evidence-based correction recommendations.
* Prevent unsupported AI-generated database modifications.
* Require explicit administrator approval before database changes.
* Maintain traceability of proposed and executed changes.
* Evaluate the performance and limitations of an LLM-based Admin Agent.

---

## Current Technology Stack

### Backend and Data Engineering

* Python
* PostgreSQL
* SQLAlchemy
* Psycopg
* Pandas
* Pandera
* Pydantic

### AI

* Qwen3-8B
* Hugging Face Transformers
* 4-bit NF4 quantization
* PyTorch
* CUDA
* Google Colab
* NVIDIA Tesla T4

### Validation and Testing

* Deterministic validation rules
* Controlled database corruption experiments
* Adversarial recommendation tests
* Referential-integrity testing
* Data-quality testing

### Development

* Git
* GitHub
* VS Code
* Python virtual environment

---

## Dataset

The current prototype uses GTFS-style Delhi public-transit data containing:

* Agency information
* Feed information
* Stops
* Routes
* Calendar/service information
* Trips
* Stop times
* Shapes

The imported prototype database currently contains approximately:

| Table      |   Records |
| ---------- | --------: |
| agency     |         2 |
| calendar   |         1 |
| routes     |     2,554 |
| stops      |     6,812 |
| shapes     |   765,633 |
| trips      |    65,322 |
| stop_times | 2,385,381 |

Raw datasets are intentionally excluded from the Git repository because of their size.

---

## Database

The PostgreSQL database used by the project is:

```text
DTMS
```

A separate test database is used for controlled corruption and safety experiments:

```text
DTMS_TEST
```

Production and experimental databases are kept separate during development.

Database credentials are stored locally through environment variables and are **not committed to GitHub**.

---

## Validation Engine

The validation system currently contains rules covering areas such as:

* Required-field validation
* Duplicate records
* Data-type validation
* Referential integrity
* Latitude/longitude validation
* Geographic anomalies
* Stop-sequence validation
* Arrival/departure-time validation
* Service-date validation
* Service-day configuration
* Missing route shapes
* Route/shape consistency
* Suspicious duplicate stops
* Missing important fields
* Invalid categorical values

The validation framework uses rule identifiers such as:

```text
R001
R002
...
R023
```

Validation results are generated as structured reports that can be consumed by the Admin AI Agent.

---

## Admin AI Agent

The Admin AI Agent receives structured validation findings and produces a structured recommendation.

The recommendation contains information such as:

```text
issue_summary
primary_issue
related_issues
evidence
unknowns
recommended_action
risk_level
confidence
proposed_changes
requires_admin_approval
```

The agent is designed to distinguish between:

### Deterministic responsibilities

* Data validation
* Rule execution
* Referential-integrity checks
* Evidence matching
* Safety checks
* Authorization checks
* Database transaction constraints

### AI responsibilities

* Interpreting validation findings
* Summarizing detected problems
* Formulating recommendations
* Explaining the reasoning behind a proposed change

This separation reduces the risk of allowing an LLM to make unsupported database decisions.

---

## Safety Architecture

A core design principle is:

> **The LLM never directly writes to PostgreSQL.**

A proposed database correction must pass multiple gates.

```text
LLM Recommendation
        ↓
Recommendation Validator
        ↓
Authoritative Evidence
        ↓
Safety Validation
        ↓
Approved Change Set
        ↓
Administrator Approval
        ↓
Database Authorization
        ↓
Controlled Transaction
        ↓
Post-Update Validation
```

The system is designed to block:

* Approval bypass
* Invented validation rules
* Invalid confidence values
* Unsupported corrections
* Missing required fields
* Missing evidence
* Unauthorized tables
* Unauthorized fields
* Mismatched safety-approved changes

---

## Controlled Experiment

The current controlled experiment introduces an invalid latitude value into `DTMS_TEST`.

The experimental corruption is:

```text
stop_id: 1
field: stop_lat
corrupted value: 999.0
```

A controlled authoritative evidence file provides the experimental replacement value.

This value is used **only for the controlled research experiment** and is not claimed to be an official DTC coordinate.

The experiment allows the research pipeline to test:

```text
Detect
  ↓
Interpret
  ↓
Verify evidence
  ↓
Recommend
  ↓
Validate
  ↓
Authorize
  ↓
Update
  ↓
Verify
```

---

## Current Research Status

Completed components include:

* GTFS data profiling
* PostgreSQL DTMS database
* GTFS data import
* Referential-integrity validation
* Deterministic validation engine
* R001–R023 validation framework
* Controlled corruption experiments
* Validation reports
* Admin Agent contracts
* Agent context construction
* Qwen3-8B integration
* Authoritative evidence service
* Read-only database evidence service
* Recommendation safety validation
* Change-authorization layer
* Adversarial safety testing
* Local Git version-control baseline

The remaining core research workflow includes:

* Finalizing the approved-change test
* Authorization adversarial testing
* Safe transactional database update
* Post-update validation
* Audit logging
* Rollback/recovery testing
* End-to-end experiment
* Research performance evaluation
* Final research analysis

---

## Repository Structure

```text
YatriSetu/
│
├── backend/
│   └── app/
│       ├── ai/
│       │   ├── agent_loop.py
│       │   ├── change_authorization.py
│       │   ├── context_builder.py
│       │   ├── contracts.py
│       │   ├── recommendation.py
│       │   ├── recommendation_validator.py
│       │   ├── report_loader.py
│       │   ├── safety_policy.py
│       │   ├── services/
│       │   └── test_*.py
│       ├── api/
│       ├── models/
│       ├── schemas/
│       └── services/
│
├── data/
│   ├── authoritative/
│   └── gtfs_profile.txt
│
├── docs/
│   └── data_dictionary.md
│
├── scripts/
│   ├── db_connection.py
│   ├── profile_database.py
│   ├── profile_gtfs.py
│   ├── import_*.py
│   └── check_tables.py
│
├── validation/
│   ├── rules/
│   ├── schemas/
│   ├── testing/
│   └── validation_engine.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Security and Repository Policy

The following are intentionally excluded from Git:

```text
.env
.venv/
data/raw/
validation/reports/
__pycache__/
*.dump
*.backup
*_backup.py
```

Database passwords, API keys, model files, large raw datasets, database dumps, and generated artifacts should not be committed to the repository.

---

## Research Direction

The research investigates whether an LLM-assisted administrative system can help interpret transportation-data quality issues while maintaining deterministic safety controls and human authorization.

The central research principle is:

```text
AI-assisted decision support
+
Deterministic validation
+
Evidence verification
+
Human approval
=
Controlled database-change workflow
```

The system is intended to support administrators rather than replace administrative authority.

---

## Future Components

Planned extensions include:

* FastAPI administrative API
* Admin dashboard
* More authoritative transportation-data sources
* Expanded correction workflows
* Audit-log database
* Transaction rollback mechanisms
* Real-time transit updates
* Passenger-facing AI assistant
* DTC and Delhi Metro integration
* Live bus tracking
* Route planning
* Passenger mobile application
* Production-scale testing

---

## License

License information will be added when the project's distribution and research-publication requirements are finalized.

---

## Project

**YatriSetu**

Delhi Public Transport Management and AI-Assisted Transit Operations Research Prototype.
