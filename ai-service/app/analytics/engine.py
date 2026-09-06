
import os
import yaml
from sqlalchemy.orm import Session
from sqlalchemy import text

class PatternEngine:
    def __init__(self, db: Session, patterns_dir: str):
        self.db = db
        self.patterns = {}
        self._load_patterns(patterns_dir)
        
    def _load_patterns(self, patterns_dir: str):
        for f in os.listdir(patterns_dir):
            if f.endswith(".yaml"):
                with open(os.path.join(patterns_dir, f), "r") as yaml_file:
                    doc = yaml.safe_load(yaml_file)
                    if "pattern" in doc:
                        self.patterns[doc["pattern"]["id"]] = doc["pattern"]
                        
    def run_pattern(self, pattern_id: str, overrides: dict = None):
        if pattern_id not in self.patterns:
            raise ValueError(f"Pattern {pattern_id} not found.")
            
        pattern = self.patterns[pattern_id]
        params = pattern.get("parameters", {}).copy()
        if overrides:
            params.update(overrides)
            
        query = text(pattern["query_template"])
        results = self.db.execute(query, params).fetchall()
        
        return [dict(row._mapping) for row in results]
