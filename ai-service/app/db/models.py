from sqlalchemy import Column, String, Text, Boolean, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.db.database import Base

class CaseStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    CLOSED = 'CLOSED'
    COLD = 'COLD'
    PENDING = 'PENDING'

class ResolutionStatus(str, enum.Enum):
    CONFIRMED = 'CONFIRMED'
    PROBABLE = 'PROBABLE'
    CANDIDATE = 'CANDIDATE'
    REJECTED = 'REJECTED'
    UNRESOLVED = 'UNRESOLVED'

class EntityType(str, enum.Enum):
    PERSON = 'PERSON'
    PHONE = 'PHONE'
    IMEI = 'IMEI'
    VEHICLE = 'VEHICLE'
    LOCATION = 'LOCATION'
    ORGANIZATION = 'ORGANIZATION'
    EVENT = 'EVENT'
    BANK_ACCOUNT = 'BANK_ACCOUNT'
    UPI_ID = 'UPI_ID'
    SOCIAL_ACCOUNT = 'SOCIAL_ACCOUNT'
    CASE = 'CASE'

class ValidationStatus(str, enum.Enum):
    CONFIRMED = 'CONFIRMED'
    NEEDS_REVIEW = 'NEEDS_REVIEW'
    REJECTED = 'REJECTED'

# IDENTITY DOMAIN
class User(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default='ACTIVE')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserPermission(Base):
    __tablename__ = 'user_permissions'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), primary_key=True)
    permissions = Column(JSONB, nullable=False, default={})

class AuditLog(Base):
    __tablename__ = 'audit_log'
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255))
    case_id = Column(String(50), ForeignKey('cases.case_id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column('metadata', JSONB)

# INVESTIGATION DOMAIN
class Case(Base):
    __tablename__ = 'cases'
    case_id = Column(String(50), primary_key=True)
    case_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    jurisdiction = Column(String(100))
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.ACTIVE)
    priority = Column(String(50))
    opened_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CaseLink(Base):
    __tablename__ = 'case_links'
    source_case_id = Column(String(50), ForeignKey('cases.case_id'), primary_key=True)
    target_case_id = Column(String(50), ForeignKey('cases.case_id'), primary_key=True)
    link_reason = Column(Text, nullable=False)

# INGESTION DOMAIN
class IngestionBatch(Base):
    __tablename__ = 'ingestion_batches'
    batch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(50), ForeignKey('cases.case_id'))
    submitted_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_hash = Column(String(64), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    error_details = Column(Text)

class DataSource(Base):
    __tablename__ = 'data_sources'
    source_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(100), unique=True, nullable=False)

class SourceRecord(Base):
    __tablename__ = 'source_records'
    record_id = Column(String(100), primary_key=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey('ingestion_batches.batch_id'))
    case_id = Column(String(50), ForeignKey('cases.case_id'))
    source_type = Column(String(50), nullable=False)
    external_record_id = Column(String(255))
    record_timestamp = Column(DateTime(timezone=True))
    raw_payload = Column(JSONB, nullable=False)
    normalized_payload = Column(JSONB)
    source_hash = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = 'documents'
    document_id = Column(String(100), primary_key=True)
    case_id = Column(String(50), ForeignKey('cases.case_id'))
    batch_id = Column(UUID(as_uuid=True), ForeignKey('ingestion_batches.batch_id'))
    source_record_id = Column(String(100), ForeignKey('source_records.record_id'))
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100))
    storage_uri = Column(String(500), nullable=False)
    document_hash = Column(String(64), unique=True, nullable=False)
    page_count = Column(Integer)
    ocr_status = Column(String(50))
    ocr_confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String(100), ForeignKey('documents.document_id'))
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer)
    text = Column(Text, nullable=False)
    char_start = Column(Integer)
    char_end = Column(Integer)
    embedding_model = Column(String(100))
    embedding_created_at = Column(DateTime(timezone=True))

class ProcessingRun(Base):
    __tablename__ = 'processing_runs'
    run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_name = Column(String(100), nullable=False)
    pipeline_version = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=False)
    input_batch_id = Column(UUID(as_uuid=True), ForeignKey('ingestion_batches.batch_id'))
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    configuration = Column(JSONB)

# ENTITY DOMAIN
class Entity(Base):
    __tablename__ = 'entities'
    entity_id = Column(String(100), primary_key=True)
    entity_type = Column(Enum(EntityType), nullable=False)
    canonical_name = Column(String(255), nullable=False)
    normalized_value = Column(String(255), nullable=False)
    resolution_status = Column(Enum(ResolutionStatus), nullable=False, default=ResolutionStatus.UNRESOLVED)
    resolution_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    cases = relationship("CaseEntity", back_populates="entity")

class EntityMention(Base):
    __tablename__ = 'entity_mentions'
    mention_id = Column(String(100), primary_key=True)
    entity_type = Column(Enum(EntityType), nullable=False)
    extracted_text = Column(Text, nullable=False)
    normalized_value = Column(String(255), nullable=False)
    extraction_method = Column(String(50), nullable=False)
    extraction_confidence = Column(Float)
    source_record_id = Column(String(100), ForeignKey('source_records.record_id'))
    document_chunk_id = Column(UUID(as_uuid=True), ForeignKey('document_chunks.chunk_id'))
    start_offset = Column(Integer)
    end_offset = Column(Integer)
    extraction_run_id = Column(UUID(as_uuid=True), ForeignKey('processing_runs.run_id'))
    resolved_entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EntityAlias(Base):
    __tablename__ = 'entity_aliases'
    alias_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    alias = Column(String(255), nullable=False)
    normalized_alias = Column(String(255), nullable=False)
    source = Column(String(255))
    confidence = Column(Float)
    provenance = Column(JSONB)

class EntityResolutionLog(Base):
    __tablename__ = 'entity_resolution_log'
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mention_id = Column(String(100), ForeignKey('entity_mentions.mention_id'))
    candidate_entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    decision = Column(Enum(ResolutionStatus), nullable=False)
    probability = Column(Float)
    matching_features = Column(JSONB)
    resolver_version = Column(String(50))
    model_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CaseEntity(Base):
    __tablename__ = 'case_entities'
    case_id = Column(String(50), ForeignKey('cases.case_id'), primary_key=True)
    entity_id = Column(String(100), ForeignKey('entities.entity_id'), primary_key=True)
    association_type = Column(String(100))
    confidence = Column(Float)
    source = Column(String(255))
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    entity = relationship("Entity", back_populates="cases")

# RELATIONSHIP DOMAIN
class Relationship(Base):
    __tablename__ = 'relationships'
    relationship_id = Column(String(100), primary_key=True)
    source_entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    relationship_type = Column(String(100), nullable=False)
    target_entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    status = Column(Enum(ValidationStatus), nullable=False, default=ValidationStatus.NEEDS_REVIEW)
    confidence = Column(Float)
    first_observed_at = Column(DateTime(timezone=True))
    last_observed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RelationshipAssertion(Base):
    __tablename__ = 'relationship_assertions'
    assertion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    target_entity_id = Column(String(100), ForeignKey('entities.entity_id'))
    relationship_type = Column(String(100), nullable=False)
    source_record_id = Column(String(100), ForeignKey('source_records.record_id'))
    document_chunk_id = Column(UUID(as_uuid=True), ForeignKey('document_chunks.chunk_id'))
    evidence_text = Column(Text)
    extraction_method = Column(String(50))
    extraction_confidence = Column(Float)
    negated = Column(Boolean, default=False)
    temporal_context = Column(JSONB)
    location_context = Column(JSONB)
    extraction_run_id = Column(UUID(as_uuid=True), ForeignKey('processing_runs.run_id'))
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RelationshipAssertionLink(Base):
    __tablename__ = 'relationship_assertion_links'
    relationship_id = Column(String(100), ForeignKey('relationships.relationship_id'), primary_key=True)
    assertion_id = Column(UUID(as_uuid=True), ForeignKey('relationship_assertions.assertion_id'), primary_key=True)

class RelationshipCase(Base):
    __tablename__ = 'relationship_cases'
    relationship_id = Column(String(100), ForeignKey('relationships.relationship_id'), primary_key=True)
    case_id = Column(String(50), ForeignKey('cases.case_id'), primary_key=True)

# FINDINGS DOMAIN
class Finding(Base):
    __tablename__ = 'findings'
    finding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(50), ForeignKey('cases.case_id'))
    finding_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(50))
    confidence = Column(Float)
    status = Column(String(50), nullable=False, default='NEW')
    generated_by = Column(String(100))
    algorithm_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# EVIDENCE DOMAIN
class Evidence(Base):
    __tablename__ = 'evidence'
    evidence_id = Column(String(100), primary_key=True)
    case_id = Column(String(50), ForeignKey('cases.case_id'))
    evidence_type = Column(String(100), nullable=False)
    title = Column(String(255))
    storage_uri = Column(String(500), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    hash_algorithm = Column(String(50), default='SHA-256')
    source = Column(String(255))
    collected_at = Column(DateTime(timezone=True))
    collected_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    sealed = Column(Boolean, default=False)
    fabric_transaction_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EvidenceCase(Base):
    __tablename__ = 'evidence_cases'
    evidence_id = Column(String(100), ForeignKey('evidence.evidence_id'), primary_key=True)
    case_id = Column(String(50), ForeignKey('cases.case_id'), primary_key=True)

class EvidenceEntity(Base):
    __tablename__ = 'evidence_entities'
    evidence_id = Column(String(100), ForeignKey('evidence.evidence_id'), primary_key=True)
    entity_id = Column(String(100), ForeignKey('entities.entity_id'), primary_key=True)

class EvidenceRelationship(Base):
    __tablename__ = 'evidence_relationships'
    evidence_id = Column(String(100), ForeignKey('evidence.evidence_id'), primary_key=True)
    relationship_id = Column(String(100), ForeignKey('relationships.relationship_id'), primary_key=True)

class EvidenceFinding(Base):
    __tablename__ = 'evidence_findings'
    evidence_id = Column(String(100), ForeignKey('evidence.evidence_id'), primary_key=True)
    finding_id = Column(UUID(as_uuid=True), ForeignKey('findings.finding_id'), primary_key=True)

class EvidenceCustodyLog(Base):
    __tablename__ = 'evidence_custody_log'
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(String(100), ForeignKey('evidence.evidence_id'))
    action = Column(String(100), nullable=False)
    actor = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    previous_hash = Column(String(64))
    resulting_hash = Column(String(64))
    metadata_json = Column('metadata', JSONB)

