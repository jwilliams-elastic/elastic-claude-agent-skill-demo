#!/usr/bin/env python3
"""
Ingestion Script for Agent Skills Repository
Indexes skill documents from sample_skills directory into Elasticsearch
Uses semantic_text with automatic inference for embeddings
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def parse_skill_metadata(skill_dir: Path) -> Dict[str, Any]:
    """
    Parse SKILL.md and extract metadata from the skill directory.

    Args:
        skill_dir: Path to skill directory

    Returns:
        Dictionary containing skill metadata
    """
    skill_md_path = skill_dir / "SKILL.md"

    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract basic metadata
    skill_id = skill_dir.name

    # Parse markdown for title (first h1)
    lines = content.split('\n')
    title = skill_id
    description = ""
    domain = "general"
    tags = []

    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line[2:].strip()
        elif line.startswith('## Description'):
            # Get content until next heading
            desc_lines = []
            for j in range(i+1, len(lines)):
                if lines[j].startswith('#'):
                    break
                desc_lines.append(lines[j])
            description = '\n'.join(desc_lines).strip()
        elif line.startswith('## Domain'):
            # Domain value is on the next non-empty line
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('#'):
                    domain = lines[j].strip().lower()
                    break
        elif line.startswith('## Tags'):
            # Tags value is on the next non-empty line
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('#'):
                    tag_str = lines[j].strip()
                    tags = [t.strip() for t in tag_str.split(',')]
                    break
        elif line.startswith('**Domain:**'):
            domain = line.split(':', 1)[1].strip().lower()
        elif line.startswith('**Tags:**'):
            tag_str = line.split(':', 1)[1].strip()
            tags = [t.strip() for t in tag_str.split(',')]

    # Collect all files in directory
    files = []
    for file_path in skill_dir.rglob('*'):
        if file_path.is_file():
            rel_path = file_path.relative_to(skill_dir)
            files.append({
                "filename": file_path.name,
                "path": str(rel_path),
                "type": file_path.suffix[1:] if file_path.suffix else "unknown"
            })

    return {
        "skill_id": skill_id,
        "title": title,
        "description": description,
        "domain": domain,
        "tags": tags,
        "content": content,
        "files": files
    }


def create_skill_document(skill_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an Elasticsearch document from skill metadata.
    Uses semantic_text field which automatically generates embeddings via inference.

    Args:
        skill_metadata: Parsed skill metadata

    Returns:
        Document ready for indexing
    """
    # Map fields to match index schema
    # The semantic_content field will be automatically populated via copy_to directives
    # Note: skill_markdown is no longer stored here - file contents are in agent_skill_files index
    doc = {
        "skill_id": skill_metadata["skill_id"],
        "name": skill_metadata["title"],  # Maps to 'name' field in index
        "description": skill_metadata["description"],
        "short_description": skill_metadata["description"][:200] if len(skill_metadata["description"]) > 200 else skill_metadata["description"],
        "domain": skill_metadata["domain"],
        "tags": skill_metadata["tags"],
        "author": "system",  # Default author
        "version": "1.0",
        "created_at": "2026-01-14T00:00:00Z",
        "updated_at": "2026-01-14T00:00:00Z",
        "usage_count": 0,
        "success_rate": 1.0,
        "avg_execution_time_ms": 0,
        "rating": 5.0,
        "allowed_tools": ["Bash", "Read", "Write"],
        "execution_mode": "inline",
        "requires_elasticsearch": False
    }

    return doc


def ensure_index(es: Elasticsearch, index_name: str, config_dir: Path, recreate: bool = False) -> None:
    """
    Create index with proper mappings and settings if it doesn't exist.

    Args:
        es: Elasticsearch client
        index_name: Name of the index
        config_dir: Path to config directory
        recreate: If True, delete and recreate the index even if it exists
    """
    if es.indices.exists(index=index_name):
        if recreate:
            print(f"Deleting existing index '{index_name}'...")
            es.indices.delete(index=index_name)
        else:
            print(f"Index '{index_name}' already exists.")
            return

    # Load mappings and settings
    mappings_path = config_dir / "index_mappings.json"
    settings_path = config_dir / "index_settings.json"

    with open(mappings_path, 'r') as f:
        mappings_config = json.load(f)

    with open(settings_path, 'r') as f:
        settings_config = json.load(f)

    # Create index with proper structure
    es.indices.create(
        index=index_name,
        mappings=mappings_config.get("mappings"),
        settings=settings_config.get("settings")
    )
    print(f"Created index '{index_name}' with mappings and settings.")


def ensure_files_index(es: Elasticsearch, index_name: str, config_dir: Path, recreate: bool = False) -> None:
    """
    Create the skill files index with proper mappings if it doesn't exist.

    Args:
        es: Elasticsearch client
        index_name: Name of the files index
        config_dir: Path to config directory
        recreate: If True, delete and recreate the index even if it exists
    """
    if es.indices.exists(index=index_name):
        if recreate:
            print(f"Deleting existing index '{index_name}'...")
            es.indices.delete(index=index_name)
        else:
            print(f"Index '{index_name}' already exists.")
            return

    # Load mappings and settings for skill files
    mappings_path = config_dir / "skill_files_mappings.json"
    settings_path = config_dir / "skill_files_settings.json"

    with open(mappings_path, 'r') as f:
        mappings_config = json.load(f)

    with open(settings_path, 'r') as f:
        settings_config = json.load(f)

    # Create index
    es.indices.create(
        index=index_name,
        mappings=mappings_config.get("mappings"),
        settings=settings_config.get("settings")
    )
    print(f"Created index '{index_name}' with mappings and settings.")


def collect_skill_files(
    skill_dir: Path,
    skill_id: str,
    index_name: str = "agent_skill_files"
) -> List[Dict[str, Any]]:
    """
    Collect all file documents from a skill directory for bulk indexing.

    Args:
        skill_dir: Path to skill directory
        skill_id: Skill identifier
        index_name: Target index name for files

    Returns:
        List of bulk operation dictionaries
    """
    operations = []

    for file_path in skill_dir.rglob('*'):
        # Skip directories, __pycache__, and .pyc files
        if not file_path.is_file():
            continue
        if '__pycache__' in str(file_path):
            continue
        if file_path.suffix == '.pyc':
            continue

        try:
            # Read file content
            file_content = file_path.read_text(encoding='utf-8')

            # Create file document
            file_doc = {
                "skill_id": skill_id,
                "file_name": file_path.name,
                "file_path": str(file_path.relative_to(skill_dir)),
                "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
                "file_content": file_content,
                "file_size_bytes": file_path.stat().st_size,
                "created_at": datetime.utcnow().isoformat()
            }

            # Generate document ID
            doc_id = f"{skill_id}_{file_path.name}"

            # Add bulk operation (action + document)
            operations.append({"index": {"_index": index_name, "_id": doc_id}})
            operations.append(file_doc)

        except UnicodeDecodeError:
            # Skip binary files that can't be decoded as text
            pass
        except Exception as e:
            print(f"    - Error reading file {file_path.name}: {e}")

    return operations


def index_skill_files(
    skill_dir: Path,
    skill_id: str,
    es_client: Elasticsearch,
    index_name: str = "agent_skill_files"
) -> int:
    """
    Index all files from a skill directory into Elasticsearch (legacy single-skill method).

    Args:
        skill_dir: Path to skill directory
        skill_id: Skill identifier
        es_client: Elasticsearch client
        index_name: Target index name for files

    Returns:
        Number of files indexed
    """
    operations = collect_skill_files(skill_dir, skill_id, index_name)

    if not operations:
        return 0

    # Bulk index
    response = es_client.bulk(operations=operations, refresh=False)

    # Count successful indexing operations
    files_indexed = sum(1 for item in response.get("items", []) if "index" in item and item["index"].get("status") in [200, 201])

    return files_indexed


def ingest_skills(
    skills_dir: Path,
    es_client: Elasticsearch,
    index_name: str = "agent_skills",
    files_index_name: str = "agent_skill_files",
    batch_size: int = 100
) -> None:
    """
    Main ingestion function. Uses bulk API for efficient batch indexing.

    Args:
        skills_dir: Path to sample_skills directory
        es_client: Elasticsearch client
        index_name: Target index name for metadata
        files_index_name: Target index name for skill files
        batch_size: Number of operations per bulk request
    """
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")

    # Get all subdirectories (each is a skill)
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if not skill_dirs:
        print("No skills found in directory.")
        return

    print(f"Found {len(skill_dirs)} skills to ingest.")
    print("Collecting documents for bulk indexing...")

    # Collect all skill metadata operations
    skill_operations = []
    # Collect all file operations
    file_operations = []

    ingested = 0
    total_files = 0
    errors = 0

    for skill_dir in skill_dirs:
        try:
            # Parse metadata
            metadata = parse_skill_metadata(skill_dir)

            # Create document
            doc = create_skill_document(metadata)

            # Add bulk operation for skill metadata
            skill_operations.append({"index": {"_index": index_name, "_id": metadata["skill_id"]}})
            skill_operations.append(doc)

            # Collect all file operations for this skill
            file_ops = collect_skill_files(skill_dir, metadata["skill_id"], files_index_name)
            file_operations.extend(file_ops)
            total_files += len(file_ops) // 2  # Each file has 2 entries (action + doc)

            ingested += 1

            # Progress indicator
            if ingested % 10 == 0:
                print(f"  Collected {ingested}/{len(skill_dirs)} skills...")

        except Exception as e:
            print(f"  ✗ Error processing {skill_dir.name}: {e}")
            errors += 1

    print(f"\nCollected {ingested} skills and {total_files} files.")

    # Bulk index skill metadata
    if skill_operations:
        print(f"Bulk indexing {ingested} skill documents...")
        response = es_client.bulk(operations=skill_operations, refresh=False)
        skill_errors = sum(1 for item in response.get("items", []) if item.get("index", {}).get("error"))
        if skill_errors:
            print(f"  Warning: {skill_errors} skill documents had errors")
        print(f"  ✓ Indexed {ingested - skill_errors} skill documents")

    # Bulk index files in batches (to avoid memory issues with large payloads)
    if file_operations:
        print(f"Bulk indexing {total_files} file documents in batches of {batch_size}...")
        files_indexed = 0
        files_errors = 0

        # Process in batches
        for i in range(0, len(file_operations), batch_size * 2):  # *2 because each doc has action + body
            batch = file_operations[i:i + batch_size * 2]
            response = es_client.bulk(operations=batch, refresh=False)

            batch_success = sum(1 for item in response.get("items", []) if "index" in item and item["index"].get("status") in [200, 201])
            batch_errors = sum(1 for item in response.get("items", []) if item.get("index", {}).get("error"))

            files_indexed += batch_success
            files_errors += batch_errors

            # Progress indicator
            progress = min(i + batch_size * 2, len(file_operations)) // 2
            print(f"  Progress: {progress}/{total_files} files...")

        print(f"  ✓ Indexed {files_indexed} file documents")
        if files_errors:
            print(f"  Warning: {files_errors} file documents had errors")

    # Final refresh to make documents searchable
    print("Refreshing indices...")
    es_client.indices.refresh(index=index_name)
    es_client.indices.refresh(index=files_index_name)

    print(f"\n{'='*60}")
    print(f"Ingestion complete: {ingested} skills, {total_files} files, {errors} errors")
    print(f"{'='*60}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest agent skills into Elasticsearch"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and recreate indices before ingesting (use when index settings change)"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Get configuration from environment
    es_url = os.getenv("ELASTIC_SEARCH_URL")
    api_key = os.getenv("ELASTIC_API_KEY")

    if not es_url or not api_key:
        print("Error: ELASTIC_SEARCH_URL and ELASTIC_API_KEY must be set in environment.")
        print("Create a .env file with these values or export them.")
        sys.exit(1)

    # Setup paths
    project_root = Path(__file__).parent.parent
    skills_dir = project_root / "sample_skills"
    config_dir = project_root / "config"

    # Initialize Elasticsearch client
    print("Connecting to Elasticsearch...")
    es = Elasticsearch(
        hosts=[es_url],
        api_key=api_key
    )

    # Verify connection
    if not es.ping():
        print("Error: Could not connect to Elasticsearch.")
        sys.exit(1)

    print("Connected successfully.")

    if args.recreate:
        print("\n⚠️  Recreate mode: indices will be deleted and recreated.\n")

    # Ensure indexes exist
    ensure_index(es, "agent_skills", config_dir, recreate=args.recreate)
    ensure_files_index(es, "agent_skill_files", config_dir, recreate=args.recreate)

    # Ingest skills and files
    ingest_skills(skills_dir, es, "agent_skills", "agent_skill_files")


if __name__ == "__main__":
    main()
