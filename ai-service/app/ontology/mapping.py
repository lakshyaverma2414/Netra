ENTITY_TYPE_MAPPING = {
    "PERSON": "netra:Person",
    "PHONE": "netra:Identifier",
    "IMEI": "netra:Identifier",
    "VEHICLE": "netra:Vehicle",
    "LOCATION": "netra:Location",
    "ORGANIZATION": "netra:Organization",
    "EVENT": "netra:Event",
    "BANK_ACCOUNT": "netra:Account",
    "UPI_ID": "netra:Account",
    "SOCIAL_ACCOUNT": "netra:Account",
    "CASE": "netra:Event"  # Map CASE to Event for V1 compatibility
}

RELATIONSHIP_TO_EVENT_MAPPING = {
    "TRANSFERRED_TO": {
        "event": "netra:FinancialTransaction",
        "source_role": "originator",
        "target_role": "beneficiary"
    },
    "LOST_ASSETS_TO": {
        "event": "netra:FinancialTransaction",
        "source_role": "originator",
        "target_role": "beneficiary"
    },
    "CONSPIRED_WITH": {
        "event": "netra:CriminalIncident",
        "source_role": "perpetrator",
        "target_role": "perpetrator"
    },
    "ARRESTED_WITH": {
        "event": "netra:CriminalIncident",
        "source_role": "perpetrator",
        "target_role": "perpetrator"
    },
    "KILLED_IN": {
        "event": "netra:CriminalIncident",
        "source_role": "victim",
        "target_role": "location"
    },
    "HAS_VICTIMS": {
        "event": "netra:CriminalIncident",
        "source_role": "perpetrator",
        "target_role": "victim"
    },
    "INCLUDES": {
        "event": "netra:CriminalIncident",
        "source_role": "perpetrator",
        "target_role": "victim"
    },
    "ARRESTED_IN": {
        "event": "netra:CriminalIncident",
        "source_role": "perpetrator",
        "target_role": "location"
    }
}

DIRECT_REL_MAPPING = {
    # Core identifiers
    "USES":                               "netra:USES",
    "USED_BY":                            "netra:USED_BY",
    "OWNS":                               "netra:OWNS",
    "OWNED_BY":                           "netra:OWNED_BY",
    "REGISTERED_TO":                      "netra:REGISTERED_TO",
    # Communication and generic Person-Person Association
    "COMMUNICATES_WITH":                  "netra:COMMUNICATES_WITH",
    "BROTHER_OF":                         "netra:COMMUNICATES_WITH",
    "FAMILY_OF":                          "netra:COMMUNICATES_WITH",
    # Location / Containment
    "LOCATED_AT":                         "netra:LOCATED_AT",
    # Association / Affiliation (Actor -> Org/Group)
    "ASSOCIATED_WITH":                    "netra:AFFILIATED_WITH",
    "AFFILIATED_WITH":                    "netra:AFFILIATED_WITH",
    "KNOWN_ASSOCIATE_OF":                 "netra:AFFILIATED_WITH",
    "EMPLOYED_BY":                        "netra:EMPLOYED_BY",
    "OPERATES_AS":                        "netra:AFFILIATED_WITH",
    "RE_REGISTERED_AS":                   "netra:AFFILIATED_WITH",
    "RE-REGISTERED_AS":                   "netra:AFFILIATED_WITH",
    "OFFERS":                             "netra:AFFILIATED_WITH",
    # Criminal / Legal participation (Actor -> Event)
    "INVOLVED_IN":                        "netra:PARTICIPATED_IN",
    "PARTICIPATED_IN":                    "netra:PARTICIPATED_IN",
    "ACCUSED_IN":                         "netra:PARTICIPATED_IN",
    "ARRESTED_FOR":                       "netra:PARTICIPATED_IN",
    "INVOLVED_IN_LEGAL_PROCEEDING_WITH":  "netra:PARTICIPATED_IN",
    "INVESTIGATED":                       "netra:PARTICIPATED_IN",
    "INITIATED_INVESTIGATION":            "netra:PARTICIPATED_IN",
    "CONDUCTS_INVESTIGATION":             "netra:PARTICIPATED_IN",
    "CONDUCTS_INVESTIGATION_FOR":         "netra:PARTICIPATED_IN",
    "RESPONDED_TO":                       "netra:PARTICIPATED_IN",
    "ISSUED_REGULATORY_NOTIFICATION_TO":  "netra:PARTICIPATED_IN",
    "CORROBORATED_BY":                    "netra:PARTICIPATED_IN",
    "EVIDENCE_OF":                        "netra:PARTICIPATED_IN",
    # Identity
    "SAME_AS":                            "netra:SAME_AS",
    "ALIAS_OF":                           "netra:ALIAS_OF",
}