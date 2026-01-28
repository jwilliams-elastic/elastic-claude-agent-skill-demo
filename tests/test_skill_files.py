"""Tests for skill file storage and retrieval."""

import pytest


def test_all_skill_files_indexed(es_client, files_index_name):
    """Verify all skill files are stored in Elasticsearch."""
    expected_files = {
        'verify-expense-policy': ['SKILL.md', 'policy_check.py', 'allowance_table.json'],
        'adjudicate-storm-claim': ['SKILL.md', 'adjudicator.py', 'risk_matrix.csv'],
        'validate-sample-viability': ['SKILL.md', 'viability_check.py', 'biomarker_constraints.json']
    }

    for skill_id, expected in expected_files.items():
        response = es_client.search(
            index=files_index_name,
            body={"query": {"term": {"skill_id": skill_id}}}
        )

        actual_files = [hit['_source']['file_name'] for hit in response['hits']['hits']]

        for file_name in expected:
            assert file_name in actual_files, f"Missing file: {skill_id}/{file_name}"


def test_file_content_not_empty(es_client, files_index_name):
    """Verify file content is properly stored."""
    response = es_client.search(
        index=files_index_name,
        body={"query": {"match_all": {}}, "size": 100}
    )

    for hit in response['hits']['hits']:
        file_doc = hit['_source']
        assert file_doc['file_content'], f"Empty content for {file_doc['skill_id']}/{file_doc['file_name']}"


def test_pycache_not_indexed(es_client, files_index_name):
    """Verify __pycache__ files are NOT indexed."""
    response = es_client.search(
        index=files_index_name,
        body={
            "query": {
                "wildcard": {"file_name": "*.pyc"}
            }
        }
    )

    assert response['hits']['total']['value'] == 0, "Found .pyc files in index"


def test_total_file_count(es_client, files_index_name):
    """Verify total file count matches expected (9 files total)."""
    response = es_client.count(index=files_index_name)
    assert response['count'] == 9, f"Expected 9 files total, found {response['count']}"


def test_file_has_required_fields(es_client, files_index_name):
    """Verify all file documents have required fields."""
    required_fields = ['skill_id', 'file_name', 'file_path', 'file_type', 'file_content', 'file_size_bytes', 'created_at']

    response = es_client.search(
        index=files_index_name,
        body={"query": {"match_all": {}}, "size": 100}
    )

    for hit in response['hits']['hits']:
        file_doc = hit['_source']
        for field in required_fields:
            assert field in file_doc, f"Missing field '{field}' in document {hit['_id']}"


def test_file_types_correct(es_client, files_index_name):
    """Verify file types are correctly identified."""
    expected_types = {
        'SKILL.md': 'md',
        'policy_check.py': 'py',
        'adjudicator.py': 'py',
        'viability_check.py': 'py',
        'allowance_table.json': 'json',
        'biomarker_constraints.json': 'json',
        'risk_matrix.csv': 'csv'
    }

    response = es_client.search(
        index=files_index_name,
        body={"query": {"match_all": {}}, "size": 100}
    )

    for hit in response['hits']['hits']:
        file_doc = hit['_source']
        file_name = file_doc['file_name']
        if file_name in expected_types:
            assert file_doc['file_type'] == expected_types[file_name], \
                f"Wrong file type for {file_name}: expected {expected_types[file_name]}, got {file_doc['file_type']}"


def test_get_skill_by_id_returns_files(get_skill_by_id):
    """Verify get_skill_by_id fixture returns files object."""
    skill = get_skill_by_id("verify-expense-policy")

    assert 'files' in skill, "Skill document missing 'files' field"
    assert 'SKILL.md' in skill['files'], "Missing SKILL.md in files"
    assert 'policy_check.py' in skill['files'], "Missing policy_check.py in files"
    assert 'allowance_table.json' in skill['files'], "Missing allowance_table.json in files"


def test_skill_markdown_backward_compatibility(get_skill_by_id):
    """Verify skill_markdown field is populated for backward compatibility."""
    skill = get_skill_by_id("verify-expense-policy")

    assert 'skill_markdown' in skill, "Skill document missing 'skill_markdown' field"
    assert skill['skill_markdown'] == skill['files']['SKILL.md'], \
        "skill_markdown should match SKILL.md file content"
