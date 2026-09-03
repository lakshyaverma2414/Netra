-- Identity & Access
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_permissions (
    user_id UUID PRIMARY KEY REFERENCES users(user_id),
    permissions JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    case_id VARCHAR(50), 
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Investigation
CREATE TYPE case_status_enum AS ENUM ('ACTIVE', 'CLOSED', 'COLD', 'PENDING');

CREATE TABLE cases (
    case_id VARCHAR(50) PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    jurisdiction VARCHAR(100),
    status case_status_enum NOT NULL DEFAULT 'ACTIVE',
    priority VARCHAR(50),
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_jurisdiction ON cases(jurisdiction);

ALTER TABLE audit_log ADD CONSTRAINT fk_audit_case FOREIGN KEY (case_id) REFERENCES cases(case_id);

CREATE TABLE case_links (
    source_case_id VARCHAR(50) REFERENCES cases(case_id),
    target_case_id VARCHAR(50) REFERENCES cases(case_id),
    link_reason TEXT NOT NULL,
    PRIMARY KEY (source_case_id, target_case_id),
    CHECK (source_case_id < target_case_id)
);

-- Ingestion
CREATE TABLE ingestion_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id VARCHAR(50) REFERENCES cases(case_id),
    submitted_by UUID REFERENCES users(user_id),
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_details TEXT
);

CREATE TABLE data_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE source_records (
    record_id VARCHAR(100) PRIMARY KEY,
    batch_id UUID REFERENCES ingestion_batches(batch_id),
    case_id VARCHAR(50) REFERENCES cases(case_id),
    source_type VARCHAR(50) NOT NULL,
    external_record_id VARCHAR(255),
    record_timestamp TIMESTAMPTZ,
    raw_payload JSONB NOT NULL,
    normalized_payload JSONB,
    source_hash VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_sr_batch ON source_records(batch_id);
CREATE INDEX idx_sr_type ON source_records(source_type);

CREATE TABLE documents (
    document_id VARCHAR(100) PRIMARY KEY,
    case_id VARCHAR(50) REFERENCES cases(case_id),
    batch_id UUID REFERENCES ingestion_batches(batch_id),
    source_record_id VARCHAR(100) REFERENCES source_records(record_id),
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100),
    storage_uri VARCHAR(500) NOT NULL,
    document_hash VARCHAR(64) UNIQUE NOT NULL,
    page_count INT,
    ocr_status VARCHAR(50),
    ocr_confidence FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(100) REFERENCES documents(document_id),
    chunk_index INT NOT NULL,
    page_number INT,
    text TEXT NOT NULL,
    char_start INT,
    char_end INT,
    embedding VECTOR,
    embedding_model VARCHAR(100),
    embedding_created_at TIMESTAMPTZ
);

-- Processing Provenance
CREATE TABLE processing_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_name VARCHAR(100) NOT NULL,
    pipeline_version VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    input_batch_id UUID REFERENCES ingestion_batches(batch_id),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    configuration JSONB
);

-- Entity Domain
CREATE TYPE resolution_status_enum AS ENUM ('CONFIRMED', 'PROBABLE', 'CANDIDATE', 'REJECTED', 'UNRESOLVED');
CREATE TYPE entity_type_enum AS ENUM ('PERSON', 'PHONE', 'IMEI', 'VEHICLE', 'LOCATION', 'ORGANIZATION', 'EVENT', 'BANK_ACCOUNT', 'UPI_ID', 'SOCIAL_ACCOUNT', 'CASE');

CREATE TABLE entities (
    entity_id VARCHAR(100) PRIMARY KEY,
    entity_type entity_type_enum NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    normalized_value VARCHAR(255) NOT NULL,
    resolution_status resolution_status_enum NOT NULL DEFAULT 'UNRESOLVED',
    resolution_score FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_normalized ON entities(normalized_value);

CREATE TABLE entity_mentions (
    mention_id VARCHAR(100) PRIMARY KEY,
    entity_type entity_type_enum NOT NULL,
    extracted_text TEXT NOT NULL,
    normalized_value VARCHAR(255) NOT NULL,
    extraction_method VARCHAR(50) NOT NULL,
    extraction_confidence FLOAT,
    source_record_id VARCHAR(100) REFERENCES source_records(record_id),
    document_chunk_id UUID REFERENCES document_chunks(chunk_id),
    start_offset INT,
    end_offset INT,
    extraction_run_id UUID REFERENCES processing_runs(run_id),
    resolved_entity_id VARCHAR(100) REFERENCES entities(entity_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (source_record_id IS NOT NULL AND document_chunk_id IS NULL) OR 
        (source_record_id IS NULL AND document_chunk_id IS NOT NULL)
    )
);

CREATE TABLE entity_aliases (
    alias_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(100) REFERENCES entities(entity_id),
    alias VARCHAR(255) NOT NULL,
    normalized_alias VARCHAR(255) NOT NULL,
    source VARCHAR(255),
    confidence FLOAT,
    provenance JSONB
);

CREATE TABLE entity_resolution_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mention_id VARCHAR(100) REFERENCES entity_mentions(mention_id),
    candidate_entity_id VARCHAR(100) REFERENCES entities(entity_id),
    decision resolution_status_enum NOT NULL,
    probability FLOAT,
    matching_features JSONB,
    resolver_version VARCHAR(50),
    model_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Case Entities
CREATE TABLE case_entities (
    case_id VARCHAR(50) REFERENCES cases(case_id),
    entity_id VARCHAR(100) REFERENCES entities(entity_id),
    association_type VARCHAR(100),
    confidence FLOAT,
    source VARCHAR(255),
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (case_id, entity_id)
);
CREATE INDEX idx_case_entities_entity ON case_entities(entity_id, case_id);

-- Relationship Domain
CREATE TYPE validation_status_enum AS ENUM ('CONFIRMED', 'NEEDS_REVIEW', 'REJECTED');

CREATE TABLE relationships (
    relationship_id VARCHAR(100) PRIMARY KEY,
    source_entity_id VARCHAR(100) REFERENCES entities(entity_id),
    relationship_type VARCHAR(100) NOT NULL,
    target_entity_id VARCHAR(100) REFERENCES entities(entity_id),
    status validation_status_enum NOT NULL DEFAULT 'NEEDS_REVIEW',
    confidence FLOAT,
    first_observed_at TIMESTAMPTZ,
    last_observed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_entity_id, relationship_type, target_entity_id)
);

CREATE TABLE relationship_assertions (
    assertion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id VARCHAR(100) REFERENCES entities(entity_id),
    target_entity_id VARCHAR(100) REFERENCES entities(entity_id),
    relationship_type VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(100) REFERENCES source_records(record_id),
    document_chunk_id UUID REFERENCES document_chunks(chunk_id),
    evidence_text TEXT,
    extraction_method VARCHAR(50),
    extraction_confidence FLOAT,
    negated BOOLEAN DEFAULT FALSE,
    temporal_context JSONB,
    location_context JSONB,
    extraction_run_id UUID REFERENCES processing_runs(run_id),
    status VARCHAR(50) NOT NULL, 
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE relationship_assertion_links (
    relationship_id VARCHAR(100) REFERENCES relationships(relationship_id),
    assertion_id UUID REFERENCES relationship_assertions(assertion_id),
    PRIMARY KEY (relationship_id, assertion_id)
);

CREATE TABLE relationship_cases (
    relationship_id VARCHAR(100) REFERENCES relationships(relationship_id),
    case_id VARCHAR(50) REFERENCES cases(case_id),
    PRIMARY KEY (relationship_id, case_id)
);
CREATE INDEX idx_relationship_cases_case ON relationship_cases(case_id, relationship_id);

-- Evidence
CREATE TABLE evidence (
    evidence_id VARCHAR(100) PRIMARY KEY,
    case_id VARCHAR(50) REFERENCES cases(case_id),
    evidence_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    storage_uri VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    hash_algorithm VARCHAR(50) DEFAULT 'SHA-256',
    source VARCHAR(255),
    collected_at TIMESTAMPTZ,
    collected_by UUID REFERENCES users(user_id),
    sealed BOOLEAN DEFAULT FALSE,
    fabric_transaction_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE evidence_cases (
    evidence_id VARCHAR(100) REFERENCES evidence(evidence_id),
    case_id VARCHAR(50) REFERENCES cases(case_id),
    PRIMARY KEY (evidence_id, case_id)
);
CREATE TABLE evidence_entities (
    evidence_id VARCHAR(100) REFERENCES evidence(evidence_id),
    entity_id VARCHAR(100) REFERENCES entities(entity_id),
    PRIMARY KEY (evidence_id, entity_id)
);
CREATE TABLE evidence_relationships (
    evidence_id VARCHAR(100) REFERENCES evidence(evidence_id),
    relationship_id VARCHAR(100) REFERENCES relationships(relationship_id),
    PRIMARY KEY (evidence_id, relationship_id)
);

CREATE TABLE evidence_custody_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id VARCHAR(100) REFERENCES evidence(evidence_id),
    action VARCHAR(100) NOT NULL,
    actor UUID REFERENCES users(user_id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    previous_hash VARCHAR(64),
    resulting_hash VARCHAR(64),
    metadata JSONB
);

-- Findings
CREATE TABLE findings (
    finding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id VARCHAR(50) REFERENCES cases(case_id),
    finding_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50),
    confidence FLOAT,
    status VARCHAR(50) NOT NULL DEFAULT 'NEW',
    generated_by VARCHAR(100),
    algorithm_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_findings_case ON findings(case_id);

CREATE TABLE evidence_findings (
    evidence_id VARCHAR(100) REFERENCES evidence(evidence_id),
    finding_id UUID REFERENCES findings(finding_id),
    PRIMARY KEY (evidence_id, finding_id)
);

CREATE TABLE finding_entities (
    finding_id UUID REFERENCES findings(finding_id),
    entity_id VARCHAR(100) REFERENCES entities(entity_id),
    PRIMARY KEY (finding_id, entity_id)
);
CREATE TABLE finding_relationships (
    finding_id UUID REFERENCES findings(finding_id),
    relationship_id VARCHAR(100) REFERENCES relationships(relationship_id),
    PRIMARY KEY (finding_id, relationship_id)
);
CREATE TABLE finding_assertions (
    finding_id UUID REFERENCES findings(finding_id),
    assertion_id UUID REFERENCES relationship_assertions(assertion_id),
    PRIMARY KEY (finding_id, assertion_id)
);
CREATE TABLE finding_documents (
    finding_id UUID REFERENCES findings(finding_id),
    document_id VARCHAR(100) REFERENCES documents(document_id),
    PRIMARY KEY (finding_id, document_id)
);

-- Feedback
CREATE TABLE investigator_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relationship_id VARCHAR(100) REFERENCES relationships(relationship_id),
    finding_id UUID REFERENCES findings(finding_id),
    investigator_id UUID REFERENCES users(user_id),
    decision VARCHAR(50) NOT NULL,
    reason TEXT,
    comments TEXT,
    model_involved VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (relationship_id IS NOT NULL AND finding_id IS NULL) OR
        (relationship_id IS NULL AND finding_id IS NOT NULL)
    )
);
