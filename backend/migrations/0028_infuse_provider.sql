-- 0028 — Add the Infuse provider
-- Infuse (Firecore, tvOS bundle com.firecore.infuse) plays local/NAS libraries and
-- reports through Home Assistant like the other Apple TV apps. Giving it its own
-- provider keeps those scrobbles out of the 'homeassistant' fallback bucket. Like
-- the other non-API placeholders it uses the generic adapter and a csv ingest type,
-- so the sync scheduler (which only schedules ingest_type='api') never tries to
-- sync it. Idempotent.
INSERT INTO providers (key, name, ingest_type, adapter, color, is_system) VALUES
    ('infuse', 'Infuse', 'csv', 'generic', '#FC7A1E', true)
ON CONFLICT (key) DO NOTHING;
