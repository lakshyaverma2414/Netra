import uuid
from typing import List
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.extraction.rule_extractor import extract_from_text
from app.ingestion.normalizer import normalize_phone, normalize_vehicle

def extract_entities_from_record(record: NormalizedRecord) -> List[EntityMention]:
    mentions = []
    
    def add_mention(etype, text, norm_val, method, start=None, end=None):
        if text:
            mentions.append(EntityMention(
                record_id=record.record_id,
                entity_type=etype,
                text=str(text),
                normalized_value=str(norm_val),
                extraction_method=method,
                confidence=1.0,
                start=start,
                end=end
            ))

    if record.content_type == "TEXT" and record.text:
        text_mentions = extract_from_text(record.text)
        for m in text_mentions:
            add_mention(m["entity_type"], m["text"], m["normalized_value"], m["extraction_method"], m["start"], m["end"])
            
    elif record.content_type == "STRUCTURED" and record.data:
        if record.source_type == "CDR":
            caller = record.data.get("caller")
            if caller:
                add_mention("PHONE", caller, normalize_phone(caller), "STRUCTURED_FIELD")
            receiver = record.data.get("receiver")
            if receiver:
                add_mention("PHONE", receiver, normalize_phone(receiver), "STRUCTURED_FIELD")
        elif record.source_type == "TRANSACTION":
            sender = record.data.get("sender_account")
            if sender:
                add_mention("UPI_ACCOUNT", sender, sender, "STRUCTURED_FIELD")
            receiver = record.data.get("receiver_account")
            if receiver:
                add_mention("UPI_ACCOUNT", receiver, receiver, "STRUCTURED_FIELD")
                
    elif record.content_type == "SEMI_STRUCTURED" and record.data:
        if record.source_type == "SURVEILLANCE":
            person = record.data.get("observed_person")
            if person:
                add_mention("PERSON", person, person, "STRUCTURED_FIELD")
            vehicle = record.data.get("vehicle_number")
            if vehicle:
                add_mention("VEHICLE", vehicle, normalize_vehicle(vehicle), "STRUCTURED_FIELD")
            location = record.data.get("location")
            if location:
                add_mention("LOCATION", location, location, "STRUCTURED_FIELD")
            notes = record.data.get("notes")
            if notes:
                text_mentions = extract_from_text(notes)
                for m in text_mentions:
                    add_mention(m["entity_type"], m["text"], m["normalized_value"], m["extraction_method"], m["start"], m["end"])
    
    return mentions
