def build_case_evidence_index_schema(index_name: str = "case-evidence", vector_dimensions: int = 1536) -> dict:
    return {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "case_id", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "document_id", "type": "Edm.String", "filterable": True},
            {"name": "chunk_id", "type": "Edm.String", "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "source_file", "type": "Edm.String", "filterable": True},
            {"name": "source_path", "type": "Edm.String"},
            {"name": "document_type", "type": "Edm.String", "filterable": True},
            {"name": "evidence_type", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "evidence_source", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "created_by", "type": "Edm.String", "filterable": True},
            {"name": "tags", "type": "Collection(Edm.String)", "filterable": True, "facetable": True},
            {"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": True, "dimensions": vector_dimensions, "vectorSearchProfile": "default-vector-profile"},
            {"name": "created_at", "type": "Edm.String", "filterable": True, "sortable": True},
            {"name": "metadata_json", "type": "Edm.String"},
        ],
    }
