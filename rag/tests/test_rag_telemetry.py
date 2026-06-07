from agents.observability.rag_telemetry import track_rag_event


def test_rag_telemetry_records_event_without_azure() -> None:
    track_rag_event("RAG_RETRIEVAL_COMPLETED", {"retrieval_mode": "local", "result_count": 1}, {"retrieval_latency_ms": 1.0})
