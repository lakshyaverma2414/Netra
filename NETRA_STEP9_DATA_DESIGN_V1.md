# NETRA_STEP9_DATA_DESIGN_V1

## Overview
This document outlines the three realistic, synthetic cases that power the NETRA prototype. They are designed to demonstrate fragmented ingestion, entity resolution, case isolation, and a deep cross-case network.

---

## CASE 1: Operation Black Web (C-001)
**What happened?**
A cyber intelligence unit intercepted dark web narcotics trafficking communications. Initial arrests yielded burner phones and online aliases, but the leadership remains unknown.

**Initial known entities:**
- `P-001`: Aryan (Alias: "Shadow")
- `PH-001`: Burner Phone (+91-9876543210)
- `LOC-001`: Abandoned Warehouse, Sector 12

**Initial evidence:**
- FIR: Arrest of Aryan.
- Cyber Surveillance: Intercept logs of `PH-001`.

**Cross-case Lead:**
`PH-001` has regular communications with an unknown number `PH-002`, which connects to a money-laundering syndicate in Case 2.

---

## CASE 2: Syndicate Ghost (C-002)
**What happened?**
Economic Offenses Wing (EOW) is investigating a massive hawala and money laundering network operating through shell companies and bulk UPI transfers.

**Initial known entities:**
- `P-002`: Vikram Singh (Financier)
- `PH-002`: Vikram's primary contact number (+91-9999988888)
- `UPI-001`: Suspicious UPI Account (ghost@bank)

**Initial evidence:**
- Financial Transaction Report (FTR): Bulk transfers tracking.
- EOW Investigation Narrative.

**Cross-case Lead:**
Vikram (`P-002`) operates `PH-002` (linking back to Case 1) and transfers funds to `UPI-001` (linking forward to Case 3).

---

## CASE 3: Border Route (C-003)
**What happened?**
Border Security intelligence identified a recurring smuggling route using civilian transport vehicles. Drivers were arrested, but the financial backing and cargo origins are under investigation.

**Initial known entities:**
- `P-002`: Vikram Singh (Logistics manager front)
- `P-003`: Rajan (Fleet Operator)
- `VEH-001`: Truck Registration (RJ-14-XYZ)
- `UPI-001`: Beneficiary Account (ghost@bank)

**Initial evidence:**
- Border Checkpoint Logs.
- Financial Intelligence Report.

**Cross-case Lead:**
Rajan (`P-003`) owns both `VEH-001` and `UPI-001`, explicitly tying the border logistics to the hawala network.

---

## The Cross-Case Network & Shared Entities
**Shared Canonical Entities:**
- `P-002` (Vikram Singh) is shared across `C-002` and `C-003`.
- `UPI-001` is shared across `C-002` and `C-003`.

**Bridges:**
- **Communication bridge (C-001 → C-002):** `P-001 → PH-001 → PH-002 → P-002`
- **Financial bridge (C-002 → C-003):** `P-002 → UPI-001 → P-003`
