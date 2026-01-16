#!/bin/bash
# ralph.sh - The Autonomous Loop

# Parse command line arguments
PRD_FILE="${1:-PRD.md}"
PROGRESS_FILE="${2:-progress.txt}"

# Show usage if --help is passed
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [PRD_FILE] [PROGRESS_FILE]"
    echo ""
    echo "Arguments:"
    echo "  PRD_FILE       Path to PRD file (default: PRD.md)"
    echo "  PROGRESS_FILE  Path to progress file (default: progress.txt)"
    echo ""
    echo "Example:"
    echo "  $0 PRD-E2E.md progress-e2e.txt"
    exit 0
fi

MAX_ITERATIONS=20
ITERATION=0

echo "Starting Ralph Loop..."
echo "PRD File: $PRD_FILE"
echo "Progress File: $PROGRESS_FILE"
echo ""

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ((ITERATION++))
    echo "--- Iteration $ITERATION / $MAX_ITERATIONS ---"

    # Run Claude Code in non-interactive mode (-p)
    # We pass the PRD and Progress file as context
    # We instruct it to output a specific XML tag when finished
    output=$(claude -p "
        Context: @$PRD_FILE @$PROGRESS_FILE

        Goal: Complete the next pending task in $PRD_FILE.
        
        Rules:
        1. READ $PROGRESS_FILE to see what is already done.
        2. Pick the NEXT highest priority task.
        3. IMPLEMENT code and RUN tests to verify.
        4. APPEND a summary of your work to $PROGRESS_FILE.
        5. If ALL tasks in $PRD_FILE are verified done, output exactly: <promise>DONE</promise>
        " 2>&1)

    echo "$output"

    # Check for the completion signal
    if echo "$output" | grep -q "<promise>DONE</promise>"; then
        echo "✅ Ralph finished successfully!"
        exit 0
    fi
done

echo "⚠️ Max iterations reached without completion."