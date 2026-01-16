"""
pytest configuration and fixtures for end-to-end testing.

This module provides fixtures for:
- Elasticsearch client initialization
- Test data setup/teardown
- Skill execution helpers
"""

import os
import pytest
from typing import Dict, Any
from dotenv import load_dotenv
from elasticsearch import Elasticsearch


@pytest.fixture(scope="session")
def es_credentials():
    """
    Load Elasticsearch credentials from .env file.

    Returns:
        Dict with 'url' and 'api_key' keys

    Raises:
        ValueError: If required credentials are missing
    """
    load_dotenv()

    url = os.getenv('ELASTIC_SEARCH_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not url:
        raise ValueError(
            "ELASTIC_SEARCH_URL not found in .env file. "
            "Required for running tests against Elasticsearch."
        )

    if not api_key:
        raise ValueError(
            "ELASTIC_API_KEY not found in .env file. "
            "Required for authentication."
        )

    return {
        'url': url,
        'api_key': api_key
    }


@pytest.fixture(scope="session")
def es_client(es_credentials):
    """
    Create and verify Elasticsearch client connection.

    Args:
        es_credentials: Fixture providing credentials

    Returns:
        Connected Elasticsearch client instance

    Raises:
        ConnectionError: If connection fails
    """
    client = Elasticsearch(
        hosts=[es_credentials['url']],
        api_key=es_credentials['api_key'],
        verify_certs=True
    )

    # Verify connection
    if not client.ping():
        raise ConnectionError(
            f"Failed to connect to Elasticsearch at {es_credentials['url']}"
        )

    yield client

    # Cleanup: client will be closed automatically


@pytest.fixture(scope="session")
def index_name():
    """
    Return the name of the test index.

    Returns:
        String name of the Elasticsearch index
    """
    return "agent_skills"


@pytest.fixture
def search_skills(es_client, index_name):
    """
    Factory fixture for executing semantic searches.

    Args:
        es_client: Elasticsearch client fixture
        index_name: Index name fixture

    Returns:
        Function that executes search queries

    Example:
        results = search_skills("expense policy", domain="finance")
    """
    def _search(query: str, domain: str = None, limit: int = 10) -> list:
        """
        Execute semantic search query.

        Args:
            query: Search query string
            domain: Optional domain filter
            limit: Maximum number of results

        Returns:
            List of search result dictionaries
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

        # Add domain filter if specified
        if domain:
            search_body["query"]["bool"].setdefault("filter", []).append({
                "term": {"domain": domain}
            })

        response = es_client.search(index=index_name, body=search_body)

        results = []
        for hit in response['hits']['hits']:
            results.append({
                'score': hit['_score'],
                'id': hit['_id'],
                'source': hit['_source']
            })

        return results

    return _search


@pytest.fixture
def get_skill_by_id(es_client, index_name):
    """
    Factory fixture for retrieving skills by ID.

    Args:
        es_client: Elasticsearch client fixture
        index_name: Index name fixture

    Returns:
        Function that retrieves skill documents by ID

    Example:
        skill = get_skill_by_id("verify-expense-policy")
    """
    def _get(skill_id: str) -> Dict[str, Any]:
        """
        Retrieve skill document by ID.

        Args:
            skill_id: The skill_id to retrieve

        Returns:
            Skill document dictionary

        Raises:
            Exception: If skill not found
        """
        # Search for the skill by skill_id field
        response = es_client.search(
            index=index_name,
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

    return _get


@pytest.fixture
def execute_skill_logic():
    """
    Factory fixture for executing skill Python code.

    Returns:
        Function that parses and executes skill code with input parameters

    Example:
        result = execute_skill_logic(skill_content, {"amount": 850})
    """
    def _execute(skill_content: Dict[str, Any], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and execute skill Python code.

        Args:
            skill_content: Skill document containing skill_markdown field
            input_params: Input parameters for the skill

        Returns:
            Execution result dictionary

        Raises:
            Exception: If execution fails
        """
        import sys
        from pathlib import Path

        # Extract Python code from skill_markdown
        skill_markdown = skill_content.get('skill_markdown', '')

        # Prefer Test Execution section over Usage Example
        test_execution_pos = skill_markdown.find('## Test Execution')

        if test_execution_pos != -1:
            # Found Test Execution section, find the code block after it
            code_start = skill_markdown.find('```python', test_execution_pos)
            if code_start == -1:
                raise Exception("Test Execution section found but no Python code block")
            code_start += len('```python\n')
        else:
            # Fall back to first Python code block
            code_start = skill_markdown.find('```python')
            if code_start == -1:
                raise Exception("No Python code block found in skill")
            code_start += len('```python\n')

        code_end = skill_markdown.find('```', code_start)

        if code_end == -1:
            raise Exception("Malformed Python code block in skill")

        python_code = skill_markdown[code_start:code_end].strip()

        # Get skill_id and build path to skill directory
        skill_id = skill_content.get('skill_id')
        if not skill_id:
            raise Exception("Skill content missing skill_id")

        # Build path to skill directory (assuming project structure)
        project_root = Path(__file__).parent.parent
        skill_dir = project_root / "sample_skills" / skill_id

        if not skill_dir.exists():
            raise Exception(f"Skill directory not found: {skill_dir}")

        # Add skill directory to Python path temporarily
        skill_dir_str = str(skill_dir)
        sys.path.insert(0, skill_dir_str)

        try:
            # Create execution environment
            exec_globals = {}
            exec_locals = {'input_data': input_params}

            # Execute the skill code
            try:
                exec(python_code, exec_globals, exec_locals)
            except Exception as e:
                raise Exception(f"Skill execution failed: {str(e)}")

            # Return the result (assumes skill sets 'result' variable)
            if 'result' not in exec_locals:
                raise Exception("Skill did not produce a 'result' variable")

            return exec_locals['result']
        finally:
            # Clean up: remove skill directory from path
            if skill_dir_str in sys.path:
                sys.path.remove(skill_dir_str)

    return _execute


@pytest.fixture
def format_test_results():
    """
    Factory fixture for formatting test results.

    Returns:
        Function that formats results for reporting

    Example:
        formatted = format_test_results(results, "Expense Policy Test")
    """
    def _format(results: Dict[str, Any], test_name: str) -> str:
        """
        Format test results for reporting.

        Args:
            results: Test results dictionary
            test_name: Name of the test

        Returns:
            Formatted string for display
        """
        output = [f"\n{'='*80}"]
        output.append(f"Test Results: {test_name}")
        output.append(f"{'='*80}\n")

        for key, value in results.items():
            output.append(f"{key}: {value}")

        return "\n".join(output)

    return _format
