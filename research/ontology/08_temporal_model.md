# Temporal Model

## Investigative Time is Not One-Dimensional
NETRA must model different temporal semantics:
*   **occurred_at**: When the real-world event happened (e.g., the murder). Often an interval (`start_time`, `end_time`) or bounded (`before_date`, `after_date`).
*   **observed_at**: When a sensor or witness recorded it (e.g., CDR log timestamp).
*   **reported_at**: When it entered the official system (e.g., FIR filing date).
*   **valid_from / valid_to**: For relationships (e.g., Person A owned Vehicle B from 2020 to 2024).

## Dealing with Uncertainty
Temporal representation must allow partial dates ("May 2023"), ranges ("Between Monday and Wednesday"), and contradictions (Witness A says 10:00, Witness B says 11:00). Events should use Allen's Interval Algebra semantics rather than strict UNIX timestamps.
