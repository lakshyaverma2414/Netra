import os

with open("/mnt/d/NETRA/SIH2026/ai-service/app/services/validation_service.py", "r") as f:
    code = f.read()

# Replace the part where it creates `Relationship` for events.
old_block = """
        if not existing_rel:
            new_rel = Relationship(
                relationship_id=rel_id,
                source_entity_id=request.source_entity_id,
                target_entity_id=request.target_entity_id,
                relationship_type=request.relationship_type,
                status=DBValStatus.CONFIRMED,
                confidence=1.0
            )
            db.add(new_rel)
            
        existing_case_link = db.query(RelationshipCase).filter_by(relationship_id=rel_id, case_id=request.case_id).first()
        if not existing_case_link:
            db.add(RelationshipCase(relationship_id=rel_id, case_id=request.case_id))
            
        db.add(RelationshipAssertionLink(relationship_id=rel_id, assertion_id=assertion.assertion_id))
        db.commit()
"""

new_block = """
        from app.db.models import Event, EventEntity
        
        # Check if it's an event
        if v1_enabled and request.relationship_type in RELATIONSHIP_TO_EVENT_MAPPING:
            ev_map = RELATIONSHIP_TO_EVENT_MAPPING[request.relationship_type]
            event_type = ev_map['event']
            
            if not existing_rel:
                # We project it as an event, but to maintain backwards compat we also insert the canonical relation edge
                # However, the generic pattern engine will query the EVENT tables.
                event_id = f"EV-{uuid.uuid4().hex[:8]}"
                new_event = Event(
                    event_id=event_id,
                    case_id=request.case_id,
                    event_type=event_type,
                    description=request.extracted_text
                )
                db.add(new_event)
                
                db.add(EventEntity(event_id=event_id, entity_id=request.source_entity_id, role=ev_map['source_role']))
                db.add(EventEntity(event_id=event_id, entity_id=request.target_entity_id, role=ev_map['target_role']))
                
                new_rel = Relationship(
                    relationship_id=rel_id,
                    source_entity_id=request.source_entity_id,
                    target_entity_id=request.target_entity_id,
                    relationship_type=request.relationship_type,
                    status=DBValStatus.CONFIRMED,
                    confidence=1.0
                )
                db.add(new_rel)
                
        else:
            if not existing_rel:
                new_rel = Relationship(
                    relationship_id=rel_id,
                    source_entity_id=request.source_entity_id,
                    target_entity_id=request.target_entity_id,
                    relationship_type=request.relationship_type,
                    status=DBValStatus.CONFIRMED,
                    confidence=1.0
                )
                db.add(new_rel)
                
        existing_case_link = db.query(RelationshipCase).filter_by(relationship_id=rel_id, case_id=request.case_id).first()
        if not existing_case_link:
            db.add(RelationshipCase(relationship_id=rel_id, case_id=request.case_id))
            
        db.add(RelationshipAssertionLink(relationship_id=rel_id, assertion_id=assertion.assertion_id))
        db.commit()
"""

code = code.replace(old_block, new_block)

with open("/mnt/d/NETRA/SIH2026/ai-service/app/services/validation_service.py", "w") as f:
    f.write(code)
