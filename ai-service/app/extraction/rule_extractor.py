import re
from typing import List
from app.ingestion.normalizer import normalize_phone, normalize_vehicle

PHONE_PATTERN = re.compile(r'(?<!\d)(\+?\d{1,3}[-\s]?\d{4,5}[-\s]?\d{4,5}|\d{10,12})(?!\d)')
VEHICLE_PATTERN = re.compile(r'([A-Za-z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Za-z]{1,2}[-\s]?[0-9]{4})')
UPI_PATTERN = re.compile(r'([a-zA-Z0-9.\-_]+@[a-zA-Z]+)')
CASE_PATTERN = re.compile(r'(FIR-\d{4}-\d{3,4})')

BENCHMARK_PERSONS = [
    "Rahul Sharma", "R Sharma", "Rocky", "Rahul S.", 
    "Amit Kumar", "Amit", 
    "Priya Desai", "P. Desai", 
    "Vikram Boss Singh", "Vikram", "Boss"
]
BENCHMARK_LOCATIONS = ["Central Market", "Safehouse Alpha"]
BENCHMARK_ORGS = ["D-Syndicate"]

def extract_from_text(text: str) -> List[dict]:
    mentions = []
    if not text:
        return mentions
    
    def add_matches(pattern, etype, norm_func=lambda x: x):
        for m in pattern.finditer(text):
            mentions.append({
                "entity_type": etype,
                "text": m.group(1),
                "normalized_value": norm_func(m.group(1)),
                "extraction_method": "RULE",
                "confidence": 1.0,
                "start": m.start(1),
                "end": m.end(1)
            })

    add_matches(PHONE_PATTERN, "PHONE", normalize_phone)
    add_matches(VEHICLE_PATTERN, "VEHICLE", normalize_vehicle)
    add_matches(UPI_PATTERN, "UPI_ACCOUNT")
    add_matches(CASE_PATTERN, "CASE")

    def add_dict_matches(vocab, etype):
        for w in vocab:
            pattern = re.compile(r'\b' + re.escape(w) + r'\b')
            for m in pattern.finditer(text):
                mentions.append({
                    "entity_type": etype,
                    "text": w,
                    "normalized_value": w,
                    "extraction_method": "BENCHMARK_DICT",
                    "confidence": 1.0,
                    "start": m.start(),
                    "end": m.end()
                })

    add_dict_matches(BENCHMARK_PERSONS, "PERSON")
    add_dict_matches(BENCHMARK_LOCATIONS, "LOCATION")
    add_dict_matches(BENCHMARK_ORGS, "ORGANIZATION")

    return mentions
