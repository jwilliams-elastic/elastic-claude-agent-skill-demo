#!/bin/bash
#
# init.sh - Initialize Agent Builder tools and agents in Kibana
#
# This script creates:
#   1. MCP tools from JSON files in agent_builder/tools/
#   2. Agent definitions from JSON files in agent_builder/agents/
#
# Prerequisites:
#   - KIBANA_URL environment variable (e.g., https://your-deployment.kb.us-east-1.aws.elastic.cloud:9243)
#   - ELASTIC_API_KEY environment variable
#
# Usage:
#   ./init.sh                    # Create all tools and agents
#   ./init.sh --tools-only       # Create only tools
#   ./init.sh --agents-only      # Create only agents
#   ./init.sh --delete-all       # Delete all tools and agents
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="${SCRIPT_DIR}/agent_builder/tools"
AGENTS_DIR="${SCRIPT_DIR}/agent_builder/agents"

# Load environment variables from .env if it exists
if [ -f "${SCRIPT_DIR}/.env" ]; then
    echo -e "${YELLOW}Loading environment from .env file...${NC}"
    export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
fi

# Validate required environment variables
if [ -z "${KIBANA_URL}" ]; then
    echo -e "${RED}Error: KIBANA_URL environment variable is not set${NC}"
    echo "Set it in your .env file or export it:"
    echo "  export KIBANA_URL=https://your-kibana-url"
    exit 1
fi

if [ -z "${ELASTIC_API_KEY}" ]; then
    echo -e "${RED}Error: ELASTIC_API_KEY environment variable is not set${NC}"
    echo "Set it in your .env file or export it:"
    echo "  export ELASTIC_API_KEY=your-api-key"
    exit 1
fi

# Remove trailing slash from KIBANA_URL if present
KIBANA_URL="${KIBANA_URL%/}"

echo "============================================"
echo "Agent Builder - Initialization"
echo "============================================"
echo "Kibana URL: ${KIBANA_URL}"
echo "Tools directory: ${TOOLS_DIR}"
echo "Agents directory: ${AGENTS_DIR}"
echo ""

# =============================================================================
# Tool Functions
# =============================================================================

# Function to create a tool
create_tool() {
    local tool_file="$1"
    local tool_name=$(basename "${tool_file}" .json)

    echo -e "${YELLOW}Creating tool: ${tool_name}${NC}"

    # Read the tool definition
    local tool_json=$(cat "${tool_file}")

    # Make the API call
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        "${KIBANA_URL}/api/agent_builder/tools" \
        -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -d "${tool_json}")

    # Extract status code (last line) and body (everything else)
    local http_code=$(echo "${response}" | tail -n1)
    local body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" = "200" ] || [ "${http_code}" = "201" ]; then
        echo -e "${GREEN}  ✓ Tool '${tool_name}' created successfully${NC}"
        return 0
    elif [ "${http_code}" = "409" ]; then
        echo -e "${YELLOW}  ⚠ Tool '${tool_name}' already exists, updating...${NC}"
        update_tool "${tool_file}"
        return $?
    else
        echo -e "${RED}  ✗ Failed to create tool '${tool_name}'${NC}"
        echo "    HTTP Status: ${http_code}"
        echo "    Response: ${body}"
        return 1
    fi
}

# Function to update an existing tool
update_tool() {
    local tool_file="$1"
    local tool_json=$(cat "${tool_file}")
    local tool_id=$(echo "${tool_json}" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

    local response=$(curl -s -w "\n%{http_code}" -X PUT \
        "${KIBANA_URL}/api/agent_builder/tools/${tool_id}" \
        -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -d "${tool_json}")

    local http_code=$(echo "${response}" | tail -n1)
    local body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" = "200" ] || [ "${http_code}" = "201" ]; then
        echo -e "${GREEN}  ✓ Tool updated successfully${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed to update tool${NC}"
        echo "    HTTP Status: ${http_code}"
        echo "    Response: ${body}"
        return 1
    fi
}

# Function to delete a tool
delete_tool() {
    local tool_file="$1"
    local tool_json=$(cat "${tool_file}")
    local tool_id=$(echo "${tool_json}" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    local tool_name=$(basename "${tool_file}" .json)

    echo -e "${YELLOW}Deleting tool: ${tool_name} (${tool_id})${NC}"

    local response=$(curl -s -w "\n%{http_code}" -X DELETE \
        "${KIBANA_URL}/api/agent_builder/tools/${tool_id}" \
        -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
        -H "kbn-xsrf: true")

    local http_code=$(echo "${response}" | tail -n1)
    local body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" = "200" ] || [ "${http_code}" = "204" ]; then
        echo -e "${GREEN}  ✓ Tool '${tool_name}' deleted successfully${NC}"
        return 0
    elif [ "${http_code}" = "404" ]; then
        echo -e "${YELLOW}  ⚠ Tool '${tool_name}' not found (already deleted?)${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed to delete tool '${tool_name}'${NC}"
        echo "    HTTP Status: ${http_code}"
        echo "    Response: ${body}"
        return 1
    fi
}

# =============================================================================
# Agent Functions
# =============================================================================

# Function to create an agent
create_agent() {
    local agent_file="$1"
    local agent_name=$(basename "${agent_file}" .json)

    echo -e "${YELLOW}Creating agent: ${agent_name}${NC}"

    # Read the agent definition
    local agent_json=$(cat "${agent_file}")

    # Make the API call
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        "${KIBANA_URL}/api/agent_builder/agents" \
        -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -d "${agent_json}")

    # Extract status code (last line) and body (everything else)
    local http_code=$(echo "${response}" | tail -n1)
    local body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" = "200" ] || [ "${http_code}" = "201" ]; then
        echo -e "${GREEN}  ✓ Agent '${agent_name}' created successfully${NC}"
        return 0
    elif [ "${http_code}" = "409" ]; then
        echo -e "${YELLOW}  ⚠ Agent '${agent_name}' already exists, updating...${NC}"
        # Try to update the agent
        update_agent "${agent_file}"
        return $?
    else
        echo -e "${RED}  ✗ Failed to create agent '${agent_name}'${NC}"
        echo "    HTTP Status: ${http_code}"
        echo "    Response: ${body}"
        return 1
    fi
}

# Function to update an existing agent
update_agent() {
    local agent_file="$1"
    local agent_json=$(cat "${agent_file}")
    local agent_id=$(echo "${agent_json}" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

    local response=$(curl -s -w "\n%{http_code}" -X PUT \
        "${KIBANA_URL}/api/agent_builder/agents/${agent_id}" \
        -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -d "${agent_json}")

    local http_code=$(echo "${response}" | tail -n1)
    local body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" = "200" ] || [ "${http_code}" = "201" ]; then
        echo -e "${GREEN}  ✓ Agent updated successfully${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed to update agent${NC}"
        echo "    HTTP Status: ${http_code}"
        echo "    Response: ${body}"
        return 1
    fi
}

# Function to delete an agent
delete_agent() {
    local agent_file="$1"
    local agent_json=$(cat "${agent_file}")
    local agent_id=$(echo "${agent_json}" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    local agent_name=$(basename "${agent_file}" .json)

    echo -e "${YELLOW}Deleting agent: ${agent_name} (${agent_id})${NC}"

    local response=$(curl -s -w "\n%{http_code}" -X DELETE \
        "${KIBANA_URL}/api/agent_builder/agents/${agent_id}" \
        -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
        -H "kbn-xsrf: true")

    local http_code=$(echo "${response}" | tail -n1)
    local body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" = "200" ] || [ "${http_code}" = "204" ]; then
        echo -e "${GREEN}  ✓ Agent '${agent_name}' deleted successfully${NC}"
        return 0
    elif [ "${http_code}" = "404" ]; then
        echo -e "${YELLOW}  ⚠ Agent '${agent_name}' not found (already deleted?)${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed to delete agent '${agent_name}'${NC}"
        echo "    HTTP Status: ${http_code}"
        echo "    Response: ${body}"
        return 1
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

# Parse arguments
CREATE_TOOLS=true
CREATE_AGENTS=true
DELETE_ALL=false

if [ "$1" = "--tools-only" ]; then
    CREATE_AGENTS=false
elif [ "$1" = "--agents-only" ]; then
    CREATE_TOOLS=false
elif [ "$1" = "--delete-all" ]; then
    DELETE_ALL=true
    CREATE_TOOLS=false
    CREATE_AGENTS=false
fi

tools_success=0
tools_fail=0
agents_success=0
agents_fail=0

# -----------------------------------------------------------------------------
# Delete All (if requested)
# -----------------------------------------------------------------------------
if [ "${DELETE_ALL}" = true ]; then
    echo "--------------------------------------------"
    echo "Deleting Agents"
    echo "--------------------------------------------"

    if [ -d "${AGENTS_DIR}" ]; then
        agent_files=$(find "${AGENTS_DIR}" -name "*.json" -type f 2>/dev/null)
        if [ -n "${agent_files}" ]; then
            for agent_file in ${agent_files}; do
                if delete_agent "${agent_file}"; then
                    ((agents_success++))
                else
                    ((agents_fail++))
                fi
            done
        else
            echo "No agent files found"
        fi
    else
        echo -e "${YELLOW}Agents directory not found${NC}"
    fi
    echo ""

    echo "--------------------------------------------"
    echo "Deleting MCP Tools"
    echo "--------------------------------------------"

    if [ -d "${TOOLS_DIR}" ]; then
        tool_files=$(find "${TOOLS_DIR}" -name "*.json" -type f 2>/dev/null)
        if [ -n "${tool_files}" ]; then
            for tool_file in ${tool_files}; do
                if delete_tool "${tool_file}"; then
                    ((tools_success++))
                else
                    ((tools_fail++))
                fi
            done
        else
            echo "No tool files found"
        fi
    else
        echo -e "${YELLOW}Tools directory not found${NC}"
    fi
    echo ""

    echo "============================================"
    echo "Delete Summary"
    echo "============================================"
    echo -e "  Agents: ${GREEN}${agents_success} deleted${NC}, ${RED}${agents_fail} failed${NC}"
    echo -e "  Tools:  ${GREEN}${tools_success} deleted${NC}, ${RED}${tools_fail} failed${NC}"
    echo "============================================"

    total_fail=$((tools_fail + agents_fail))
    exit ${total_fail}
fi

# -----------------------------------------------------------------------------
# Create Tools
# -----------------------------------------------------------------------------
if [ "${CREATE_TOOLS}" = true ]; then
    echo "--------------------------------------------"
    echo "Creating MCP Tools"
    echo "--------------------------------------------"

    if [ ! -d "${TOOLS_DIR}" ]; then
        echo -e "${YELLOW}Tools directory not found: ${TOOLS_DIR}${NC}"
        echo "Skipping tool creation..."
    else
        tool_files=$(find "${TOOLS_DIR}" -name "*.json" -type f 2>/dev/null)
        if [ -z "${tool_files}" ]; then
            echo "No tool files found in ${TOOLS_DIR}"
        else
            for tool_file in ${tool_files}; do
                if create_tool "${tool_file}"; then
                    ((tools_success++))
                else
                    ((tools_fail++))
                fi
            done
        fi
    fi
    echo ""
fi

# -----------------------------------------------------------------------------
# Create Agents
# -----------------------------------------------------------------------------
if [ "${CREATE_AGENTS}" = true ]; then
    echo "--------------------------------------------"
    echo "Creating Agents"
    echo "--------------------------------------------"

    if [ ! -d "${AGENTS_DIR}" ]; then
        echo -e "${YELLOW}Agents directory not found: ${AGENTS_DIR}${NC}"
        echo "Skipping agent creation..."
    else
        agent_files=$(find "${AGENTS_DIR}" -name "*.json" -type f 2>/dev/null)
        if [ -z "${agent_files}" ]; then
            echo "No agent files found in ${AGENTS_DIR}"
        else
            for agent_file in ${agent_files}; do
                if create_agent "${agent_file}"; then
                    ((agents_success++))
                else
                    ((agents_fail++))
                fi
            done
        fi
    fi
    echo ""
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "============================================"
echo "Summary"
echo "============================================"
if [ "${CREATE_TOOLS}" = true ]; then
    echo -e "  Tools:  ${GREEN}${tools_success} created${NC}, ${RED}${tools_fail} failed${NC}"
fi
if [ "${CREATE_AGENTS}" = true ]; then
    echo -e "  Agents: ${GREEN}${agents_success} created${NC}, ${RED}${agents_fail} failed${NC}"
fi
echo "============================================"
echo ""
echo -e "${YELLOW}Next Steps (run in separate terminals):${NC}"
echo ""
echo "  1. Start the API server:"
echo "     uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  2. Expose via Cloudflare tunnel:"
echo "     cloudflared tunnel --url http://localhost:8000"
echo ""
echo "  3. Update 'consts.api_base_url' in agent_builder/workflows/agent_skills_operator.yaml"
echo "     to your new Cloudflare tunnel URL"
echo ""
echo "============================================"

total_fail=$((tools_fail + agents_fail))
exit ${total_fail}
