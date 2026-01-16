#!/usr/bin/env python3
"""
Test ES|QL queries for Agent Builder tools.

This script tests ES|QL queries against the Elasticsearch serverless instance
to validate they work correctly before registering as Agent Builder tools.

Usage:
    uv run scripts/test_esql_queries.py --query search_skills --params '{"query": "expense policy", "limit": 5}'
    uv run scripts/test_esql_queries.py --query get_skill_by_id --params '{"skill_id": "verify-expense-policy"}'
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


def load_credentials() -> tuple[str, str]:
    """Load Elasticsearch credentials from .env file."""
    load_dotenv()

    search_url = os.getenv('ELASTIC_SEARCH_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not search_url:
        raise ValueError("ELASTIC_SEARCH_URL not found in .env file")
    if not api_key:
        raise ValueError("ELASTIC_API_KEY not found in .env file")

    return search_url, api_key


def create_es_client(search_url: str, api_key: str) -> Elasticsearch:
    """Create and verify Elasticsearch client connection."""
    es = Elasticsearch(
        hosts=[search_url],
        api_key=api_key,
        verify_certs=True
    )

    if not es.ping():
        raise ConnectionError(f"Failed to connect to Elasticsearch at {search_url}")

    return es


def load_esql_query(query_name: str) -> str:
    """Load ES|QL query from file."""
    query_file = Path(__file__).parent.parent / 'agent_builder' / 'queries' / f'{query_name}.esql'

    if not query_file.exists():
        raise FileNotFoundError(f"Query file not found: {query_file}")

    return query_file.read_text().strip()


def execute_esql_query(
    es: Elasticsearch,
    query: str,
    params: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Execute ES|QL query with parameters.

    Args:
        es: Elasticsearch client
        query: ES|QL query string with parameter placeholders
        params: Dictionary of parameter values

    Returns:
        List of result rows
    """
    try:
        # ES|QL API expects params as a list of values in order they appear in query
        # For now, we'll substitute parameters directly in the query
        # This is a workaround - Agent Builder will handle params properly
        query_with_params = query
        for key, value in params.items():
            placeholder = f"?{key}"
            if isinstance(value, list):
                # For array values, format as ES|QL array
                if len(value) > 0 and isinstance(value[0], str):
                    array_str = ', '.join([f'"{v}"' for v in value])
                else:
                    array_str = ', '.join([str(v) for v in value])
                query_with_params = query_with_params.replace(placeholder, f'({array_str})')
            elif isinstance(value, str):
                # For string values, wrap in quotes
                query_with_params = query_with_params.replace(placeholder, f'"{value}"')
            else:
                # For numeric values, use as is
                query_with_params = query_with_params.replace(placeholder, str(value))

        response = es.esql.query(query=query_with_params)

        # Convert ObjectApiResponse to dict if needed
        if hasattr(response, 'body'):
            response_data = response.body
        elif hasattr(response, '__dict__'):
            response_data = dict(response)
        else:
            response_data = response

        # Debug: print response structure
        print(f"DEBUG: Response type: {type(response_data)}")
        if isinstance(response_data, dict):
            print(f"DEBUG: Response keys: {response_data.keys()}")
            print(f"DEBUG: Columns: {len(response_data.get('columns', []))}")
            print(f"DEBUG: Values: {len(response_data.get('values', []))}")

        # Parse response - the response format varies
        # Check if it's in columnar format
        if isinstance(response_data, dict):
            if 'columns' in response_data and 'values' in response_data:
                columns = [col['name'] for col in response_data['columns']]
                results = []
                for row in response_data['values']:
                    result = dict(zip(columns, row))
                    results.append(result)
                return results
            elif 'values' in response_data:
                # Simple values format
                return response_data['values']

        # If response is a list, return as is
        if isinstance(response_data, list):
            return response_data

        return []

    except Exception as e:
        raise Exception(f"ES|QL query failed: {str(e)}")


def format_results(results: List[Dict[str, Any]], query_name: str) -> str:
    """Format query results for console output."""
    if not results:
        return f"\nNo results found for query: '{query_name}'\n"

    output = [f"\n{'='*80}"]
    output.append(f"ES|QL Query Results: '{query_name}'")
    output.append(f"Found {len(results)} result(s)")
    output.append(f"{'='*80}\n")

    for idx, result in enumerate(results, 1):
        output.append(f"Result #{idx}")
        output.append(f"{'-'*80}")
        for key, value in result.items():
            if isinstance(value, (list, dict)):
                output.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                output.append(f"{key}: {value}")
        output.append("")

    return "\n".join(output)


def main():
    """Main entry point for ES|QL query testing."""
    parser = argparse.ArgumentParser(
        description='Test ES|QL queries for Agent Builder tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query search_skills --params '{"query": "expense policy", "limit": 5}'
  %(prog)s --query get_skill_by_id --params '{"skill_id": "verify-expense-policy"}'
  %(prog)s --query list_skills_by_domain --params '{"domain": "finance"}'
        """
    )

    parser.add_argument(
        '--query',
        required=True,
        help='Name of the ES|QL query file (without .esql extension)'
    )

    parser.add_argument(
        '--params',
        required=True,
        help='JSON string of query parameters'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print the ES|QL query before execution'
    )

    args = parser.parse_args()

    try:
        # Parse parameters
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in --params: {e}")

        # Load credentials
        print("Loading credentials from .env file...")
        search_url, api_key = load_credentials()
        print(f"✓ Credentials loaded")

        # Create Elasticsearch client
        print(f"Connecting to Elasticsearch at {search_url}...")
        es = create_es_client(search_url, api_key)
        print(f"✓ Connected successfully")

        # Load ES|QL query
        print(f"Loading ES|QL query: {args.query}...")
        query = load_esql_query(args.query)
        print(f"✓ Query loaded")

        if args.verbose:
            print(f"\nES|QL Query:")
            print(f"{'-'*80}")
            print(query)
            print(f"{'-'*80}\n")
            print(f"Parameters: {json.dumps(params, indent=2)}\n")

        # Execute query
        print(f"Executing ES|QL query...")
        results = execute_esql_query(es, query, params)
        print(f"✓ Query executed successfully")

        # Display results
        print(format_results(results, args.query))

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        return 1

    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}", file=sys.stderr)
        return 1

    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
