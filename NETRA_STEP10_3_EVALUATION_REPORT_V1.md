# NETRA_STEP10_3_EVALUATION_REPORT_V1

## A. Model
* Qwen model: Qwen3-4B-Instruct-2507 (Q4_K_M)
* Llama.cpp backend: httpx client via FastAPI

## B. Dataset
* Number of documents evaluated: 14

## C. Performance Metrics
- **True Positives**: 1
- **False Positives**: 6
- **False Negatives**: 10
- **Precision**: 0.14
- **Recall**: 0.09
- **F1 Score**: 0.11

## D. Raw Examples and Failure Analysis
### Source Record: SR-101
> FIR-001: Arrest of Aryan (Shadow) with handset +91-9876543210.
**Latency**: 30.73s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "aryan",
    "USES",
    "+91-9876543210"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "aryan",
    "USES",
    "+91-9876543210"
  ]
]
```
---
### Source Record: SR-102
> CDR Analysis for +91-9876543210.
**Latency**: 7.79s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "+91-9876543210",
    "COMMUNICATES_WITH",
    "+91-9999988888"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "+91-9876543210",
    "COMMUNICATES_WITH",
    "+91-9999988888"
  ]
]
```
---
### Source Record: SR-103
> Cyber surveillance narrative: Subject observed in Sector 12 Warehouse.
**Latency**: 1.95s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "subject",
    "LOCATED_AT",
    "sector 12 warehouse"
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "aryan",
    "LOCATED_AT",
    "sector 12 warehouse"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[
  [
    "subject",
    "LOCATED_AT",
    "sector 12 warehouse"
  ]
]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "aryan",
    "LOCATED_AT",
    "sector 12 warehouse"
  ]
]
```
---
### Source Record: SR-104
> Unverified tip: Aryan associated with Rajan.
**Latency**: 1.88s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "aryan",
    "ASSOCIATED_WITH",
    "rajan"
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "aryan",
    "ASSOCIATED_WITH",
    "rajan"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[]
```
---
### Source Record: SR-201
> EOW FIR regarding Ghost Shell Co.
**Latency**: 0.63s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "vikram singh",
    "OWNS",
    "ghost shell co"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "vikram singh",
    "OWNS",
    "ghost shell co"
  ]
]
```
---
### Source Record: SR-202
> Financial Transaction Report: V. Singh transferred 50L to ghost@bank.
**Latency**: 2.00s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "v. singh",
    "TRANSFERRED_TO",
    "ghost@bank"
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "vikram singh",
    "TRANSFERRED_TO",
    "ghost@bank"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[
  [
    "v. singh",
    "TRANSFERRED_TO",
    "ghost@bank"
  ]
]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "vikram singh",
    "TRANSFERRED_TO",
    "ghost@bank"
  ]
]
```
---
### Source Record: SR-203
> CDR extract for +91-9999988888.
**Latency**: 0.71s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "vikram singh",
    "USES",
    "+91-9999988888"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "vikram singh",
    "USES",
    "+91-9999988888"
  ]
]
```
---
### Source Record: SR-204
> EOW Investigation narrative: Vikram Singh suspected of hawala operations.
**Latency**: 0.65s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[]
```
---
### Source Record: SR-205
> Informant log: Vikram operates Ghost Shell Co.
**Latency**: 1.90s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "vikram",
    "OWNS",
    "ghost shell co."
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[
  [
    "vikram",
    "OWNS",
    "ghost shell co."
  ]
]
```
**False Negatives (Missed by Model)**:
```json
[]
```
---
### Source Record: SR-301
> Border checkpoint log: RJ-14-XYZ crossed at 03:00 AM.
**Latency**: 0.69s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "rj-14-xyz",
    "LOCATED_AT",
    "border post alpha"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "rj-14-xyz",
    "LOCATED_AT",
    "border post alpha"
  ]
]
```
---
### Source Record: SR-302
> RTO Record: RJ-14-XYZ registered to Rajan.
**Latency**: 2.14s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "rajan",
    "ASSOCIATED_WITH",
    "rj-14-xyz"
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "rajan",
    "OWNS",
    "rj-14-xyz"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[
  [
    "rajan",
    "ASSOCIATED_WITH",
    "rj-14-xyz"
  ]
]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "rajan",
    "OWNS",
    "rj-14-xyz"
  ]
]
```
---
### Source Record: SR-303
> Financial Intelligence: Beneficiary account ghost@bank linked to Rajan.
**Latency**: 1.98s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "beneficiary account ghost@bank",
    "LINKED_TO",
    "rajan"
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "rajan",
    "OWNS",
    "ghost@bank"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[
  [
    "beneficiary account ghost@bank",
    "LINKED_TO",
    "rajan"
  ]
]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "rajan",
    "OWNS",
    "ghost@bank"
  ]
]
```
---
### Source Record: SR-304
> Investigation memo: Logistics managed by Vikram Singh.
**Latency**: 1.83s

**Predicted (Qwen Candidates)**:
```json
[
  [
    "vikram singh",
    "OWNS",
    "logistics"
  ]
]
```
**Ground Truth (PostgreSQL)**:
```json
[
  [
    "vikram singh",
    "ASSOCIATED_WITH",
    "rajan"
  ]
]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[
  [
    "vikram singh",
    "OWNS",
    "logistics"
  ]
]
```
**False Negatives (Missed by Model)**:
```json
[
  [
    "vikram singh",
    "ASSOCIATED_WITH",
    "rajan"
  ]
]
```
---
### Source Record: SR-305
> Subject Rajan observed near border crossing.
**Latency**: 0.67s

**Predicted (Qwen Candidates)**:
```json
[]
```
**Ground Truth (PostgreSQL)**:
```json
[]
```
**False Positives (Hallucinations/Over-extractions)**:
```json
[]
```
**False Negatives (Missed by Model)**:
```json
[]
```
---