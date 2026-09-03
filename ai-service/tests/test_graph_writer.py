import pytest
from app.graph.graph_writer import MockGraphWriter as GraphWriter
from app.schemas.validation import RelationshipValidationResult, ValidationStatus
from datetime import datetime

def test_graph_writer_only_commits_confirmed():
    writer = GraphWriter()
    writer.connect()
    
    res1 = RelationshipValidationResult(
        relationship_id="rel1",
        status=ValidationStatus.CONFIRMED,
        source_entity_id="E1",
        relationship_type="USES",
        target_entity_id="E2",
        validated_at=datetime.utcnow()
    )
    
    res2 = RelationshipValidationResult(
        relationship_id="rel2",
        status=ValidationStatus.REJECTED,
        source_entity_id="E3",
        relationship_type="OWNS",
        target_entity_id="E4",
        reasons=["INVALID_ONTOLOGY"],
        validated_at=datetime.utcnow()
    )
    
    res3 = RelationshipValidationResult(
        relationship_id="rel3",
        status=ValidationStatus.NEEDS_REVIEW,
        source_entity_id="E5",
        relationship_type="COMMUNICATES_WITH",
        target_entity_id="E6",
        reasons=["CONTRADICTION"],
        validated_at=datetime.utcnow()
    )
    
    written_count = writer.write_relationships([res1, res2, res3])
    assert written_count == 1  # Only the CONFIRMED one should be written!

def test_graph_writer_requires_connection():
    writer = GraphWriter()
    with pytest.raises(RuntimeError):
        writer.write_relationships([])
