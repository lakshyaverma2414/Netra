# Ontology Design Decisions

## 1. Event-Centric over Binary Relations for Complex Interactions
*Decision*: `PERSON -> COMMUNICATES_WITH -> PERSON` is insufficient.
*Justification*: Communications have timestamps, durations, and channels. Binary relations in Apache AGE only have edge properties, which makes querying "who communicated via WhatsApp on Tuesday" highly inefficient if modeled purely as edge properties on a single static `COMMUNICATES_WITH` edge. Using an `Event` node (e.g., `CommunicationEvent`) linked to both Persons allows robust temporal indexing and n-ary participation.

## 2. Strong Provenance Requirement
*Decision*: Every Canonical Edge must map back to an `Assertion`, which maps to an `Observation`, which maps to a `SourceRecord`.
*Justification*: In criminal investigations, facts are challenged in court. A KG without trace-back is an intelligence toy, not an investigative tool. 

## 3. Ambiguity Tolerance
*Decision*: Allow `Entity -> ALIAS_OF -> Entity` and delayed resolution.
*Justification*: We often don't know if "John Doe" in Case A is "John Doe" in Case B. The ontology must allow them to exist as separate Canonical Entities until evidence justifies an `SAME_AS` edge, which the Graph DB can traverse seamlessly.
