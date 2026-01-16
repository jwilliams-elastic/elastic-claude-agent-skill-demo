#!/usr/bin/env python3
"""
Test script for Elastic Agent Builder tools via MCP endpoint.

This script tests registered Agent Builder tools by invoking them through the
Elastic MCP endpoint and validating their responses.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class MCPToolTester:
    """Client for testing Agent Builder tools via MCP endpoint."""

    def __init__(self, mcp_url: str, api_key: str):
        """
        Initialize the MCP tool tester.

        Args:
            mcp_url: Elastic MCP endpoint URL (e.g., https://kibana.example.com/api/agent_builder/mcp)
            api_key: Elastic API key for authentication
        """
        self.mcp_url = mcp_url.rstrip('/')
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"ApiKey {self.api_key}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def test_tool(self, tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a tool by invoking it with parameters via JSON-RPC.

        Args:
            tool_id: Tool identifier
            params: Parameters to pass to the tool

        Returns:
            Response data from the tool execution

        Raises:
            requests.HTTPError: If the API request fails
        """
        # MCP uses JSON-RPC 2.0 protocol
        jsonrpc_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_id,
                "arguments": params
            }
        }

        try:
            response = requests.post(
                self.mcp_url,
                headers=self._get_headers(),
                json=jsonrpc_payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Extract the actual result from JSON-RPC response
            if "error" in result:
                return {"error": result["error"].get("message", "Unknown error")}

            # Parse the MCP tool result
            if "result" in result:
                content = result["result"].get("content", [])
                if content and len(content) > 0:
                    # The result is in the text field as JSON
                    text_content = content[0].get("text", "{}")
                    try:
                        return json.loads(text_content)
                    except json.JSONDecodeError:
                        return {"data": text_content}

            return result
        except requests.exceptions.RequestException as e:
            self._handle_error(e, f"testing tool '{tool_id}'")
            raise

    def _handle_error(self, error: Exception, action: str):
        """
        Handle and format API errors.

        Args:
            error: The exception that occurred
            action: Description of the action being performed
        """
        print(f"\n❌ Error {action}:", file=sys.stderr)

        if isinstance(error, requests.exceptions.HTTPError):
            print(f"   Status Code: {error.response.status_code}", file=sys.stderr)
            try:
                error_data = error.response.json()
                print(f"   Message: {json.dumps(error_data, indent=2)}", file=sys.stderr)
            except json.JSONDecodeError:
                print(f"   Response: {error.response.text}", file=sys.stderr)
        elif isinstance(error, requests.exceptions.ConnectionError):
            print(f"   Connection Error: Could not connect to {self.mcp_url}", file=sys.stderr)
            print(f"   Details: {str(error)}", file=sys.stderr)
        elif isinstance(error, requests.exceptions.Timeout):
            print(f"   Timeout: Request took longer than 30 seconds", file=sys.stderr)
        else:
            print(f"   {type(error).__name__}: {str(error)}", file=sys.stderr)


def format_results(response: Dict[str, Any], verbose: bool = False) -> str:
    """
    Format tool execution results for display.

    Args:
        response: Response from tool execution
        verbose: If True, show full response including metadata

    Returns:
        Formatted string for display
    """
    output = []

    # Check for errors in response
    if "error" in response:
        output.append("❌ Tool execution failed:")
        output.append(f"   {response['error']}")
        return "\n".join(output)

    # Extract results
    results = response.get("results", response.get("data", []))

    if not results:
        output.append("⚠️  No results returned")
        return "\n".join(output)

    # Format results based on structure
    if isinstance(results, list):
        output.append(f"✅ Found {len(results)} result(s):\n")

        for idx, result in enumerate(results, 1):
            output.append(f"Result {idx}:")
            if isinstance(result, dict):
                for key, value in result.items():
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 100 and not verbose:
                        value = value[:100] + "..."
                    output.append(f"  {key}: {value}")
            else:
                output.append(f"  {result}")
            output.append("")  # Empty line between results

    elif isinstance(results, dict):
        output.append("✅ Result:\n")
        for key, value in results.items():
            if isinstance(value, str) and len(value) > 100 and not verbose:
                value = value[:100] + "..."
            output.append(f"  {key}: {value}")

    else:
        output.append(f"✅ Result: {results}")

    # Show full response in verbose mode
    if verbose:
        output.append("\n" + "="*60)
        output.append("Full Response:")
        output.append(json.dumps(response, indent=2))

    return "\n".join(output)


def run_test_case(tester: MCPToolTester, tool_id: str, params: Dict[str, Any],
                  description: str, verbose: bool = False) -> bool:
    """
    Run a single test case.

    Args:
        tester: MCP tool tester instance
        tool_id: Tool identifier
        params: Parameters for the tool
        description: Test case description
        verbose: If True, show detailed output

    Returns:
        True if test passed, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"Tool: {tool_id}")
    print(f"Params: {json.dumps(params, indent=2)}")
    print(f"{'='*60}")

    try:
        response = tester.test_tool(tool_id, params)
        print(format_results(response, verbose))
        return True
    except requests.HTTPError:
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        return False


def run_search_skills_tests(tester: MCPToolTester, verbose: bool = False) -> int:
    """Run test cases for search_skills tool."""
    print("\n" + "="*60)
    print("Testing: search_skills")
    print("="*60)

    test_cases = [
        {
            "description": "Search for 'expense policy'",
            "params": {"query": "expense policy", "limit": 5},
            "expected": "verify-expense-policy"
        },
        {
            "description": "Search for 'storm damage'",
            "params": {"query": "storm damage", "limit": 5},
            "expected": "adjudicate-storm-claim"
        },
        {
            "description": "Search for 'sample viability'",
            "params": {"query": "sample viability", "limit": 5},
            "expected": "validate-sample-viability"
        },
        {
            "description": "Search with limit=1",
            "params": {"query": "expense", "limit": 1},
            "expected": "single result"
        }
    ]

    passed = 0
    for test_case in test_cases:
        if run_test_case(tester, "search_skills", test_case["params"],
                        test_case["description"], verbose):
            passed += 1

    return passed


def run_get_skill_by_id_tests(tester: MCPToolTester, verbose: bool = False) -> int:
    """Run test cases for get_skill_by_id tool."""
    print("\n" + "="*60)
    print("Testing: get_skill_by_id")
    print("="*60)

    test_cases = [
        {
            "description": "Get 'verify-expense-policy'",
            "params": {"skill_id": "verify-expense-policy"}
        },
        {
            "description": "Get 'adjudicate-storm-claim'",
            "params": {"skill_id": "adjudicate-storm-claim"}
        },
        {
            "description": "Get nonexistent skill",
            "params": {"skill_id": "nonexistent-skill"}
        }
    ]

    passed = 0
    for test_case in test_cases:
        if run_test_case(tester, "get_skill_by_id", test_case["params"],
                        test_case["description"], verbose):
            passed += 1

    return passed


def run_list_skills_by_domain_tests(tester: MCPToolTester, verbose: bool = False) -> int:
    """Run test cases for list_skills_by_domain tool."""
    print("\n" + "="*60)
    print("Testing: list_skills_by_domain")
    print("="*60)

    test_cases = [
        {
            "description": "List finance skills",
            "params": {"domain": "finance"}
        },
        {
            "description": "List insurance skills",
            "params": {"domain": "insurance"}
        },
        {
            "description": "List life_sciences skills",
            "params": {"domain": "life_sciences"}
        },
        {
            "description": "List nonexistent domain",
            "params": {"domain": "nonexistent"}
        }
    ]

    passed = 0
    for test_case in test_cases:
        if run_test_case(tester, "list_skills_by_domain", test_case["params"],
                        test_case["description"], verbose):
            passed += 1

    return passed


def run_get_skill_metadata_tests(tester: MCPToolTester, verbose: bool = False) -> int:
    """Run test cases for get_skill_metadata tool."""
    print("\n" + "="*60)
    print("Testing: get_skill_metadata")
    print("="*60)

    test_cases = [
        {
            "description": "Get metadata for 'verify-expense-policy'",
            "params": {"skill_id": "verify-expense-policy"}
        },
        {
            "description": "Get metadata for nonexistent skill",
            "params": {"skill_id": "nonexistent-skill"}
        }
    ]

    passed = 0
    for test_case in test_cases:
        if run_test_case(tester, "get_skill_metadata", test_case["params"],
                        test_case["description"], verbose):
            passed += 1

    return passed


def run_search_skills_by_tags_tests(tester: MCPToolTester, verbose: bool = False) -> int:
    """Run test cases for search_skills_by_tags tool."""
    print("\n" + "="*60)
    print("Testing: search_skills_by_tags")
    print("="*60)

    test_cases = [
        {
            "description": "Search for tag 'finance'",
            "params": {"tag": ".*finance.*"}
        },
        {
            "description": "Search for tag 'insurance'",
            "params": {"tag": ".*insurance.*"}
        },
        {
            "description": "Search for tag 'compliance'",
            "params": {"tag": ".*compliance.*"}
        }
    ]

    passed = 0
    for test_case in test_cases:
        if run_test_case(tester, "search_skills_by_tags", test_case["params"],
                        test_case["description"], verbose):
            passed += 1

    return passed


def run_all_tests(tester: MCPToolTester, verbose: bool = False) -> Dict[str, int]:
    """
    Run all test suites.

    Args:
        tester: MCP tool tester instance
        verbose: If True, show detailed output

    Returns:
        Dictionary with test results
    """
    results = {
        "search_skills": run_search_skills_tests(tester, verbose),
        "get_skill_by_id": run_get_skill_by_id_tests(tester, verbose),
        "list_skills_by_domain": run_list_skills_by_domain_tests(tester, verbose),
        "get_skill_metadata": run_get_skill_metadata_tests(tester, verbose),
        "search_skills_by_tags": run_search_skills_by_tags_tests(tester, verbose)
    }

    # Print summary
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)

    total_passed = 0
    for tool, passed in results.items():
        total_passed += passed
        print(f"  {tool}: {passed} passed")

    print(f"\nTotal: {total_passed} tests passed")

    return results


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(
        description='Test Elastic Agent Builder tools via MCP endpoint',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a specific tool with parameters
  %(prog)s --tool search_skills --params '{"query": "expense", "limit": 5}'

  # Run all test suites
  %(prog)s --all

  # Test a specific tool suite
  %(prog)s --test-suite search_skills

  # Show verbose output
  %(prog)s --tool get_skill_by_id --params '{"skill_id": "verify-expense-policy"}' --verbose
        """
    )

    parser.add_argument(
        '--tool',
        help='Tool ID to test'
    )

    parser.add_argument(
        '--params',
        help='JSON string with tool parameters'
    )

    parser.add_argument(
        '--test-suite',
        choices=['search_skills', 'get_skill_by_id', 'list_skills_by_domain',
                 'get_skill_metadata', 'search_skills_by_tags'],
        help='Run predefined test suite for a tool'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all test suites'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output including full responses'
    )

    args = parser.parse_args()

    # Check if at least one action is specified
    if not any([args.tool, args.test_suite, args.all]):
        parser.print_help()
        sys.exit(1)

    # Get environment variables
    mcp_url = os.getenv('ELASTIC_MCP_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not mcp_url or not api_key:
        print("❌ Error: ELASTIC_MCP_URL and ELASTIC_API_KEY environment variables must be set",
              file=sys.stderr)
        print("   Please check your .env file or set these variables manually", file=sys.stderr)
        sys.exit(1)

    tester = MCPToolTester(mcp_url, api_key)

    try:
        if args.all:
            # Run all test suites
            results = run_all_tests(tester, args.verbose)
            sys.exit(0)

        elif args.test_suite:
            # Run specific test suite
            test_functions = {
                'search_skills': run_search_skills_tests,
                'get_skill_by_id': run_get_skill_by_id_tests,
                'list_skills_by_domain': run_list_skills_by_domain_tests,
                'get_skill_metadata': run_get_skill_metadata_tests,
                'search_skills_by_tags': run_search_skills_by_tags_tests
            }

            test_func = test_functions[args.test_suite]
            passed = test_func(tester, args.verbose)

            print(f"\n✅ {passed} test(s) completed")
            sys.exit(0)

        elif args.tool:
            # Test specific tool with custom parameters
            if not args.params:
                print("❌ Error: --params required when using --tool", file=sys.stderr)
                sys.exit(1)

            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                print(f"❌ Error: Invalid JSON in --params: {str(e)}", file=sys.stderr)
                sys.exit(1)

            success = run_test_case(tester, args.tool, params,
                                   f"Custom test for {args.tool}", args.verbose)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Testing cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
