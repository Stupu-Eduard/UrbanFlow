-- Initialize UrbanFlowAI Database
-- This script runs automatically when PostgreSQL container starts

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create schema
CREATE SCHEMA IF NOT EXISTS urbanflow;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA urbanflow TO urbanflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA urbanflow TO urbanflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA urbanflow TO urbanflow;

-- Verify PostGIS
SELECT PostGIS_version();

