-- 0031 — Merging two titles keeps their tags
-- wv_merge_titles (0014, extended in 0018) moved episodes, watch events, scrobble
-- sessions, progress, people, genres and provenance onto the canonical title but
-- not tags: title_tags / season_tags / episode_tags cascaded away with the
-- duplicate. That mattered little while tags only sat on watched titles; now that
-- a series can be tagged from a Sonarr list (and may later meet a Plex-created row
-- for the same show), a merge must not drop them.
--
-- This is the 0018 function unchanged, plus step 5b (tags).

CREATE OR REPLACE FUNCTION wv_merge_titles(p_canonical uuid, p_dup uuid)
RETURNS void AS $$
BEGIN
    IF p_canonical = p_dup OR p_canonical IS NULL OR p_dup IS NULL THEN
        RETURN;
    END IF;

    -- 1. Ensure canonical owns every (season, episode) the dup has.
    INSERT INTO title_episodes
        (title_id, season, episode, name, overview, air_date, runtime_minutes,
         still_path, tmdb_id, normalized_key)
    SELECT p_canonical, season, episode, name, overview, air_date,
           runtime_minutes, still_path, tmdb_id, normalized_key
    FROM title_episodes WHERE title_id = p_dup
    ON CONFLICT (title_id, season, episode) DO NOTHING;

    -- 2. Repoint watch events onto the matching canonical episode, then title.
    UPDATE watch_events we
       SET episode_id = ce.id
      FROM title_episodes de
      JOIN title_episodes ce
        ON ce.title_id = p_canonical
       AND ce.season = de.season
       AND ce.episode = de.episode
     WHERE de.title_id = p_dup
       AND we.episode_id = de.id;
    UPDATE watch_events SET title_id = p_canonical WHERE title_id = p_dup;

    -- 2b. Repoint live scrobble sessions the same way (episode then title). Its
    --     title_id FK is ON DELETE SET NULL, so it must move before the delete.
    UPDATE scrobble_sessions ss
       SET episode_id = ce.id
      FROM title_episodes de
      JOIN title_episodes ce
        ON ce.title_id = p_canonical
       AND ce.season = de.season
       AND ce.episode = de.episode
     WHERE de.title_id = p_dup
       AND ss.episode_id = de.id;
    UPDATE scrobble_sessions SET title_id = p_canonical WHERE title_id = p_dup;

    -- 2c. Repoint precomputed progress where the canonical has no row for that
    --     user; the remaining dup rows cascade away with the dup delete. Counts
    --     are refreshed by the caller (wv_recompute_series_progress_title).
    UPDATE title_progress tp SET title_id = p_canonical
     WHERE tp.title_id = p_dup
       AND NOT EXISTS (
           SELECT 1 FROM title_progress c
           WHERE c.user_id = tp.user_id AND c.title_id = p_canonical);
    DELETE FROM title_progress WHERE title_id = p_dup;

    -- 3. Additive child rows: people/genres the dup had that canonical lacks.
    INSERT INTO title_people (title_id, person_id, role, character, job, ord)
    SELECT p_canonical, person_id, role, character, job, ord
    FROM title_people WHERE title_id = p_dup
    ON CONFLICT (title_id, person_id, role) DO NOTHING;

    INSERT INTO title_genres (title_id, genre_id)
    SELECT p_canonical, genre_id FROM title_genres WHERE title_id = p_dup
    ON CONFLICT DO NOTHING;

    -- 4. Provenance: keep dup entries for fields the canonical has none for.
    UPDATE metadata_provenance mp
       SET entity_id = p_canonical
     WHERE mp.entity_type = 'title' AND mp.entity_id = p_dup
       AND NOT EXISTS (
           SELECT 1 FROM metadata_provenance c
           WHERE c.entity_type = 'title' AND c.entity_id = p_canonical
             AND c.field = mp.field);
    DELETE FROM metadata_provenance
     WHERE entity_type = 'title' AND entity_id = p_dup;

    -- 5. Fill any empty scalar on the canonical from the dup.
    UPDATE titles c SET
        tmdb_id         = COALESCE(c.tmdb_id, d.tmdb_id),
        imdb_id         = COALESCE(c.imdb_id, d.imdb_id),
        year            = COALESCE(c.year, d.year),
        original_title  = COALESCE(c.original_title, d.original_title),
        overview        = COALESCE(NULLIF(c.overview, ''), d.overview),
        overviews       = d.overviews || c.overviews,
        runtime_minutes = COALESCE(c.runtime_minutes, d.runtime_minutes),
        poster_path     = COALESCE(c.poster_path, d.poster_path),
        backdrop_path   = COALESCE(c.backdrop_path, d.backdrop_path),
        external_ids    = d.external_ids || c.external_ids,
        metadata        = d.metadata || c.metadata,
        platform_override_provider_id =
            COALESCE(c.platform_override_provider_id, d.platform_override_provider_id),
        enriched_at     = COALESCE(c.enriched_at, d.enriched_at),
        updated_at      = now()
    FROM titles d
    WHERE c.id = p_canonical AND d.id = p_dup;

    -- 5b. Tags: move the dup's tags onto the canonical. Without this they cascade
    --     away with the dup (a tagged series would lose its tags when a Plex
    --     duplicate is merged into the older row). Episode tags follow the
    --     (season, episode) the canonical owns since step 1.
    INSERT INTO title_tags (title_id, tag_id)
    SELECT p_canonical, tag_id FROM title_tags WHERE title_id = p_dup
    ON CONFLICT DO NOTHING;
    INSERT INTO season_tags (title_id, season, tag_id)
    SELECT p_canonical, season, tag_id FROM season_tags WHERE title_id = p_dup
    ON CONFLICT DO NOTHING;
    INSERT INTO episode_tags (episode_id, tag_id)
    SELECT ce.id, et.tag_id
      FROM episode_tags et
      JOIN title_episodes de ON de.id = et.episode_id AND de.title_id = p_dup
      JOIN title_episodes ce ON ce.title_id = p_canonical
                            AND ce.season = de.season AND ce.episode = de.episode
    ON CONFLICT DO NOTHING;

    -- 6. Drop the dup; its remaining children cascade away.
    DELETE FROM titles WHERE id = p_dup;

    -- 7. The canonical's runtime/episode set changed — re-roll its daily agg.
    PERFORM wv_recompute_agg_for_title(p_canonical);
END;
$$ LANGUAGE plpgsql;
