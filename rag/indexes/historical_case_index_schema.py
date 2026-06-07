def build_historical_case_index_schema(index_name: str = "historical-fraud-cases", vector_dimensions: int = 1536) -> dict:
    fields = [
        "id", "document_id", "chunk_id", "title", "content", "source_file", "source_path",
        "document_type", "historical_case_id", "case_type", "outcome", "channel",
        "amount_band", "customer_segment", "created_at", "metadata_json"
    ]
    schema_fields = []
    for field in fields:
        schema_fields.append({
            "name": field,
            "type": "Edm.String",
            "key": field == "id",
            "searchable": field in {"title", "content"},
            "filterable": field not in {"content", "source_path", "metadata_json"},
            "facetable": field in {"case_type", "outcome", "channel", "amount_band", "customer_segment"},
            "sortable": field == "created_at",
        })
    schema_fields.append({"name": "risk_indicators", "type": "Collection(Edm.String)", "filterable": True, "facetable": True})
    schema_fields.append({"name": "tags", "type": "Collection(Edm.String)", "filterable": True, "facetable": True})
    schema_fields.append({"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": True, "dimensions": vector_dimensions, "vectorSearchProfile": "default-vector-profile"})
    return {"name": index_name, "fields": schema_fields}
