#!/usr/bin/env python3
"""
Functional search test script for Elasticsearch semantic search.

This script connects to an Elasticsearch serverless instance and performs
semantic search queries using the semantic_text field with automatic inference.

Usage:
    uv run scripts/search_test.py --query "expense policy approval" --domain finance --limit 5
    uv run scripts/search_test.py --query "storm damage claims" --domain insurance
    uv run scripts/search_test.py --query "sample viability" --domain life_sciences
"""

import argparse
import os
import sys
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


def load_credentials() -> tuple[str, str]:
    """
    Load Elasticsearch credentials from .env file.

    Returns:
        Tuple of (search_url, api_key)

    Raises:
        ValueError: If required credentials are missing
    """
    load_dotenv()

    search_url = os.getenv('ELASTIC_SEARCH_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not search_url:
        raise ValueError(
            "ELASTIC_SEARCH_URL not found in .env file. "
            "Please add: ELASTIC_SEARCH_URL=https://your-deployment.es.region.cloud.es.io"
        )

    if not api_key:
        raise ValueError(
            "ELASTIC_API_KEY not found in .env file. "
            "Please add: ELASTIC_API_KEY=your_api_key_here"
        )

    return search_url, api_key


def create_es_client(search_url: str, api_key: str) -> Elasticsearch:
    """
    Create and verify Elasticsearch client connection.

    Args:
        search_url: Elasticsearch endpoint URL
        api_key: API key for authentication

    Returns:
        Connected Elasticsearch client

    Raises:
        ConnectionError: If connection fails
    """
    es = Elasticsearch(
        hosts=[search_url],
        api_key=api_key,
        verify_certs=True
    )

    # Verify connection
    if not es.ping():
        raise ConnectionError(
            f"Failed to connect to Elasticsearch at {search_url}. "
            "Please verify your credentials and network connection."
        )

    return es


def build_search_query(
    query: str,
    domain: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Build Elasticsearch query with semantic search and optional filters.

    Args:
        query: Search query string for semantic search
        domain: Optional domain filter (finance, insurance, life_sciences)
        tags: Optional list of tags to filter by
        limit: Maximum number of results to return

    Returns:
        Elasticsearch query DSL
    """
    # Base semantic search query on semantic_content field
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
        },
        "_source": [
            "skill_id",
            "name",
            "domain",
            "description",
            "short_description",
            "tags",
            "author",
            "version"
        ]
    }

    # Add domain filter if specified
    if domain:
        search_body["query"]["bool"].setdefault("filter", []).append({
            "term": {"domain": domain}
        })

    # Add tag filters if specified
    if tags:
        for tag in tags:
            search_body["query"]["bool"].setdefault("filter", []).append({
                "term": {"tags": tag}
            })

    return search_body


def execute_search(
    es: Elasticsearch,
    index_name: str,
    query: str,
    domain: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Execute semantic search query and return formatted results.

    Args:
        es: Elasticsearch client
        index_name: Name of the index to search
        query: Search query string
        domain: Optional domain filter
        tags: Optional tag filters
        limit: Maximum number of results

    Returns:
        List of search result dictionaries with score and source data

    Raises:
        Exception: If search query fails
    """
    search_body = build_search_query(query, domain, tags, limit)

    try:
        response = es.search(index=index_name, body=search_body)

        results = []
        for hit in response['hits']['hits']:
            results.append({
                'score': hit['_score'],
                'skill_id': hit['_source'].get('skill_id'),
                'name': hit['_source'].get('name'),
                'domain': hit['_source'].get('domain'),
                'description': hit['_source'].get('description'),
                'short_description': hit['_source'].get('short_description'),
                'tags': hit['_source'].get('tags', []),
                'author': hit['_source'].get('author'),
                'version': hit['_source'].get('version')
            })

        return results

    except Exception as e:
        raise Exception(f"Search query failed: {str(e)}")


def format_results(results: List[Dict[str, Any]], query: str) -> str:
    """
    Format search results for console output.

    Args:
        results: List of search result dictionaries
        query: Original search query

    Returns:
        Formatted string for display
    """
    if not results:
        return f"\nNo results found for query: '{query}'\n"

    output = [f"\n{'='*80}"]
    output.append(f"Search Results for: '{query}'")
    output.append(f"Found {len(results)} result(s)")
    output.append(f"{'='*80}\n")

    for idx, result in enumerate(results, 1):
        output.append(f"Result #{idx} (Relevance Score: {result['score']:.4f})")
        output.append(f"{'-'*80}")
        output.append(f"Skill ID: {result['skill_id']}")
        output.append(f"Name: {result['name']}")
        output.append(f"Domain: {result['domain']}")
        output.append(f"Author: {result.get('author', 'N/A')}")
        output.append(f"Version: {result.get('version', 'N/A')}")
        output.append(f"Tags: {', '.join(result['tags']) if result['tags'] else 'None'}")
        output.append(f"\nDescription:")
        output.append(f"{result.get('short_description') or result.get('description', 'N/A')}")
        output.append(f"\n")

    return "\n".join(output)


def main():
    """Main entry point for search test script."""
    parser = argparse.ArgumentParser(
        description='Test semantic search against Elasticsearch serverless instance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "expense policy approval rules" --domain finance
  %(prog)s --query "storm damage claim" --domain insurance --limit 3
  %(prog)s --query "sample viability validation" --domain life_sciences
  %(prog)s --query "compliance" --limit 10
        """
    )

    parser.add_argument(
        '--query',
        required=True,
        help='Search query string for semantic search'
    )

    parser.add_argument(
        '--domain',
        choices=['finance', 'insurance', 'life_sciences'],
        help='Filter results by domain (finance, insurance, life_sciences)'
    )

    parser.add_argument(
        '--tags',
        nargs='+',
        help='Filter results by tags (space-separated list)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Maximum number of results to return (default: 5)'
    )

    parser.add_argument(
        '--index',
        default='agent_skills',
        help='Index name to search (default: agent_skills)'
    )

    args = parser.parse_args()

    try:
        # Load credentials
        print("Loading credentials from .env file...")
        search_url, api_key = load_credentials()
        print(f"✓ Credentials loaded")

        # Create Elasticsearch client
        print(f"Connecting to Elasticsearch at {search_url}...")
        es = create_es_client(search_url, api_key)
        print(f"✓ Connected successfully")

        # Execute search
        print(f"Executing semantic search on index '{args.index}'...")
        results = execute_search(
            es=es,
            index_name=args.index,
            query=args.query,
            domain=args.domain,
            tags=args.tags,
            limit=args.limit
        )
        print(f"✓ Search completed")

        # Display results
        print(format_results(results, args.query))

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease check your .env file and ensure all required variables are set.", file=sys.stderr)
        return 1

    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}", file=sys.stderr)
        print("\nTroubleshooting steps:", file=sys.stderr)
        print("1. Verify ELASTIC_SEARCH_URL is correct", file=sys.stderr)
        print("2. Verify ELASTIC_API_KEY is valid", file=sys.stderr)
        print("3. Check network connectivity", file=sys.stderr)
        print("4. Verify Elasticsearch instance is running", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
