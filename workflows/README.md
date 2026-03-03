# Workflow Layer – Automation Orchestration

## Overview

This project uses a Python-based CLI orchestrator (`run_pipeline.py`)
to simulate a production automation workflow under zero-cost constraints.

In a production environment, this orchestration layer could be replaced with:

- n8n
- Zapier
- Airflow
- Supabase Edge Functions
- Internal job schedulers

The current implementation ensures:

- Deterministic execution
- Batch processing
- Safe re-runs (idempotent behavior)
- Folder-driven pairing of demo and onboarding transcripts

---

## Current Execution Flow

1. Scan `transcripts/demo/`
2. Generate v1 configuration from demo transcript
3. Check for matching onboarding transcript
4. If onboarding exists:
   - Apply structured patch
   - Generate v2 configuration
   - Generate structured diff
5. Log execution

---

## Logical Flow Diagram

Demo Transcript  
↓  
Extract Structured Memo (v1)  
↓  
Generate Agent Spec (v1)  
↓  
Check for Onboarding Transcript  
↓  
If exists:  
  → Extract Confirmed Rules  
  → Apply Structured Patch  
  → Generate Agent Spec (v2)  
  → Generate Diff (`changes.json`)

---

## Design Philosophy

The orchestration layer is intentionally:

- Minimal
- Deterministic
- Replaceable
- Zero-cost compliant
- Production-extendable

Each script in `/scripts` acts as a modular workflow unit,
making this pipeline easy to port into n8n or another workflow engine if needed.