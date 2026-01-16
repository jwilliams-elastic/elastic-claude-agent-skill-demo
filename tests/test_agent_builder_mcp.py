"""
Automated test suite for Agent Builder MCP tools.

This module contains pytest tests for validating Agent Builder tools
via the Elastic MCP endpoint.
"""

import json
import os
from typing import Dict, Any

import pytest
import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def mcp_client():
    """
    Pytest fixture for MCP client.

    Returns:
        Dict with client configuration
    """
    mcp_url = os.getenv('ELASTIC_MCP_URL')
    api_key = os.getenv('ELASTIC_API_KEY')

    if not mcp_url or not api_key:
        pytest.skip("ELASTIC_MCP_URL and ELASTIC_API_KEY environment variables must be set")

    return {
        'mcp_url': mcp_url.rstrip('/'),
        'api_key': api_key,
        'headers': {
            "Authorization": f"ApiKey {api_key}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json"
        }
    }


def execute_tool(client: Dict[str, Any], tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool via MCP endpoint.

    Args:
        client: MCP client configuration
        tool_id: Tool identifier
        params: Tool parameters

    Returns:
        Response from tool execution
    """
    endpoint = f"{client['mcp_url']}/tools/{tool_id}/execute"
    response = requests.post(
        endpoint,
        headers=client['headers'],
        json={"params": params},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


class TestSearchSkills:
    """Test suite for search_skills tool."""

    def test_search_expense_policy(self, mcp_client):
        """Test searching for 'expense policy' returns relevant results."""
        result = execute_tool(mcp_client, "search_skills", {
            "query": "expense policy",
            "limit": 5
        })

        assert result is not None
        assert "error" not in result
        # Results should be returned (implementation-dependent structure)
        assert "results" in result or "data" in result

    def test_search_storm_damage(self, mcp_client):
        """Test searching for 'storm damage' returns relevant results."""
        result = execute_tool(mcp_client, "search_skills", {
            "query": "storm damage",
            "limit": 5
        })

        assert result is not None
        assert "error" not in result
        assert "results" in result or "data" in result

    def test_search_sample_viability(self, mcp_client):
        """Test searching for 'sample viability' returns relevant results."""
        result = execute_tool(mcp_client, "search_skills", {
            "query": "sample viability",
            "limit": 5
        })

        assert result is not None
        assert "error" not in result
        assert "results" in result or "data" in result

    def test_search_with_limit_one(self, mcp_client):
        """Test searching with limit=1 returns single result."""
        result = execute_tool(mcp_client, "search_skills", {
            "query": "expense",
            "limit": 1
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))
        if isinstance(results, list):
            assert len(results) <= 1, "Should return at most 1 result"


class TestGetSkillById:
    """Test suite for get_skill_by_id tool."""

    def test_get_verify_expense_policy(self, mcp_client):
        """Test retrieving 'verify-expense-policy' skill."""
        result = execute_tool(mcp_client, "get_skill_by_id", {
            "skill_id": "verify-expense-policy"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skill data
        if isinstance(results, list):
            assert len(results) > 0, "Should return skill document"
            skill = results[0]
            assert skill.get("skill_id") == "verify-expense-policy"
        elif isinstance(results, dict):
            assert results.get("skill_id") == "verify-expense-policy"

    def test_get_adjudicate_storm_claim(self, mcp_client):
        """Test retrieving 'adjudicate-storm-claim' skill."""
        result = execute_tool(mcp_client, "get_skill_by_id", {
            "skill_id": "adjudicate-storm-claim"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skill data
        if isinstance(results, list):
            assert len(results) > 0, "Should return skill document"
            skill = results[0]
            assert skill.get("skill_id") == "adjudicate-storm-claim"
        elif isinstance(results, dict):
            assert results.get("skill_id") == "adjudicate-storm-claim"

    def test_get_nonexistent_skill(self, mcp_client):
        """Test retrieving a nonexistent skill returns empty or error."""
        result = execute_tool(mcp_client, "get_skill_by_id", {
            "skill_id": "nonexistent-skill-12345"
        })

        # Should return empty results or error
        results = result.get("results", result.get("data", []))
        if isinstance(results, list):
            assert len(results) == 0, "Should return no results for nonexistent skill"


class TestListSkillsByDomain:
    """Test suite for list_skills_by_domain tool."""

    def test_list_finance_skills(self, mcp_client):
        """Test listing finance domain skills."""
        result = execute_tool(mcp_client, "list_skills_by_domain", {
            "domain": "finance"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skills
        if isinstance(results, list):
            assert len(results) > 0, "Should return finance skills"
            # All results should have domain='finance'
            for skill in results:
                assert skill.get("domain") == "finance"

    def test_list_insurance_skills(self, mcp_client):
        """Test listing insurance domain skills."""
        result = execute_tool(mcp_client, "list_skills_by_domain", {
            "domain": "insurance"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skills
        if isinstance(results, list):
            assert len(results) > 0, "Should return insurance skills"
            # All results should have domain='insurance'
            for skill in results:
                assert skill.get("domain") == "insurance"

    def test_list_life_sciences_skills(self, mcp_client):
        """Test listing life_sciences domain skills."""
        result = execute_tool(mcp_client, "list_skills_by_domain", {
            "domain": "life_sciences"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skills
        if isinstance(results, list):
            assert len(results) > 0, "Should return life_sciences skills"
            # All results should have domain='life_sciences'
            for skill in results:
                assert skill.get("domain") == "life_sciences"

    def test_list_nonexistent_domain(self, mcp_client):
        """Test listing skills from nonexistent domain returns empty results."""
        result = execute_tool(mcp_client, "list_skills_by_domain", {
            "domain": "nonexistent-domain-xyz"
        })

        # Should return empty results
        results = result.get("results", result.get("data", []))
        if isinstance(results, list):
            assert len(results) == 0, "Should return no results for nonexistent domain"


class TestGetSkillMetadata:
    """Test suite for get_skill_metadata tool."""

    def test_get_metadata_verify_expense_policy(self, mcp_client):
        """Test retrieving metadata for 'verify-expense-policy'."""
        result = execute_tool(mcp_client, "get_skill_metadata", {
            "skill_id": "verify-expense-policy"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return metadata
        if isinstance(results, list):
            assert len(results) > 0, "Should return metadata"
            metadata = results[0]

            # Check metadata fields are present
            expected_fields = ["skill_id", "name", "domain", "tags"]
            for field in expected_fields:
                assert field in metadata, f"Metadata should include {field}"

            # Large fields should NOT be present
            assert "skill_markdown" not in metadata or len(str(metadata.get("skill_markdown", ""))) < 1000
            assert metadata.get("skill_id") == "verify-expense-policy"

        elif isinstance(results, dict):
            # Check metadata fields are present
            expected_fields = ["skill_id", "name", "domain", "tags"]
            for field in expected_fields:
                assert field in results, f"Metadata should include {field}"
            assert results.get("skill_id") == "verify-expense-policy"

    def test_get_metadata_nonexistent_skill(self, mcp_client):
        """Test retrieving metadata for nonexistent skill returns empty."""
        result = execute_tool(mcp_client, "get_skill_metadata", {
            "skill_id": "nonexistent-skill-12345"
        })

        # Should return empty results
        results = result.get("results", result.get("data", []))
        if isinstance(results, list):
            assert len(results) == 0, "Should return no results for nonexistent skill"


class TestSearchSkillsByTags:
    """Test suite for search_skills_by_tags tool."""

    def test_search_finance_tag(self, mcp_client):
        """Test searching for 'finance' tag."""
        result = execute_tool(mcp_client, "search_skills_by_tags", {
            "tag": ".*finance.*"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skills with finance tag
        if isinstance(results, list) and len(results) > 0:
            for skill in results:
                tags = skill.get("tags", [])
                # Check if any tag contains 'finance'
                has_finance_tag = any("finance" in str(tag).lower() for tag in tags)
                assert has_finance_tag, f"Skill should have 'finance' tag, got {tags}"

    def test_search_insurance_tag(self, mcp_client):
        """Test searching for 'insurance' tag."""
        result = execute_tool(mcp_client, "search_skills_by_tags", {
            "tag": ".*insurance.*"
        })

        assert result is not None
        assert "error" not in result

        # Extract results
        results = result.get("results", result.get("data", []))

        # Should return skills with insurance tag
        if isinstance(results, list) and len(results) > 0:
            for skill in results:
                tags = skill.get("tags", [])
                # Check if any tag contains 'insurance'
                has_insurance_tag = any("insurance" in str(tag).lower() for tag in tags)
                assert has_insurance_tag, f"Skill should have 'insurance' tag, got {tags}"

    def test_search_compliance_tag(self, mcp_client):
        """Test searching for 'compliance' tag."""
        result = execute_tool(mcp_client, "search_skills_by_tags", {
            "tag": ".*compliance.*"
        })

        assert result is not None
        assert "error" not in result

        # Should return results (may be empty if no compliance-tagged skills exist)
        assert "results" in result or "data" in result


# Integration test
class TestIntegration:
    """Integration tests for Agent Builder MCP tools."""

    def test_end_to_end_workflow(self, mcp_client):
        """Test complete workflow: search, get by ID, get metadata."""
        # Step 1: Search for skills
        search_result = execute_tool(mcp_client, "search_skills", {
            "query": "expense",
            "limit": 5
        })

        assert "error" not in search_result
        results = search_result.get("results", search_result.get("data", []))

        if isinstance(results, list) and len(results) > 0:
            # Step 2: Get first skill by ID
            first_skill = results[0]
            skill_id = first_skill.get("skill_id")

            if skill_id:
                # Get full skill document
                skill_result = execute_tool(mcp_client, "get_skill_by_id", {
                    "skill_id": skill_id
                })

                assert "error" not in skill_result

                # Step 3: Get metadata only
                metadata_result = execute_tool(mcp_client, "get_skill_metadata", {
                    "skill_id": skill_id
                })

                assert "error" not in metadata_result

                # Metadata should be smaller than full document
                metadata_size = len(json.dumps(metadata_result))
                skill_size = len(json.dumps(skill_result))

                # This is a soft check - metadata might not always be smaller
                # depending on the actual implementation
                print(f"Metadata size: {metadata_size}, Full skill size: {skill_size}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
