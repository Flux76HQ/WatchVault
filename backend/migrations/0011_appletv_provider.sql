-- 0011 — Apple TV+ provider
-- Added so Trakt watch events whose TMDB network is "Apple TV+" can be
-- re-attributed to a real streaming service (and so it shows up in the
-- household's streaming-service list). Like the other non-API placeholders
-- (HBO Max, Prime Video, Disney+) it uses the generic adapter and a csv
-- ingest type, so the sync scheduler (which only schedules ingest_type='api')
-- never tries to sync it. Idempotent.
INSERT INTO providers (key, name, ingest_type, adapter, color, is_system) VALUES
    ('appletv', 'Apple TV+', 'csv', 'generic', '#2C2C2E', true)
ON CONFLICT (key) DO NOTHING;
