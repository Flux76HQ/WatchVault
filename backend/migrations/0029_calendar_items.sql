-- 0029 — Sonarr / Radarr calendars for the dashboard "Continue watching" block
-- Sonarr and Radarr are *calendar* sources: they know what was downloaded
-- recently, not what anyone watched. Each sync (manual, or the worker's 15-minute
-- schedule) replaces the connection's rows here with the calendar window it just
-- read, so the dashboard never calls Sonarr/Radarr itself. Only items that already
-- have a file are stored: the block shows what is ready to watch, not an agenda.
-- Whether an item has been watched is decided at read time against watch_events.
INSERT INTO providers (key, name, ingest_type, adapter, color) VALUES
    ('sonarr', 'Sonarr', 'api', 'sonarr_api', '#35C5F4'),
    ('radarr', 'Radarr', 'api', 'radarr_api', '#FFC230')
ON CONFLICT (key) DO NOTHING;

CREATE TABLE calendar_items (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    uuid NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    connection_id   uuid NOT NULL REFERENCES source_connections(id) ON DELETE CASCADE,
    source          text NOT NULL,                 -- 'sonarr' | 'radarr'
    kind            text NOT NULL,                 -- 'series' (one episode) | 'movie'
    external_key    text NOT NULL,                 -- stable per source: 'e:<episodeId>' | 'm:<movieId>'
    title           text NOT NULL,                 -- series or movie title
    year            integer,
    season          integer,
    episode         integer,
    episode_name    text,
    tmdb_id         integer,                       -- matches titles.tmdb_id when the title is known
    tvdb_id         integer,
    imdb_id         text,
    poster_url      text,                          -- absolute URL from Sonarr/Radarr (may be null)
    runtime_minutes integer,
    air_date        date,
    available_at    timestamptz NOT NULL,          -- when the file arrived (falls back to the air/release date)
    fetched_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (connection_id, external_key)
);
CREATE INDEX idx_calendar_items_household ON calendar_items(household_id, available_at DESC);
CREATE INDEX idx_calendar_items_tmdb      ON calendar_items(tmdb_id);
