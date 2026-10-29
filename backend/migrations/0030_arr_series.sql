-- 0030 — Running series from Sonarr
-- A snapshot of the series a Sonarr connection reports as running (status
-- 'continuing' and monitored), replaced on every sync like calendar_items. It lets
-- Imports list those series and tag them, and gives the "What's next" overview
-- Sonarr's own next-airing date. A series is only added to the catalog (titles)
-- when someone tags it; until then this table is all WatchVault knows about it.
CREATE TABLE arr_series (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        uuid NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    connection_id       uuid NOT NULL REFERENCES source_connections(id) ON DELETE CASCADE,
    sonarr_id           integer NOT NULL,
    title               text NOT NULL,
    normalized_key      text NOT NULL,                 -- util.title_key(title, 'series')
    year                integer,
    status              text NOT NULL,                 -- 'continuing' (the only one stored for now)
    monitored           boolean NOT NULL DEFAULT true,
    tmdb_id             integer,                       -- null when this Sonarr does not report one
    tvdb_id             integer,
    imdb_id             text,
    network             text,
    poster_url          text,                          -- absolute URL from Sonarr (may be null)
    next_airing         timestamptz,
    previous_airing     timestamptz,
    season_count        integer,
    episode_file_count  integer,                       -- episodes on disk
    episode_count       integer,                       -- aired, monitored episodes
    total_episode_count integer,
    fetched_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (connection_id, sonarr_id)
);
CREATE INDEX idx_arr_series_household ON arr_series(household_id);
CREATE INDEX idx_arr_series_tmdb      ON arr_series(tmdb_id);
