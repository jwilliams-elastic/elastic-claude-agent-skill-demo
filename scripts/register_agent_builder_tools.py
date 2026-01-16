#!/usr/bin/env python3
"""
Registration script for Elastic Agent Builder tools.

This script registers tool definitions from JSON files to Kibana Agent Builder API.
It supports creating, updating, deleting, and listing tools via the Kibana API.
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


class AgentBuilderClient:
    """Client for interacting with Kibana Agent Builder API."""

    def __init__(self, kibana_url: str, api_key: str):
        """
        Initialize the Agent Builder client.

        Args:
            kibana_url: Base Kibana URL (e.g., https://kibana.example.com)
            api_key: Elastic API key for authentication
        """
        self.kibana_url = kibana_url.rstrip('/')
        self.api_key = api_key
        self.api_endpoint = f"{self.kibana_url}/api/agent_builder/tools"

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"ApiKey {self.api_key}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json"
        }

    def register_tool(self, tool_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new tool with Agent Builder API.

        Args:
            tool_definition: Tool definition JSON object

        Returns:
            Response data from the API

        Raises:
            requests.HTTPError: If the API request fails
        """
        try:
            response = requests.post(
                self.api_endpoint,
                headers=self._get_headers(),
                json=tool_definition,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_error(e, "registering tool")
            raise

    def update_tool(self, tool_id: str, tool_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing tool.

        Args:
            tool_id: Tool identifier
            tool_definition: Updated tool definition JSON object

        Returns:
            Response data from the API

        Raises:
            requests.HTTPError: If the API request fails
        """
        try:
            response = requests.put(
                f"{self.api_endpoint}/{tool_id}",
                headers=self._get_headers(),
                json=tool_definition,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_error(e, f"updating tool '{tool_id}'")
            raise

    def delete_tool(self, tool_id: str) -> Dict[str, Any]:
        """
        Delete a tool.

        Args:
            tool_id: Tool identifier

        Returns:
            Response data from the API

        Raises:
            requests.HTTPError: If the API request fails
        """
        try:
            response = requests.delete(
                f"{self.api_endpoint}/{tool_id}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else {"success": True}
        except requests.exceptions.RequestException as e:
            self._handle_error(e, f"deleting tool '{tool_id}'")
            raise

    def list_tools(self) -> Dict[str, Any]:
        """
        List all registered tools.

        Returns:
            Response data from the API containing list of tools

        Raises:
            requests.HTTPError: If the API request fails
        """
        try:
            response = requests.get(
                self.api_endpoint,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_error(e, "listing tools")
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
            print(f"   Connection Error: Could not connect to {self.kibana_url}", file=sys.stderr)
            print(f"   Details: {str(error)}", file=sys.stderr)
        elif isinstance(error, requests.exceptions.Timeout):
            print(f"   Timeout: Request took longer than 30 seconds", file=sys.stderr)
        else:
            print(f"   {type(error).__name__}: {str(error)}", file=sys.stderr)


def load_tool_definition(file_path: Path) -> Dict[str, Any]:
    """
    Load tool definition from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Tool definition as dictionary

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def validate_tool_definition(tool_def: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate tool definition structure.

    Args:
        tool_def: Tool definition to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['id', 'type', 'configuration']

    for field in required_fields:
        if field not in tool_def:
            return False, f"Missing required field: {field}"

    if 'query' not in tool_def.get('configuration', {}):
        return False, "Missing required field: configuration.query"

    if tool_def['type'] != 'esql':
        return False, f"Invalid type: {tool_def['type']} (expected 'esql')"

    return True, None


def register_tool_from_file(client: AgentBuilderClient, file_path: Path, dry_run: bool = False) -> bool:
    """
    Register a single tool from a JSON file.

    Args:
        client: Agent Builder client
        file_path: Path to tool definition JSON file
        dry_run: If True, validate only without registering

    Returns:
        True if successful, False otherwise
    """
    try:
        tool_def = load_tool_definition(file_path)
        tool_id = tool_def.get('id', 'unknown')

        # Validate tool definition
        is_valid, error_msg = validate_tool_definition(tool_def)
        if not is_valid:
            print(f"❌ {file_path.name}: Validation failed - {error_msg}")
            return False

        if dry_run:
            print(f"✓ {file_path.name}: Valid tool definition for '{tool_id}'")
            return True

        # Register tool
        response = client.register_tool(tool_def)
        print(f"✅ {file_path.name}: Successfully registered tool '{tool_id}'")
        return True

    except FileNotFoundError:
        print(f"❌ {file_path.name}: File not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ {file_path.name}: Invalid JSON - {str(e)}")
        return False
    except requests.HTTPError:
        return False
    except Exception as e:
        print(f"❌ {file_path.name}: Unexpected error - {str(e)}")
        return False


def register_all_tools(tools_dir: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Register all tools from a directory.

    Args:
        tools_dir: Directory containing tool definition JSON files
        dry_run: If True, validate only without registering

    Returns:
        Dictionary with counts: {'total': n, 'successful': n, 'failed': n}
    """
    # Get environment variables
    kibana_url = os.getenv('KIBANA_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not kibana_url or not api_key:
        print("❌ Error: KIBANA_URL and ELASTIC_API_KEY environment variables must be set", file=sys.stderr)
        sys.exit(1)

    client = AgentBuilderClient(kibana_url, api_key)

    # Find all JSON files in tools directory
    json_files = sorted(tools_dir.glob('*.json'))

    if not json_files:
        print(f"⚠️  No JSON files found in {tools_dir}")
        return {'total': 0, 'successful': 0, 'failed': 0}

    print(f"\n{'Validating' if dry_run else 'Registering'} {len(json_files)} tool(s)...\n")

    results = {'total': len(json_files), 'successful': 0, 'failed': 0}

    for json_file in json_files:
        if register_tool_from_file(client, json_file, dry_run):
            results['successful'] += 1
        else:
            results['failed'] += 1

    # Print summary
    print(f"\n{'Validation' if dry_run else 'Registration'} Summary:")
    print(f"  Total: {results['total']}")
    print(f"  ✅ Successful: {results['successful']}")
    print(f"  ❌ Failed: {results['failed']}")

    return results


def main():
    """Main entry point for the registration script."""
    parser = argparse.ArgumentParser(
        description='Register and manage Elastic Agent Builder tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register all tools
  %(prog)s --register

  # Validate tools without registering (dry run)
  %(prog)s --dry-run

  # Update a specific tool
  %(prog)s --update search_skills

  # Delete a specific tool
  %(prog)s --delete search_skills

  # List all registered tools
  %(prog)s --list
        """
    )

    parser.add_argument(
        '--register',
        action='store_true',
        help='Register all tools from agent_builder/tools/ directory'
    )

    parser.add_argument(
        '--update',
        metavar='TOOL_ID',
        help='Update a specific tool by ID'
    )

    parser.add_argument(
        '--delete',
        metavar='TOOL_ID',
        help='Delete a specific tool by ID'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all registered tools'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate tool definitions without registering them'
    )

    parser.add_argument(
        '--tools-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'agent_builder' / 'tools',
        help='Directory containing tool definition JSON files (default: agent_builder/tools/)'
    )

    args = parser.parse_args()

    # Check if at least one action is specified
    if not any([args.register, args.update, args.delete, args.list, args.dry_run]):
        parser.print_help()
        sys.exit(1)

    # Get environment variables
    kibana_url = os.getenv('KIBANA_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not kibana_url or not api_key:
        print("❌ Error: KIBANA_URL and ELASTIC_API_KEY environment variables must be set", file=sys.stderr)
        print("   Please check your .env file or set these variables manually", file=sys.stderr)
        sys.exit(1)

    client = AgentBuilderClient(kibana_url, api_key)

    try:
        # Handle different actions
        if args.list:
            print(f"\n🔍 Listing registered tools...\n")
            response = client.list_tools()
            print(json.dumps(response, indent=2))

        elif args.delete:
            print(f"\n🗑️  Deleting tool '{args.delete}'...\n")
            response = client.delete_tool(args.delete)
            print(f"✅ Successfully deleted tool '{args.delete}'")

        elif args.update:
            tool_file = args.tools_dir / f"{args.update}.json"
            if not tool_file.exists():
                print(f"❌ Error: Tool definition file not found: {tool_file}", file=sys.stderr)
                sys.exit(1)

            print(f"\n🔄 Updating tool '{args.update}'...\n")
            tool_def = load_tool_definition(tool_file)

            # Validate before updating
            is_valid, error_msg = validate_tool_definition(tool_def)
            if not is_valid:
                print(f"❌ Validation failed: {error_msg}", file=sys.stderr)
                sys.exit(1)

            response = client.update_tool(args.update, tool_def)
            print(f"✅ Successfully updated tool '{args.update}'")

        elif args.register or args.dry_run:
            if not args.tools_dir.exists():
                print(f"❌ Error: Tools directory not found: {args.tools_dir}", file=sys.stderr)
                sys.exit(1)

            results = register_all_tools(args.tools_dir, dry_run=args.dry_run)

            # Exit with error code if any registrations failed
            if results['failed'] > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
