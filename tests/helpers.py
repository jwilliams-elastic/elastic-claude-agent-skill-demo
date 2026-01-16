"""
Helper utility functions for end-to-end tests.

This module provides standalone utility functions that can be used
across multiple test files. Most functionality is also available
via pytest fixtures in conftest.py.
"""

from typing import Dict, Any, List
from elasticsearch import Elasticsearch


def search_skills(
    es_client: Elasticsearch,
    query: str,
    domain: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Execute semantic search query against Elasticsearch.

    Args:
        es_client: Elasticsearch client instance
        query: Search query string
        domain: Optional domain filter (finance, insurance, life_sciences)
        limit: Maximum number of results (default: 10)

    Returns:
        List of search result dictionaries with score and source

    Example:
        results = search_skills(es, "expense policy", domain="finance")
    """
    search_body = {
        "size": limit,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "semantic_content": {
                                "query": query
                            }
                        }
                    }
                ]
            }
        }
    }

    if domain:
        search_body["query"]["bool"].setdefault("filter", []).append({
            "term": {"domain": domain}
        })

    response = es_client.search(index="agent_skills", body=search_body)

    results = []
    for hit in response['hits']['hits']:
        results.append({
            'score': hit['_score'],
            'id': hit['_id'],
            'source': hit['_source']
        })

    return results


def get_skill_by_id(
    es_client: Elasticsearch,
    skill_id: str
) -> Dict[str, Any]:
    """
    Retrieve skill document by skill_id.

    Args:
        es_client: Elasticsearch client instance
        skill_id: The skill_id to retrieve

    Returns:
        Skill document dictionary

    Raises:
        Exception: If skill not found

    Example:
        skill = get_skill_by_id(es, "verify-expense-policy")
    """
    response = es_client.search(
        index="agent_skills",
        body={
            "query": {
                "term": {
                    "skill_id": skill_id
                }
            },
            "size": 1
        }
    )

    if response['hits']['total']['value'] == 0:
        raise Exception(f"Skill not found: {skill_id}")

    return response['hits']['hits'][0]['_source']


def execute_skill_logic(
    skill_content: Dict[str, Any],
    input_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Parse and execute skill Python code with input parameters.

    Args:
        skill_content: Skill document containing skill_markdown field
        input_params: Input parameters dictionary for the skill

    Returns:
        Execution result dictionary

    Raises:
        Exception: If execution fails or code is malformed

    Example:
        result = execute_skill_logic(skill, {"amount": 850, "category": "Team_Dinner"})
    """
    skill_markdown = skill_content.get('skill_markdown', '')

    # Find Python code block
    code_start = skill_markdown.find('```python')
    if code_start == -1:
        raise Exception("No Python code block found in skill")

    code_start += len('```python\n')
    code_end = skill_markdown.find('```', code_start)

    if code_end == -1:
        raise Exception("Malformed Python code block in skill")

    python_code = skill_markdown[code_start:code_end].strip()

    # Create execution environment
    exec_globals = {}
    exec_locals = {'input_data': input_params}

    # Execute the skill code
    try:
        exec(python_code, exec_globals, exec_locals)
    except Exception as e:
        raise Exception(f"Skill execution failed: {str(e)}")

    # Return the result
    if 'result' not in exec_locals:
        raise Exception("Skill did not produce a 'result' variable")

    return exec_locals['result']


def format_test_results(
    results: Dict[str, Any],
    test_name: str
) -> str:
    """
    Format test results for console or report output.

    Args:
        results: Test results dictionary
        test_name: Name of the test

    Returns:
        Formatted string for display

    Example:
        formatted = format_test_results({"status": "PASSED"}, "Expense Policy Test")
    """
    output = [f"\n{'='*80}"]
    output.append(f"Test Results: {test_name}")
    output.append(f"{'='*80}\n")

    for key, value in results.items():
        if isinstance(value, dict):
            output.append(f"{key}:")
            for sub_key, sub_value in value.items():
                output.append(f"  {sub_key}: {sub_value}")
        elif isinstance(value, list):
            output.append(f"{key}:")
            for item in value:
                output.append(f"  - {item}")
        else:
            output.append(f"{key}: {value}")

    return "\n".join(output)


def validate_skill_structure(skill: Dict[str, Any]) -> bool:
    """
    Validate that a skill document has required fields.

    Args:
        skill: Skill document dictionary

    Returns:
        True if valid, False otherwise

    Example:
        is_valid = validate_skill_structure(skill)
    """
    required_fields = [
        'skill_id',
        'name',
        'domain',
        'description',
        'skill_markdown'
    ]

    for field in required_fields:
        if field not in skill:
            return False

    return True


def extract_violations(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract violations from skill execution result.

    Handles different result formats and returns normalized violation list.

    Args:
        result: Skill execution result dictionary

    Returns:
        List of violation dictionaries

    Example:
        violations = extract_violations(result)
    """
    violations = []

    # Check common violation field names
    if 'violations' in result:
        violations.extend(result['violations'])

    if 'errors' in result:
        violations.extend(result['errors'])

    if 'warnings' in result:
        # Include warnings as violations with lower severity
        warnings = result['warnings']
        for warning in warnings:
            if isinstance(warning, dict):
                warning['severity'] = 'WARNING'
                violations.append(warning)
            else:
                violations.append({
                    'type': 'WARNING',
                    'message': str(warning),
                    'severity': 'WARNING'
                })

    return violations


def is_approval_status(result: Dict[str, Any]) -> bool:
    """
    Determine if result indicates approval/acceptance.

    Checks various status fields and returns normalized boolean.

    Args:
        result: Skill execution result dictionary

    Returns:
        True if approved/accepted, False otherwise

    Example:
        approved = is_approval_status(result)
    """
    # Check common approval field names
    if result.get('approved') is True:
        return True

    if result.get('viable') is True:
        return True

    status = result.get('overall_status') or result.get('status')
    if status:
        approval_statuses = ['APPROVED', 'ACCEPTED', 'VIABLE', 'PASS']
        if str(status).upper() in approval_statuses:
            return True

    return False
