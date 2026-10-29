"""Sonarr / Radarr adapters — read the calendar, not the watch history.

Both expose ``GET {base_url}/api/v3/calendar?start=..&end=..`` (header ``X-Api-Key``).
They know what was downloaded, not what anyone watched, so they are *calendar*
sources: ``fetch_calendar`` returns the items of a date window that already have a
file, normalised to the shape stored in ``calendar_items``. The dashboard
"Continue watching" block compares those with the household's watch history.

Config: {"base_url": "http://host:8989", "api_key": "..."}
"""
from __future__ import annotations

import datetime as dt

import requests

from .base import SourceAdapter

TIMEOUT = 20


def _int(value) -> int | None:
    try:
        n = int(value)
    except (ValueError, TypeError):
        return None
    return n or None  # Sonarr/Radarr report an unknown id as 0


def _parse_dt(value) -> dt.datetime | None:
    """ISO-8601 from Sonarr/Radarr (``2025-06-01T20:00:00Z`` or a bare date)."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _poster(images) -> str | None:
    """The poster's absolute URL. ``url`` is relative to the *arr instance and needs
    its API key, so only ``remoteUrl`` (the TMDB/TVDB copy) is usable in a browser."""
    for img in images or []:
        if img.get("coverType") == "poster":
            remote = img.get("remoteUrl")
            if isinstance(remote, str) and remote.startswith("http"):
                return remote
    return None


def _item(source: str, kind: str, key: str, title: str, *, available: dt.datetime | None,
          air: dt.datetime | None, **extra) -> dict | None:
    when = available or air
    if not title or when is None:
        return None
    return {"source": source, "kind": kind, "external_key": key, "title": title,
            "air_date": (air or when).date(), "available_at": when, **extra}


def sonarr_item(raw: dict) -> dict | None:
    """One Sonarr calendar episode -> a calendar item, or ``None`` when it has no file
    (still to air / not downloaded), has no usable date, or has no series."""
    if not raw.get("hasFile"):
        return None
    series = raw.get("series") or {}
    episode_file = raw.get("episodeFile") or {}
    return _item(
        "sonarr", "series", f"e:{raw.get('id')}", series.get("title") or "",
        available=_parse_dt(episode_file.get("dateAdded")),
        air=_parse_dt(raw.get("airDateUtc") or raw.get("airDate")),
        year=_int(series.get("year")),
        season=raw.get("seasonNumber"), episode=raw.get("episodeNumber"),
        episode_name=raw.get("title") or None,
        tmdb_id=_int(series.get("tmdbId")), tvdb_id=_int(series.get("tvdbId")),
        imdb_id=series.get("imdbId") or None,
        poster_url=_poster(series.get("images")),
        runtime_minutes=_int(raw.get("runtime") or series.get("runtime")),
    )


def radarr_item(raw: dict) -> dict | None:
    """One Radarr calendar movie -> a calendar item, or ``None`` when it has no file."""
    if not raw.get("hasFile"):
        return None
    movie_file = raw.get("movieFile") or {}
    release = next((_parse_dt(raw.get(k)) for k in ("digitalRelease", "physicalRelease", "inCinemas")
                    if _parse_dt(raw.get(k))), None)
    return _item(
        "radarr", "movie", f"m:{raw.get('id')}", raw.get("title") or "",
        available=_parse_dt(movie_file.get("dateAdded")), air=release,
        year=_int(raw.get("year")), season=None, episode=None, episode_name=None,
        tmdb_id=_int(raw.get("tmdbId")), tvdb_id=None, imdb_id=raw.get("imdbId") or None,
        poster_url=_poster(raw.get("images")),
        runtime_minutes=_int(raw.get("runtime")),
    )


class _ArrAdapter(SourceAdapter):
    ingest_type = "api"
    produces = "calendar"
    config_fields = [
        {"key": "base_url", "label": "Server URL", "type": "url", "required": True,
         "placeholder": "http://192.168.1.10:8989"},
        {"key": "api_key", "label": "API key", "type": "password", "required": True,
         "placeholder": "API key",
         "help": "Settings → General → Security → API Key."},
    ]
    _params: dict = {}
    _normalise = staticmethod(lambda raw: None)

    def fetch_calendar(self, config: dict, start: dt.date, end: dt.date) -> list[dict]:
        base = (config.get("base_url") or "").rstrip("/")
        key = config.get("api_key")
        if not base or not key:
            raise ValueError(f"{self.display_name} connection requires base_url and api_key")
        resp = requests.get(
            f"{base}/api/v3/calendar", headers={"X-Api-Key": key, "Accept": "application/json"},
            params={"start": start.isoformat(), "end": end.isoformat(),
                    "unmonitored": "false", **self._params},
            timeout=TIMEOUT)
        if resp.status_code in (401, 403):
            raise ValueError(f"{self.display_name} rejected the API key (HTTP {resp.status_code})")
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, list):
            raise ValueError(f"{self.display_name} returned an unexpected calendar response")
        items, seen = [], set()
        for raw in payload:
            item = self._normalise(raw)
            if item and item["external_key"] not in seen:
                seen.add(item["external_key"])
                items.append(item)
        return items


class SonarrAdapter(_ArrAdapter):
    id = "sonarr_api"
    display_name = "Sonarr"
    _params = {"includeSeries": "true", "includeEpisodeFile": "true"}
    _normalise = staticmethod(sonarr_item)


class RadarrAdapter(_ArrAdapter):
    id = "radarr_api"
    display_name = "Radarr"
    _normalise = staticmethod(radarr_item)
