-- Create the main table to store raw GLPI ticket data
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    glpi_ticket_id INTEGER UNIQUE NOT NULL,
    raw_data JSONB NOT NULL,
    status INTEGER NOT NULL,
    priority INTEGER NOT NULL,
    -- Assuming assignee_id is available in raw_data and can be used to link to a group.
    -- In a real GLPI setup, mapping assignee to group might involve more complex joins
    -- with glpi_users and glpi_groups_users tables. Here, we simplify for the MV.
    assignee_id INTEGER,
    opened_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a lookup table for GLPI status names (optional, but good for readability)
CREATE TABLE IF NOT EXISTS glpi_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Populate GLPI statuses (based on research notes [1, 2])
INSERT INTO glpi_statuses (id, name) VALUES
(1, 'New'),
(2, 'Processing (Assigned)'),
(3, 'Processing (Planned)'),
(4, 'Pending'),
(5, 'Solved'),
(6, 'Closed'),
(10, 'Approval')
ON CONFLICT (id) DO NOTHING;

-- Create a lookup table for GLPI priority names (optional, but good for readability)
CREATE TABLE IF NOT EXISTS glpi_priorities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Populate GLPI priorities (based on research notes [1, 2])
INSERT INTO glpi_priorities (id, name) VALUES
(1, 'Very Low'),
(2, 'Low'),
(3, 'Medium'),
(4, 'High'),
(5, 'Very High'),
(6, 'Major')
ON CONFLICT (id) DO NOTHING;

-- Create a lookup table for GLPI groups (simplified for MV, assuming assignee_id maps to a group ID)
-- This table would typically be populated from GLPI's group data.
CREATE TABLE IF NOT EXISTS glpi_groups (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Example data for glpi_groups (replace with actual data from your GLPI instance)
INSERT INTO glpi_groups (id, name) VALUES
(1, 'Support Level 1'),
(2, 'Network Team'),
(3, 'Development Team'),
(4, 'Admin Team')
ON CONFLICT (id) DO NOTHING;


-- Create the materialized view for ticket summary
-- This view will join with lookup tables for human-readable names.
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ticket_summary AS
SELECT
    t.glpi_ticket_id AS ticket_id,
    gs.name AS status,
    gp.name AS priority,
    COALESCE(gg.name, 'Unassigned') AS group_name, -- Use COALESCE for unassigned tickets
    t.opened_at::DATE AS opened_at -- Cast to DATE to remove time component
FROM
    tickets t
LEFT JOIN
    glpi_statuses gs ON t.status = gs.id
LEFT JOIN
    glpi_priorities gp ON t.priority = gp.id
LEFT JOIN
    glpi_groups gg ON t.assignee_id = gg.id -- Simplified: assuming assignee_id maps to a group ID
WITH NO DATA; -- Create empty initially

-- Create a unique index on the materialized view for CONCURRENTLY refreshes [3]
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ticket_summary_ticket_id ON mv_ticket_summary (ticket_id);