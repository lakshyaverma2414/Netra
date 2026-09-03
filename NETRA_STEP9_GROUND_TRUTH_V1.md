# NETRA_STEP9_GROUND_TRUTH_V1

This document serves as the evaluation oracle for the SIH 26189 demo.

## CASE-001
**Known entities:**
- `P-001` (Aryan)
- `PH-001` (+91-9876543210)
- `LOC-001` (Sector 12 Warehouse)
- `PH-002` (+91-9999988888)

**Known relationships:**
- `P-001` --USES--> `PH-001`
- `P-001` --LOCATED_AT--> `LOC-001`
- `PH-001` --COMMUNICATES_WITH--> `PH-002`

**Cross-case leads:**
- Who owns `PH-002`?

**Evidence:**
- FIR-001, Cyber Surveillance Log (Doc 1)

---

## CASE-002
**Known entities:**
- `P-002` (Vikram Singh)
- `PH-002` (+91-9999988888)
- `UPI-001` (ghost@bank)
- `ORG-001` (Ghost Shell Co)

**Known relationships:**
- `P-002` --USES--> `PH-002`
- `P-002` --TRANSFERRED_TO--> `UPI-001`
- `P-002` --OWNS--> `ORG-001`

**Cross-case leads:**
- `PH-002` bridges to C-001.
- `UPI-001` bridges to C-003.

**Evidence:**
- EOW Investigation Narrative (Doc 2), Financial Transaction Report

---

## CASE-003
**Known entities:**
- `P-002` (Vikram Singh)
- `P-003` (Rajan)
- `VEH-001` (RJ-14-XYZ)
- `UPI-001` (ghost@bank)

**Known relationships:**
- `P-002` --ASSOCIATED_WITH--> `P-003`
- `P-003` --OWNS--> `VEH-001`
- `P-003` --OWNS--> `UPI-001`

**Cross-case leads:**
- `P-002` and `UPI-001` trace back to C-002.

**Evidence:**
- Border Checkpoint Narrative (Doc 3), Financial Intelligence Report

---

## COMMUNICATION BRIDGE
C-001 → C-002
`P-001` → `PH-001` → `PH-002` → `P-002`

## FINANCIAL BRIDGE
C-002 → C-003
`P-002` → `UPI-001` → `P-003`

## OPERATIONAL BRIDGE
C-003
`P-003` → `VEH-001`

## NEGATIVE RELATIONSHIP
**NEEDS_REVIEW:**
`P-001` --ASSOCIATED_WITH--> `P-003` (Not in AGE graph)
