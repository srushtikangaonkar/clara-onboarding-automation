# Clara Answers – Zero-Cost Onboarding Automation Pipeline

## Overview

This project implements a structured, version-controlled automation pipeline that converts:

**Demo Call Transcript → Preliminary Agent Configuration (v1)**  
**Onboarding Transcript → Confirmed Operational Configuration (v2)**  
**→ Structured Change Log (Diff)**  

It simulates Clara’s real onboarding automation challenge:

> Unstructured human conversations → structured operational rules → deployable AI voice agent configuration.

The system is designed to be:

- Deterministic (no hallucination)
- Explicitly version-controlled (v1 → v2)
- Idempotent and safe to re-run
- Batch-capable
- Fully local (zero-cost compliant)
- Reproducible

---

# Problem Context

Service trade businesses require precise call handling logic, including:

- Emergency vs non-emergency routing
- Business hours vs after-hours behavior
- Transfer timeouts and fallback protocols
- Integration constraints
- Escalation logic

Demo calls provide exploratory, high-level information.  
Onboarding calls confirm operational precision.

The engineering challenge is to convert evolving conversational inputs into structured, production-ready AI agent configurations — without hallucination, destructive updates, or silent assumptions.

This repository implements that automation layer.

---

# Architecture

## 1. Input Layer
transcripts/
demo/
onboarding/


- Each demo transcript generates a **v1 configuration**
- Each onboarding transcript updates the same account to **v2**
- File naming ensures deterministic pairing

---

## 2. Schema-First Design

`scripts/schema.py`

Defines structured models:

- `AccountMemo`
- `BusinessHours`
- `RoutingRule`
- `CallTransferRules`

Why schema-first?

- Enforces structured configuration boundaries
- Enables safe patch logic
- Prevents accidental data drift
- Makes missing data explicit

This mirrors how production configuration systems are built.

---

## 3. Demo → v1 Pipeline

`scripts/extract_demo.py`

Processes demo transcripts into:

outputs/accounts/<ACCOUNT_ID>/v1/account_memo.json


Design principles:

- Extract only explicitly stated data
- Leave missing fields as `null`
- Add unresolved items to `questions_or_unknowns`
- Avoid inferred routing logic

This ensures exploratory demo data does not become accidental configuration.

---

## 4. Agent Specification Generator

`scripts/generate_agent_spec.py`

Generates a structured Retell-compatible agent draft including:

- Office-hours call flow
- After-hours call flow
- Emergency confirmation logic
- Transfer protocol
- Transfer failure fallback
- Prompt hygiene constraints

The generated prompt:

- Does not mention internal tools
- Collects only necessary information
- Separates business-hours and after-hours logic
- Follows deterministic routing rules

---

## 5. Onboarding → v2 Update Layer

`scripts/update_onboarding.py`

Workflow:

1. Load v1 memo
2. Extract confirmed onboarding rules
3. Apply structured patch
4. Preserve unrelated configuration
5. Regenerate agent spec
6. Generate structured diff (`changes.json`)

Key guarantees:

- No destructive overwrites
- No silent field mutation
- Explicit change tracking via DeepDiff
- Deterministic configuration update

This models safe production configuration evolution.

---

## 6. Batch Orchestration Layer

`scripts/run_pipeline.py`

- Scans demo directory
- Generates v1 for each transcript
- Matches onboarding file
- Generates v2 if available
- Logs execution

Properties:

- Folder-driven
- Batch-capable
- Safe to re-run
- No duplicate constraints
- No cascading corruption

---

# Output Structure
outputs/
accounts/
<ACCOUNT_ID>/
v1/
account_memo.json
agent_spec.json
v2/
account_memo.json
agent_spec.json
changes.json


Version history is preserved.  
Changes are explicit and auditable.

---

# Core Engineering Principles

## 1. No Hallucination Policy

If demo does not confirm:

- Business hours
- Timezone
- Routing rules
- Integration constraints

The system:

- Leaves fields `null`
- Flags ambiguity in `questions_or_unknowns`

No assumption becomes configuration.

---

## 2. Explicit Versioning

- v1 = Demo-derived configuration
- v2 = Onboarding-confirmed configuration

Changes are logged structurally, not narratively.

---

## 3. Deterministic Patch Logic

Onboarding updates:

- Modify only confirmed fields
- Avoid duplicates
- Preserve unrelated settings

This prevents silent configuration corruption.

---

## 4. Zero-Cost Compliance

- No paid APIs
- No external LLM calls
- Fully local execution
- Rule-based structured extraction

All constraints satisfied without external dependencies.

---

# How to Run

## 1. Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


## 2. Execute Full Pipeline
python scripts/run_pipeline.py


The pipeline will:

- Generate v1 configurations
- Apply onboarding updates
- Produce structured diffs
- Preserve version history

---

# Known Limitations

- Rule-based extraction may not handle highly complex phrasing.
- Emergency detection is keyword-driven.
- Routing logic extraction can be extended further.
- CLI-driven (no dashboard UI).

---

# Production Extensions (Future Work)

With production access:

- Integrate structured LLM parsing for improved extraction robustness
- Add conflict detection warnings during onboarding patch
- Add validation for inconsistent business hours
- Integrate with Retell API directly
- Replace file storage with database-backed configuration
- Add visual diff dashboard for configuration review

---

# Conclusion

This system treats onboarding automation as structured configuration management — not as transcript parsing.

It is:

- Schema-first
- Version-aware
- Diff-tracked
- Deterministic
- Safe under ambiguity
- Designed for scale

It simulates the internal infrastructure required to operationalize AI voice agents reliably.

---

# Author

Srushti Rajendra Kangaonkar  