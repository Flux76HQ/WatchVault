"""Ingestion package: provider adapters + normalization into the central model."""
from .models import NormalizedEvent
from .normalize import ingest_events, prune_connection_libraries, clear_connection_events

__all__ = ["NormalizedEvent", "ingest_events", "prune_connection_libraries",
           "clear_connection_events"]
