--
-- PostgreSQL database dump
--

\restrict IBIR8wPkqQPiGrRno2p5q4fVtr3JwTPafyUdXgOmWqYWQNedXLhRSM9GyKYlnSc

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: document_chunks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_chunks (
    chunk_id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id character varying(100),
    chunk_index integer NOT NULL,
    page_number integer,
    text text NOT NULL,
    char_start integer,
    char_end integer,
    embedding public.vector,
    embedding_model character varying(100),
    embedding_created_at timestamp with time zone
);


ALTER TABLE public.document_chunks OWNER TO postgres;

--
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    document_id character varying(100) NOT NULL,
    case_id character varying(50),
    batch_id uuid,
    source_record_id character varying(100),
    filename character varying(255) NOT NULL,
    mime_type character varying(100),
    storage_uri character varying(500) NOT NULL,
    document_hash character varying(64) NOT NULL,
    page_count integer,
    ocr_status character varying(50),
    ocr_confidence double precision,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- Name: entity_mentions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entity_mentions (
    mention_id character varying(100) NOT NULL,
    entity_type public.entity_type_enum NOT NULL,
    extracted_text text NOT NULL,
    normalized_value character varying(255) NOT NULL,
    extraction_method character varying(50) NOT NULL,
    extraction_confidence double precision,
    source_record_id character varying(100),
    document_chunk_id uuid,
    start_offset integer,
    end_offset integer,
    extraction_run_id uuid,
    resolved_entity_id character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT entity_mentions_check CHECK ((((source_record_id IS NOT NULL) AND (document_chunk_id IS NULL)) OR ((source_record_id IS NULL) AND (document_chunk_id IS NOT NULL))))
);


ALTER TABLE public.entity_mentions OWNER TO postgres;

--
-- Name: evidence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evidence (
    evidence_id character varying(100) NOT NULL,
    case_id character varying(50),
    evidence_type character varying(100) NOT NULL,
    title character varying(255),
    storage_uri character varying(500) NOT NULL,
    file_hash character varying(64) NOT NULL,
    hash_algorithm character varying(50) DEFAULT 'SHA-256'::character varying,
    source character varying(255),
    collected_at timestamp with time zone,
    collected_by uuid,
    sealed boolean DEFAULT false,
    fabric_transaction_id character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.evidence OWNER TO postgres;

--
-- Name: relationship_assertions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.relationship_assertions (
    assertion_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_entity_id character varying(100),
    target_entity_id character varying(100),
    relationship_type character varying(100) NOT NULL,
    source_record_id character varying(100),
    document_chunk_id uuid,
    evidence_text text,
    extraction_method character varying(50),
    extraction_confidence double precision,
    negated boolean DEFAULT false,
    temporal_context jsonb,
    location_context jsonb,
    extraction_run_id uuid,
    status character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.relationship_assertions OWNER TO postgres;

--
-- Name: relationships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.relationships (
    relationship_id character varying(100) NOT NULL,
    source_entity_id character varying(100),
    relationship_type character varying(100) NOT NULL,
    target_entity_id character varying(100),
    status public.validation_status_enum DEFAULT 'NEEDS_REVIEW'::public.validation_status_enum NOT NULL,
    confidence double precision,
    first_observed_at timestamp with time zone,
    last_observed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.relationships OWNER TO postgres;

--
-- Name: source_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.source_records (
    record_id character varying(100) NOT NULL,
    batch_id uuid,
    case_id character varying(50),
    source_type character varying(50) NOT NULL,
    external_record_id character varying(255),
    record_timestamp timestamp with time zone,
    raw_payload jsonb NOT NULL,
    normalized_payload jsonb,
    source_hash character varying(64),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.source_records OWNER TO postgres;

--
-- Name: document_chunks document_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_chunks
    ADD CONSTRAINT document_chunks_pkey PRIMARY KEY (chunk_id);


--
-- Name: documents documents_document_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_document_hash_key UNIQUE (document_hash);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (document_id);


--
-- Name: entity_mentions entity_mentions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_mentions
    ADD CONSTRAINT entity_mentions_pkey PRIMARY KEY (mention_id);


--
-- Name: evidence evidence_file_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_file_hash_key UNIQUE (file_hash);


--
-- Name: evidence evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_pkey PRIMARY KEY (evidence_id);


--
-- Name: relationship_assertions relationship_assertions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationship_assertions
    ADD CONSTRAINT relationship_assertions_pkey PRIMARY KEY (assertion_id);


--
-- Name: relationships relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationships
    ADD CONSTRAINT relationships_pkey PRIMARY KEY (relationship_id);


--
-- Name: relationships relationships_source_entity_id_relationship_type_target_ent_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationships
    ADD CONSTRAINT relationships_source_entity_id_relationship_type_target_ent_key UNIQUE (source_entity_id, relationship_type, target_entity_id);


--
-- Name: source_records source_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_records
    ADD CONSTRAINT source_records_pkey PRIMARY KEY (record_id);


--
-- Name: idx_sr_batch; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sr_batch ON public.source_records USING btree (batch_id);


--
-- Name: idx_sr_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sr_type ON public.source_records USING btree (source_type);


--
-- Name: document_chunks document_chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_chunks
    ADD CONSTRAINT document_chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(document_id);


--
-- Name: documents documents_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.ingestion_batches(batch_id);


--
-- Name: documents documents_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(case_id);


--
-- Name: documents documents_source_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES public.source_records(record_id);


--
-- Name: entity_mentions entity_mentions_document_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_mentions
    ADD CONSTRAINT entity_mentions_document_chunk_id_fkey FOREIGN KEY (document_chunk_id) REFERENCES public.document_chunks(chunk_id);


--
-- Name: entity_mentions entity_mentions_extraction_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_mentions
    ADD CONSTRAINT entity_mentions_extraction_run_id_fkey FOREIGN KEY (extraction_run_id) REFERENCES public.processing_runs(run_id);


--
-- Name: entity_mentions entity_mentions_resolved_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_mentions
    ADD CONSTRAINT entity_mentions_resolved_entity_id_fkey FOREIGN KEY (resolved_entity_id) REFERENCES public.entities(entity_id);


--
-- Name: entity_mentions entity_mentions_source_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_mentions
    ADD CONSTRAINT entity_mentions_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES public.source_records(record_id);


--
-- Name: evidence evidence_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(case_id);


--
-- Name: evidence evidence_collected_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_collected_by_fkey FOREIGN KEY (collected_by) REFERENCES public.users(user_id);


--
-- Name: relationship_assertions relationship_assertions_document_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationship_assertions
    ADD CONSTRAINT relationship_assertions_document_chunk_id_fkey FOREIGN KEY (document_chunk_id) REFERENCES public.document_chunks(chunk_id);


--
-- Name: relationship_assertions relationship_assertions_extraction_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationship_assertions
    ADD CONSTRAINT relationship_assertions_extraction_run_id_fkey FOREIGN KEY (extraction_run_id) REFERENCES public.processing_runs(run_id);


--
-- Name: relationship_assertions relationship_assertions_source_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationship_assertions
    ADD CONSTRAINT relationship_assertions_source_entity_id_fkey FOREIGN KEY (source_entity_id) REFERENCES public.entities(entity_id);


--
-- Name: relationship_assertions relationship_assertions_source_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationship_assertions
    ADD CONSTRAINT relationship_assertions_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES public.source_records(record_id);


--
-- Name: relationship_assertions relationship_assertions_target_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationship_assertions
    ADD CONSTRAINT relationship_assertions_target_entity_id_fkey FOREIGN KEY (target_entity_id) REFERENCES public.entities(entity_id);


--
-- Name: relationships relationships_source_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationships
    ADD CONSTRAINT relationships_source_entity_id_fkey FOREIGN KEY (source_entity_id) REFERENCES public.entities(entity_id);


--
-- Name: relationships relationships_target_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relationships
    ADD CONSTRAINT relationships_target_entity_id_fkey FOREIGN KEY (target_entity_id) REFERENCES public.entities(entity_id);


--
-- Name: source_records source_records_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_records
    ADD CONSTRAINT source_records_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.ingestion_batches(batch_id);


--
-- Name: source_records source_records_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_records
    ADD CONSTRAINT source_records_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(case_id);


--
-- PostgreSQL database dump complete
--

\unrestrict IBIR8wPkqQPiGrRno2p5q4fVtr3JwTPafyUdXgOmWqYWQNedXLhRSM9GyKYlnSc

