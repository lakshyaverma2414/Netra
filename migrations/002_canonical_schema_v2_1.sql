BEGIN;

-- 1. Create Enums
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'provenance_status_enum') THEN
        CREATE TYPE provenance_status_enum AS ENUM ('VERIFIED', 'LEGACY', 'MIGRATED');
    END IF;
END$$;

-- 2. New Governance Tables
CREATE TABLE IF NOT EXISTS source_systems (
    system_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    agency VARCHAR(255),
    classification VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS source_datasets (
    dataset_id VARCHAR(100) PRIMARY KEY,
    system_id VARCHAR(50) REFERENCES source_systems(system_id),
    description TEXT
);

-- Note: ingestion_batches already exists
-- Let's add any missing columns safely
ALTER TABLE ingestion_batches ADD COLUMN IF NOT EXISTS dataset_id VARCHAR(100) REFERENCES source_datasets(dataset_id);
ALTER TABLE ingestion_batches ADD COLUMN IF NOT EXISTS records_received INT DEFAULT 0;
ALTER TABLE ingestion_batches ADD COLUMN IF NOT EXISTS records_failed INT DEFAULT 0;

-- source_records already exists. It has record_id (VARCHAR), source_hash, source_type.
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS dataset_id VARCHAR(100) REFERENCES source_datasets(dataset_id);
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS schema_version VARCHAR(50);
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS observed_at TIMESTAMPTZ;
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS occurred_at TIMESTAMPTZ;
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS reported_at TIMESTAMPTZ;
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'PENDING';

-- Drop any old unique constraint if we want the new one, but let's just add a new one safely
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'source_records_idempotency_key'
    ) THEN
        ALTER TABLE source_records ADD CONSTRAINT source_records_idempotency_key UNIQUE (dataset_id, source_hash);
    END IF;
END$$;

-- 3. Processing & Artifacts
-- processing_runs already exists!
-- It has: run_id, pipeline_name, pipeline_version, model_version, input_batch_id, status, started_at, completed_at, configuration.
-- It maps well to our V2.1 design.

CREATE TABLE IF NOT EXISTS derived_artifacts (
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id VARCHAR(100), -- FK deferred
    processing_run_id UUID REFERENCES processing_runs(run_id),
    artifact_type VARCHAR(100) NOT NULL,
    storage_uri VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100),
    artifact_hash VARCHAR(64),
    hash_algorithm VARCHAR(50) DEFAULT 'SHA-256',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Observations & Extraction
-- Because the DB uses document_chunks and direct references, we can introduce 'observations' as an abstraction
CREATE TABLE IF NOT EXISTS observations (
    observation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_record_id VARCHAR(100) REFERENCES source_records(record_id),
    derived_artifact_id UUID REFERENCES derived_artifacts(artifact_id),
    processing_run_id UUID REFERENCES processing_runs(run_id),
    observation_type VARCHAR(100) NOT NULL,
    raw_text TEXT,
    normalized_value VARCHAR(500),
    observed_at TIMESTAMPTZ,
    extraction_confidence DOUBLE PRECISION,
    CONSTRAINT observation_provenance_check CHECK (source_record_id IS NOT NULL OR derived_artifact_id IS NOT NULL)
);

-- 5. Events & Locations
CREATE TABLE IF NOT EXISTS locations (
    location_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    district VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    jurisdiction VARCHAR(100),
    location_type VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(100) PRIMARY KEY,
    case_id VARCHAR(50) REFERENCES cases(case_id),
    event_type VARCHAR(100) NOT NULL,
    occurred_at TIMESTAMPTZ,
    observed_at TIMESTAMPTZ,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    location_id VARCHAR(100) REFERENCES locations(location_id),
    description TEXT,
    source_record_id VARCHAR(100) REFERENCES source_records(record_id)
);

CREATE TABLE IF NOT EXISTS event_entities (
    event_id VARCHAR(100) REFERENCES events(event_id),
    entity_id VARCHAR(100) REFERENCES entities(entity_id),
    role VARCHAR(100),
    PRIMARY KEY (event_id, entity_id)
);

-- 6. Mentions and Assertions
-- entity_mentions already exists! 
ALTER TABLE entity_mentions ADD COLUMN IF NOT EXISTS observation_id UUID REFERENCES observations(observation_id);

-- relationship_assertions already exists!
ALTER TABLE relationship_assertions ADD COLUMN IF NOT EXISTS observation_id UUID REFERENCES observations(observation_id);
ALTER TABLE relationship_assertions ADD COLUMN IF NOT EXISTS valid_from TIMESTAMPTZ;
ALTER TABLE relationship_assertions ADD COLUMN IF NOT EXISTS valid_to TIMESTAMPTZ;

-- 7. Alter Existing Tables Safely
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS source_record_id VARCHAR(100) REFERENCES source_records(record_id);
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS provenance_status provenance_status_enum DEFAULT 'VERIFIED';
UPDATE evidence SET provenance_status = 'LEGACY' WHERE provenance_status IS NULL OR source_record_id IS NULL;

ALTER TABLE relationships ADD COLUMN IF NOT EXISTS valid_from TIMESTAMPTZ;
ALTER TABLE relationships ADD COLUMN IF NOT EXISTS valid_to TIMESTAMPTZ;

-- Add FK from derived_artifacts to evidence
ALTER TABLE derived_artifacts DROP CONSTRAINT IF EXISTS fk_derived_evidence;
ALTER TABLE derived_artifacts ADD CONSTRAINT fk_derived_evidence FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id);

COMMIT;
