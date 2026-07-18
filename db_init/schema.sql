-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- DATASETS TABLE
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    uri TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COLUMNS TABLE (schema information)
CREATE TABLE columns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    column_name VARCHAR(255),
    data_type VARCHAR(50),
    is_nullable BOOLEAN
);

-- PIPELINE RUNS
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name VARCHAR(255),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50)
);

-- COLUMN STATISTICS
CREATE TABLE column_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    column_id UUID REFERENCES columns(id) ON DELETE CASCADE,
    run_id UUID REFERENCES runs(id),
    null_fraction FLOAT,
    distinct_count INT
);

-- DATA QUALITY RESULTS
CREATE TABLE data_quality_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES runs(id),
    dataset_id UUID REFERENCES datasets(id),
    rule_name VARCHAR(255),
    success BOOLEAN,
    observed_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LINEAGE GRAPH
CREATE TABLE lineage_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_dataset_id UUID REFERENCES datasets(id),
    target_dataset_id UUID REFERENCES datasets(id),
    run_id UUID REFERENCES runs(id),
    edge_type VARCHAR(50)
);