#!/bin/bash
# Task 1.3 Completion Script
# This script runs ingestion (if needed) and validates the document structure

set -e  # Exit on error

echo "=========================================="
echo "Task 1.3: Document Structure Validation"
echo "=========================================="
echo ""

# Check if index already has documents
echo "Step 1: Checking if ingestion is needed..."
VALIDATION_OUTPUT=$(uv run scripts/run_task_1_3_validation.py 2>&1 || true)

if echo "$VALIDATION_OUTPUT" | grep -q "does not exist yet"; then
    echo "  Index not found. Running ingestion..."
    echo ""
    echo "Step 2: Running ingestion script..."
    uv run scripts/ingest_skills.py
    echo ""
    echo "Step 3: Running validation..."
    uv run scripts/run_task_1_3_validation.py
elif echo "$VALIDATION_OUTPUT" | grep -q "No documents found"; then
    echo "  Index exists but empty. Running ingestion..."
    echo ""
    echo "Step 2: Running ingestion script..."
    uv run scripts/ingest_skills.py
    echo ""
    echo "Step 3: Running validation..."
    uv run scripts/run_task_1_3_validation.py
else
    echo "  Index already has documents. Running validation only..."
    echo ""
    echo "Step 2: Running validation..."
    uv run scripts/run_task_1_3_validation.py
fi

echo ""
echo "=========================================="
echo "Task 1.3 Complete!"
echo "=========================================="
