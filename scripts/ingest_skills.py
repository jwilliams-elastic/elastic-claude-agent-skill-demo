#!/usr/bin/env python3
"""
Ingestion Script for Agent Skills Repository
Indexes skill documents from sample_skills directory into Elasticsearch
Uses semantic_text with automatic inference for embeddings
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
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
    doc = {
        "skill_id": skill_metadata["skill_id"],
        "name": skill_metadata["title"],  # Maps to 'name' field in index
        "description": skill_metadata["description"],
        "short_description": skill_metadata["description"][:200] if len(skill_metadata["description"]) > 200 else skill_metadata["description"],
        "domain": skill_metadata["domain"],
        "tags": skill_metadata["tags"],
        "author": "system",  # Default author
        "skill_markdown": skill_metadata["content"],  # Full SKILL.md content
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


def ensure_index(es: Elasticsearch, index_name: str, config_dir: Path) -> None:
    """
    Create index with proper mappings and settings if it doesn't exist.

    Args:
        es: Elasticsearch client
        index_name: Name of the index
        config_dir: Path to config directory
    """
    if es.indices.exists(index=index_name):
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


def ingest_skills(
    skills_dir: Path,
    es_client: Elasticsearch,
    index_name: str = "agent_skills"
) -> None:
    """
    Main ingestion function.

    Args:
        skills_dir: Path to sample_skills directory
        es_client: Elasticsearch client
        index_name: Target index name
    """
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")

    # Get all subdirectories (each is a skill)
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]

    if not skill_dirs:
        print("No skills found in directory.")
        return

    print(f"Found {len(skill_dirs)} skills to ingest.")

    ingested = 0
    errors = 0

    for skill_dir in skill_dirs:
        try:
            print(f"\nProcessing: {skill_dir.name}")

            # Parse metadata
            metadata = parse_skill_metadata(skill_dir)

            # Create document
            doc = create_skill_document(metadata)

            # Index document
            response = es_client.index(
                index=index_name,
                id=metadata["skill_id"],
                document=doc
            )

            print(f"  ✓ Indexed: {metadata['title']} (ID: {metadata['skill_id']})")
            print(f"    Domain: {metadata['domain']}, Tags: {', '.join(metadata['tags'])}")
            ingested += 1

        except Exception as e:
            print(f"  ✗ Error processing {skill_dir.name}: {e}")
            errors += 1

    print(f"\n{'='*60}")
    print(f"Ingestion complete: {ingested} succeeded, {errors} failed")
    print(f"{'='*60}")


def main():
    """Main entry point."""
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

    # Ensure index exists
    ensure_index(es, "agent_skills", config_dir)

    # Ingest skills
    ingest_skills(skills_dir, es, "agent_skills")


if __name__ == "__main__":
    main()
