#!/usr/bin/env python3
"""
Validation script to check if documents are indexed with semantic_content field.
Part of Task 1.3: Update Document Structure Validation
"""

import os
import sys
from pathlib import Path
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


def validate_indexing():
    """Validate that documents are indexed with semantic_content field."""

    # Get configuration from environment
    es_url = os.getenv("ELASTIC_SEARCH_URL")
    api_key = os.getenv("ELASTIC_API_KEY")

    if not es_url or not api_key:
        print("Error: ELASTIC_SEARCH_URL and ELASTIC_API_KEY must be set in environment.")
        sys.exit(1)

    # Initialize Elasticsearch client
    print("Connecting to Elasticsearch...")
    es = Elasticsearch(
        hosts=[es_url],
        api_key=api_key
    )

    # Verify connection
    if not es.ping():
        print("Error: Could not connect to Elasticsearch.")
        sys.exit(1)

    print("✓ Connected successfully.\n")

    index_name = "agent_skills"

    # Check if index exists
    if not es.indices.exists(index=index_name):
        print(f"✗ Index '{index_name}' does not exist.")
        print("Run 'uv run scripts/ingest_skills.py' first to create and populate the index.")
        sys.exit(1)

    print(f"✓ Index '{index_name}' exists.\n")

    # Get index mapping to verify semantic_text configuration
    print("Checking index mapping...")
    mapping = es.indices.get_mapping(index=index_name)

    if index_name in mapping:
        properties = mapping[index_name]['mappings'].get('properties', {})

        if 'semantic_content' in properties:
            semantic_field = properties['semantic_content']
            print(f"✓ semantic_content field exists:")
            print(f"  Type: {semantic_field.get('type')}")
            if 'inference_id' in semantic_field:
                print(f"  Inference ID: {semantic_field['inference_id']}")
        else:
            print("✗ semantic_content field not found in mapping")
            return False

    # Check document count
    count_result = es.count(index=index_name)
    doc_count = count_result['count']
    print(f"\n✓ Found {doc_count} documents in index.\n")

    if doc_count == 0:
        print("✗ No documents found. Run 'uv run scripts/ingest_skills.py' to index skills.")
        sys.exit(1)

    # Query a sample document
    print("Retrieving sample document to verify field structure...")
    search_result = es.search(
        index=index_name,
        size=1,
        query={"match_all": {}}
    )

    if search_result['hits']['total']['value'] > 0:
        doc = search_result['hits']['hits'][0]
        doc_id = doc['_id']
        doc_source = doc['_source']

        print(f"\n✓ Sample Document (ID: {doc_id}):")
        print(f"  skill_id: {doc_source.get('skill_id')}")
        print(f"  name: {doc_source.get('name')}")
        print(f"  domain: {doc_source.get('domain')}")
        print(f"  tags: {doc_source.get('tags')}")

        # Check for copy_to source fields
        required_fields = ['skill_id', 'name', 'description', 'short_description',
                          'domain', 'tags', 'author']

        print("\n  Checking required fields that map to semantic_content:")
        all_present = True
        for field in required_fields:
            if field in doc_source:
                value = doc_source[field]
                preview = str(value)[:50] if value else "(empty)"
                print(f"    ✓ {field}: {preview}...")
            else:
                print(f"    ✗ {field}: MISSING")
                all_present = False

        # Check if semantic_content is populated
        # Note: semantic_content is a semantic_text field and may not appear in _source
        # We need to check if the field exists in the mapping and if documents can be searched
        print("\n  Testing semantic search capability...")
        test_search = es.search(
            index=index_name,
            size=1,
            query={
                "match": {
                    "semantic_content": "expense policy"
                }
            }
        )

        if test_search['hits']['total']['value'] > 0:
            print("    ✓ Semantic search is working (semantic_content is functional)")
        else:
            print("    ⚠ Semantic search returned no results (may need time to process)")

        if all_present:
            print("\n✅ VALIDATION PASSED: All required fields are present and semantic search is configured.")
            return True
        else:
            print("\n✗ VALIDATION FAILED: Some required fields are missing.")
            return False
    else:
        print("✗ Could not retrieve sample document.")
        return False


if __name__ == "__main__":
    success = validate_indexing()
    sys.exit(0 if success else 1)
