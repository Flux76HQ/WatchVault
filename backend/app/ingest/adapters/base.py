"""Provider-adapter pattern.

Every streaming source is a small adapter implementing a common interface so
new providers can be added without touching core logic:

    import_file(content, filename) -> list[NormalizedEvent]   # CSV/JSON sources
    fetch_history(config, cursor)  -> (list[NormalizedEvent], new_cursor)  # API
"""
from __future__ import annotations

from ..models import NormalizedEvent


class SourceAdapter:
    id: str = "base"
    ingest_type: str = "csv"            # 'csv' | 'json' | 'api'
    display_name: str = "Base"
    # Per-adapter connection config schema (API adapters). Each field:
    #   {"key", "label", "type": 'text'|'password'|'url', "placeholder", "required", "help"}
    config_fields: list[dict] = []

    def import_file(self, content: bytes, filename: str) -> list[NormalizedEvent]:
        raise NotImplementedError(f"{self.id} does not support file import")

    def fetch_history(self, config: dict, cursor: dict) -> tuple[list[NormalizedEvent], dict]:
        raise NotImplementedError(f"{self.id} does not support API sync")

    def list_libraries(self, config: dict) -> list[dict]:
        """Discover selectable libraries for this connection.

        Returns ``[{"id": str, "name": str, "type": str}]``. Adapters whose
        source has no concept of libraries can leave the default (none).
        """
        return []

    def library_prune_spec(self, config: dict) -> tuple[str, set[str]] | None:
        """Describe how to prune watch events to the selected library subset.

        Returns ``(raw_key, selected_ids)`` where ``raw_key`` is the JSON key each
        event records its source library under (in ``raw``) and ``selected_ids`` is
        the set of libraries to keep. Returns ``None`` when no subset is selected
        (i.e. all libraries are kept, nothing to prune). Adapters without libraries
        keep the default (no pruning).
        """
        return None

