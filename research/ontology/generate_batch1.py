import os
import csv

BASE_DIR = "/mnt/d/NETRA/SIH2026/research/ontology"
os.makedirs(BASE_DIR, exist_ok=True)

def write_md(name, content):
    with open(os.path.join(BASE_DIR, name), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. 01_ontology_landscape.md
write_md("01_ontology_landscape.md", """
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
""")

# 2. 02_existing_ontology_comparison.csv
csv_path = os.path.join(BASE_DIR, "02_existing_ontology_comparison.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Framework", "Scope", "Entities", "Events", "Actions", "Relationships", "Evidence", "Provenance",
        "Temporal Model", "Uncertainty", "Cyber", "Physical Crime", "Financial", "Case Management", 
        "Extensibility", "OWL/RDF", "JSON/API friendliness", "Reuse potential", "Limitations"
    ])
    writer.writerow([
        "CASE/UCO", "Cyber Investigations / Digital Forensics", "Extensive (Cyber objects, identities)", "Basic", "Forensic Actions", "Yes (Core layer)", "Strong (Trace, Artifact)", "Strong (Chain of Custody)",
        "Timestamps, Time Ranges", "Basic (Confidence)", "High", "Low", "Medium", "Basic",
        "High", "Yes", "High (JSON-LD)", "High (For digital artifacts)", "Too granular for high-level link analysis; verbose JSON-LD."
    ])
    writer.writerow([
        "STIX 2.1", "Cyber Threat Intelligence", "Threat Actors, Infrastructure, Malware", "Campaigns, Incidents", "Attack Patterns", "SROs (Relationship Objects)", "Sightings, Observables", "Moderate (Sighting context)",
        "Timestamps (Valid_from/to)", "Confidence Scores", "Very High", "Very Low", "Low", "Low",
        "High", "No (JSON)", "Very High", "Medium (Adopt Threat Actor patterns)", "Lacks physical crime concepts; focuses on network defense."
    ])
    writer.writerow([
        "Project COSMOS", "Cybercrime Ecosystems", "Role Players, Platforms, Markets, Victims", "Events, Phases", "Techniques", "Hierarchical/Semantic", "Mapped", "Mapped",
        "Intervals", "Semantic definitions", "High", "Medium", "High", "Low",
        "Very High", "Yes", "Medium", "Very High (For conceptual design/governance)", "It is a framework/governance model, not an out-of-the-box DB schema."
    ])
    writer.writerow([
        "CSI Ontology (Onnoom)", "Crime Scene Recommendation", "Weapons, Bloodstains, Suspects", "Crime Events", "Investigation Tasks", "Specific to CSI", "Physical Evidence", "Basic",
        "Point events", "None", "Low", "High", "Low", "Basic",
        "Low", "Yes", "Low", "Low", "Too theoretical, brittle rules, lacks digital forensics."
    ])

# 3. 03_netra_domain_concept_model.md
write_md("03_netra_domain_concept_model.md", """
# NETRA Domain Concept Model

## Core Principle
ONTOLOGY ≠ TRUTH. The ontology defines the semantic possibilities of the investigative domain.

## Abstract Layers
1.  **ENTITY**: A distinct, independently existing object or actor (e.g., Person, Vehicle, Bank Account).
2.  **EVENT / ACTION**: A bounded occurrence in time involving Entities (e.g., Communication, Transaction, Arrest). 
    *   *Why use Events?* A transaction is not merely `AccountA -> TRANSFERRED_TO -> AccountB`. It has an amount, a timestamp, a bank branch, and a currency. Events capture n-ary relationships perfectly.
3.  **RELATIONSHIP (Binary)**: A stateful, non-event linkage (e.g., `OWNS`, `SIBLING_OF`, `AFFILIATED_WITH`).
4.  **EVIDENCE / OBSERVATION**: The raw data artifact (FIR text, CDR log) and the extracted claim. This layer binds the theoretical KG to the real world.
5.  **CONTEXT / CASE**: The investigative container. Entities may exist globally, but they participate in Case Contexts.

## Separation of Concerns
*   **The World**: Entities, Events, Relationships.
*   **The Investigation**: Evidence, Observations, Provenance, Cases.
""")

# 4. 04_entity_taxonomy_proposal.yaml
write_md("04_entity_taxonomy_proposal.yaml", """
Entity:
  Actor:
    Person:
      description: "A human being, known or unknown."
    Organization:
      description: "A formal entity (company, agency)."
    Group:
      description: "An informal collective (syndicate, gang)."
  DigitalObject:
    Account:
      description: "A logical account (Bank, Crypto, Social Media)."
    Identifier:
      description: "A digital routing point (Email, Phone Number, IP, MAC)."
    Device:
      description: "A physical computing device (Mobile, Laptop)."
  PhysicalObject:
    Vehicle:
      description: "A mode of transport."
    Weapon:
      description: "An instrument used in an event."
    Asset:
      description: "Property, real estate, valuables."
  Location:
    PhysicalLocation:
      description: "Geo-coordinate, Address, Region."
    DigitalLocation:
      description: "URL, Domain, Darkweb forum."
""")

# 5. 05_event_action_taxonomy_proposal.yaml
write_md("05_event_action_taxonomy_proposal.yaml", """
Event:
  CommunicationEvent:
    description: "Exchange of information between identifiers."
    attributes: [timestamp, duration, channel, direction]
    participants: [sender, receiver, infrastructure]
  FinancialTransaction:
    description: "Movement of value."
    attributes: [timestamp, amount, currency, status]
    participants: [source_account, destination_account, facilitating_org]
  PhysicalMovement:
    description: "Actor or Object moving between locations."
    attributes: [start_time, end_time, method]
    participants: [actor, object, origin, destination]
  CyberAction:
    description: "An interaction with digital infrastructure (login, access, exploit)."
    attributes: [timestamp, action_type, outcome]
    participants: [actor, source_ip, target_device, target_account]
  CriminalIncident:
    description: "The core crime event (murder, theft, fraud)."
    attributes: [timestamp, crime_type, status]
    participants: [perpetrator, victim, weapon, location]
""")

# 6. 06_relationship_taxonomy_proposal.yaml
write_md("06_relationship_taxonomy_proposal.yaml", """
Relationship:
  Identity:
    SAME_AS:
      domain: Entity
      range: Entity
      properties: [symmetric, transitive]
    ALIAS_OF:
      domain: Actor
      range: Actor
  Association:
    AFFILIATED_WITH:
      domain: Actor
      range: [Actor, Organization, Group]
    KNOWS:
      domain: Person
      range: Person
      properties: [symmetric]
  OwnershipControl:
    OWNS:
      domain: [Person, Organization]
      range: [Vehicle, Asset, DigitalObject, Organization]
    CONTROLS:
      domain: [Person, Organization]
      range: [Account, Device, Organization]
  Spatial:
    LOCATED_AT:
      domain: [Person, PhysicalObject, Event]
      range: PhysicalLocation
  Temporal:
    PRECEDES:
      domain: Event
      range: Event
      properties: [transitive]
""")

print("Batch 1 completed.")
