# The Ontology Landscape for Investigative Platforms

## Overview
Traditional crime databases use relational schemas that struggle with heterogeneous data (devices, crypto, locations, aliases). The Semantic Web offered RDF/OWL, but these were often too abstract or academic (e.g., Onnoom's Crime Scene Investigation Ontology) to handle the messy reality of digital forensics and provenance.

## The Shift to Forensic and Threat Ontologies
Modern frameworks recognize that investigation requires representing the *process* of discovery as much as the *entities* discovered.
*   **CASE/UCO**: Standardized digital forensics. They model cyber-objects, chains of custody, and extraction processes.
*   **STIX 2.1 / OCAI**: Threat intelligence. Originally focused on IOCs, now extending into campaign attribution and investigation.
*   **Project COSMOS**: High-level, abstract modelling of cybercrime ecosystems. Separates the conceptual framework (Ontology) from concrete data (Graph).

## The Gap
Most existing models either over-index on cyber (STIX), over-index on bits-and-bytes forensic extraction (CASE), or over-index on theoretical mapping (OWL). NETRA needs a pragmatic, generic investigative ontology that bridges physical crime (locations, vehicles), cyber crime (crypto, IP addresses), and provenance (how do we know this fact?).
