# Synthetic Ground-Truth Dataset

This dataset represents a synthetic, controlled environment for evaluating the extraction, resolution, and relationship-building components of the AI service.

**ALL IDENTITIES AND RECORDS ARE COMPLETELY SYNTHETIC AND DO NOT REPRESENT REAL PERSONS OR EVENTS.**

## Structure

*   ground_truth/: Contains the canonical expected output.
    *   entities.json: The fully resolved, authoritative list of entities (persons, phones, locations, etc.).
    *   elationships.json: The authoritative graph of relationships connecting the entities.
*   sources/: Contains fragmented, unstructured, and semi-structured input observations that collectively form the ground truth.
    *   ir_001.json, ir_002.json: Simulated First Information Reports.
    *   cdr_001.csv: Simulated Call Detail Records.
    *   	ransactions_001.csv: Simulated financial transactions.
    *   surveillance_001.json: Simulated field surveillance reports.

## Design Patterns

This dataset intentionally includes:
1.  **Alias Variation:** Entities like "Rahul Sharma" appear as "R Sharma" or "Rocky" in sources to test Entity Resolution.
2.  **Fragmented Identifiers:** Phone numbers appear with and without country codes. Vehicle numbers appear with and without spaces.
3.  **Hidden Multi-hop Path:** A direct relationship between certain entities does not exist. They can only be linked via multi-hop graph traversal (e.g., P001 -> PHONE001 -> PHONE002 -> P002 -> UPI001 -> UPI002 -> P003 -> VEHICLE001 -> CASE002).
4.  **Investigative Leads:** Patterns such as communication bursts and shared assets are included to test Network Analytics, without explicitly labeling entities as "guilty".

## Usage

This dataset is used by unit and integration tests to verify that the extraction pipelines and Splink resolution models correctly reconstruct the ground_truth graph from the sources inputs.
