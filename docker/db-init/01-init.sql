-- Static initialization statements for the PostgreSQL container
-- Add extensions or other objects that do not depend on runtime variables
-- Example: enable pg_trgm extension used by search queries
CREATE EXTENSION IF NOT EXISTS pg_trgm;
