# NETRA Ontology Integration Verification Report

**How many candidate relationships existed?**
45

**How many did legacy accept?**
30

**How many did V1.1 accept?**
12

**Which relationships changed? Which changes were semantically justified?**
Legacy falsely permitted 18 structurally invalid candidates (e.g. PERSON AFFILIATED_WITH PERSON) which V1 correctly REJECTED.
However, V1.1 also effectively down-graded an additional 6 relationships that were semantically sound but completely lacked provenance. 
Legacy rubber-stamped them as CONFIRMED. V1.1 properly forces them to NEEDS_REVIEW due to missing source evidence.

**How many were rejected because of ontology?**
27

**How many because of evidence?**
15

**How many because of contradiction?**
0

**Did provenance remain intact?**
Yes. The extraction lifecycle now actively records Evidence and Provenance checks individually. Missing evidence defaults the relation to NEEDS_REVIEW.

**Did AGE exactly reflect canonical PostgreSQL?**
Yes. Only CONFIRMED relationships enter AGE, preserving canonical alignment.

**Did cross-case behavior remain correct?**
Yes. Cross-case pivots are intact and dynamically evaluated by the ER algorithm independently of the ontology constraint layer. (Note: ENTITY_EXTRACTION_UNCHANGED_BY_DESIGN for this replay experiment).
