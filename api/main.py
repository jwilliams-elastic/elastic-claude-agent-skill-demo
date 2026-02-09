"""
Data Operations API Service
RESTful API to expose setup-skills, teardown-skills, and granular ingestion operations.
Synchronous operations - all endpoints wait for completion before returning.
"""

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_ROOT = PROJECT_ROOT / "skills"
PRODUCTION_SKILLS_DIR = SKILLS_ROOT / "production-skills"
STAGED_SKILLS_DIR = SKILLS_ROOT / "staged-skills"
DEV_SKILLS_DIR = SKILLS_ROOT / "dev-skills"
CONFIG_DIR = PROJECT_ROOT / "config"

# API Key Security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


# =============================================================================
# Authentication
# =============================================================================

def get_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """Validate API key from header."""
    expected_key = os.getenv("API_SERVICE_KEY")
    if not expected_key:
        # If no key configured, allow requests (for development)
        return ""
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


def get_es_client() -> Elasticsearch:
    """Create and return an Elasticsearch client."""
    es_url = os.getenv("ELASTIC_SEARCH_URL")
    api_key = os.getenv("ELASTIC_API_KEY")

    if not es_url or not api_key:
        logger.error("Missing ELASTIC_SEARCH_URL or ELASTIC_API_KEY environment variables")
        raise Exception("ELASTIC_SEARCH_URL and ELASTIC_API_KEY must be configured")

    client = Elasticsearch(hosts=[es_url], api_key=api_key)

    if not client.ping():
        logger.error("Failed to connect to Elasticsearch")
        raise Exception("Cannot connect to Elasticsearch")

    return client


# =============================================================================
# Response Models
# =============================================================================

class OperationDetails(BaseModel):
    indexes_created: List[str] = []
    indexes_deleted: List[str] = []
    skills_created: List[str] = []
    skills_deleted: List[str] = []
    files_indexed: int = 0


class OperationResponse(BaseModel):
    status: str
    message: str
    summary: str
    details: OperationDetails


class UpdateSkillsRequest(BaseModel):
    skills_path: Optional[str] = None


class IngestRequest(BaseModel):
    folder_name: str
    target_index: Optional[str] = "agent_skills"


class IngestResponse(BaseModel):
    status: str
    message: str
    folder: str
    documents_indexed: int
    files_indexed: int
    files_list: List[str] = []
    errors: int


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Data Operations API",
    description="API service for data operations including setup-skills, teardown-skills, and granular skill ingestion. All operations are synchronous.",
    version="3.0.0",
)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("Data Operations API Service v3.0 starting...")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Production skills directory: {PRODUCTION_SKILLS_DIR}")
    logger.info(f"Staged skills directory: {STAGED_SKILLS_DIR}")
    logger.info(f"Dev skills directory: {DEV_SKILLS_DIR}")
    logger.info("Synchronous mode - all operations wait for completion")
    logger.info("=" * 60)

    # Ensure skills directories exist
    for skills_dir in [PRODUCTION_SKILLS_DIR, STAGED_SKILLS_DIR, DEV_SKILLS_DIR]:
        if not skills_dir.exists():
            skills_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created skills directory at {skills_dir}")


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": get_timestamp()}


@app.post("/api/v1/ops/setup-skills", response_model=OperationResponse)
async def setup_skills(_api_key: str = Depends(get_api_key)):
    """
    Run the full data setup process (synchronous).
    Creates indexes and ingests all skills from production-skills folder.
    Waits for completion and returns the full result.
    """
    logger.info("=" * 60)
    logger.info("SETUP-SKILLS - Starting full data setup process")
    logger.info("=" * 60)

    details = OperationDetails()

    try:
        # Import ingestion modules
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from ingest_skills import (
            ensure_files_index,
            ensure_index,
            ingest_skills,
        )

        logger.info("Connecting to Elasticsearch...")
        es = get_es_client()

        # Create indexes
        logger.info("Creating index 'agent_skills'...")
        index_existed = es.indices.exists(index="agent_skills")
        ensure_index(es, "agent_skills", CONFIG_DIR)
        if not index_existed:
            details.indexes_created.append("agent_skills")
            logger.info("Index 'agent_skills' created")

        logger.info("Creating index 'agent_skill_files'...")
        index_existed = es.indices.exists(index="agent_skill_files")
        ensure_files_index(es, "agent_skill_files", CONFIG_DIR)
        if not index_existed:
            details.indexes_created.append("agent_skill_files")
            logger.info("Index 'agent_skill_files' created")

        # Enumerate skills
        skill_folders = [
            d.name for d in PRODUCTION_SKILLS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        total_skills = len(skill_folders)
        logger.info(f"Found {total_skills} skill folders to ingest")

        # Bulk ingest all skills
        logger.info(f"Bulk ingesting {total_skills} skills...")
        stats = ingest_skills(PRODUCTION_SKILLS_DIR, es, "agent_skills", "agent_skill_files")

        details.skills_created = skill_folders
        details.files_indexed = stats.get("files_indexed", 0) if isinstance(stats, dict) else 0

        # Build response
        summary = f"Ingested {len(details.skills_created)} skills, {details.files_indexed} files"
        message = (
            f"Setup complete. "
            f"Indexes: {details.indexes_created or 'already existed'}. "
            f"Skills: {len(details.skills_created)}. "
            f"Files: {details.files_indexed}."
        )

        logger.info("=" * 60)
        logger.info(f"SETUP-SKILLS - Completed successfully")
        logger.info(f"  Indexes created: {details.indexes_created}")
        logger.info(f"  Skills ingested: {len(details.skills_created)}")
        logger.info(f"  Files indexed: {details.files_indexed}")
        logger.info("=" * 60)

        return OperationResponse(
            status="completed",
            message=message,
            summary=summary,
            details=details,
        )

    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")


@app.post("/api/v1/ops/teardown-skills", response_model=OperationResponse)
async def teardown_skills(_api_key: str = Depends(get_api_key)):
    """
    Run the data cleanup process (synchronous).
    Deletes all indexes and their contents.
    Waits for completion and returns the full result.
    """
    logger.info("=" * 60)
    logger.info("TEARDOWN-SKILLS - Starting cleanup process")
    logger.info("=" * 60)

    details = OperationDetails()

    try:
        logger.info("Connecting to Elasticsearch...")
        es = get_es_client()

        # Get list of skills before deletion
        logger.info("Enumerating existing skills...")
        try:
            if es.indices.exists(index="agent_skills"):
                result = es.search(
                    index="agent_skills",
                    body={"query": {"match_all": {}}, "_source": ["skill_id", "name"]},
                    size=1000,
                )
                details.skills_deleted = [
                    hit["_source"].get("name", hit["_source"].get("skill_id", hit["_id"]))
                    for hit in result["hits"]["hits"]
                ]
                logger.info(f"Found {len(details.skills_deleted)} skills to delete")
        except Exception as e:
            logger.warning(f"Could not enumerate existing skills: {e}")

        # Delete indexes
        indexes = ["agent_skills", "agent_skill_files"]
        skipped = []

        for index in indexes:
            logger.info(f"Deleting index '{index}'...")
            if es.indices.exists(index=index):
                es.indices.delete(index=index)
                details.indexes_deleted.append(index)
                logger.info(f"Index '{index}' deleted")
            else:
                skipped.append(index)
                logger.info(f"Index '{index}' does not exist, skipping")

        # Build response
        summary = f"Deleted {len(details.indexes_deleted)} indexes, {len(details.skills_deleted)} skills"
        message = (
            f"Teardown complete. "
            f"Indexes deleted: {details.indexes_deleted or 'none'}. "
            f"Skills deleted: {len(details.skills_deleted)}."
        )
        if skipped:
            message += f" Skipped (not found): {skipped}."

        logger.info("=" * 60)
        logger.info(f"TEARDOWN-SKILLS - Completed")
        logger.info(f"  Indexes deleted: {details.indexes_deleted}")
        logger.info(f"  Skills deleted: {len(details.skills_deleted)}")
        logger.info("=" * 60)

        return OperationResponse(
            status="completed",
            message=message,
            summary=summary,
            details=details,
        )

    except Exception as e:
        logger.error(f"Teardown failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Teardown failed: {str(e)}")


@app.post("/api/v1/ops/update-skills", response_model=OperationResponse)
async def update_skills(
    request: Optional[UpdateSkillsRequest] = None,
    _api_key: str = Depends(get_api_key),
):
    """
    Ingest all skills from a specified folder (synchronous).
    Scans the directory and ingests any skill folders found.
    Waits for completion and returns the full result.

    Args:
        request: Optional request body with skills_path. If not provided or skills_path is None,
                 defaults to the staged-skills directory.
    """
    # Determine the skills directory to use
    if request and request.skills_path:
        skills_dir = Path(request.skills_path)
        if not skills_dir.is_absolute():
            skills_dir = PROJECT_ROOT / request.skills_path
    else:
        skills_dir = STAGED_SKILLS_DIR

    logger.info("=" * 60)
    logger.info(f"UPDATE-SKILLS - Starting ingestion from {skills_dir}")
    logger.info("=" * 60)

    details = OperationDetails()

    try:
        # Check if skills folder exists
        if not skills_dir.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Skills directory not found: {skills_dir}",
            )

        # Get all subdirectories (each is a skill)
        skill_dirs = [
            d for d in skills_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        if not skill_dirs:
            logger.info(f"No skills found in {skills_dir}")
            return OperationResponse(
                status="completed",
                message=f"No skills found in {skills_dir}. Add skill directories to ingest them.",
                summary="No skills to ingest",
                details=details,
            )

        total_skills = len(skill_dirs)
        logger.info(f"Found {total_skills} skill(s) to ingest: {[d.name for d in skill_dirs]}")

        # Import ingestion functions
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from ingest_skills import (
            create_skill_document,
            index_skill_files,
            parse_skill_metadata,
        )

        logger.info("Connecting to Elasticsearch...")
        es = get_es_client()

        skills_failed = []

        for i, skill_dir in enumerate(skill_dirs, 1):
            skill_name = skill_dir.name
            logger.info(f"[{i}/{total_skills}] Processing skill: {skill_name}")

            try:
                # Parse metadata
                metadata = parse_skill_metadata(skill_dir)
                logger.info(f"  Parsed metadata for: {metadata.get('title', skill_name)}")

                # Create and index skill document
                doc = create_skill_document(metadata)
                es.index(
                    index="agent_skills",
                    id=metadata["skill_id"],
                    document=doc,
                )
                logger.info(f"  Indexed skill document")

                # Index skill files
                files_count = index_skill_files(
                    skill_dir=skill_dir,
                    skill_id=metadata["skill_id"],
                    es_client=es,
                    index_name="agent_skill_files",
                )
                details.files_indexed += files_count
                logger.info(f"  Indexed {files_count} files")

                details.skills_created.append(skill_name)
                logger.info(f"  ✓ Successfully ingested: {skill_name}")

            except Exception as e:
                logger.error(f"  ✗ Failed to ingest {skill_name}: {str(e)}")
                skills_failed.append(f"{skill_name}: {str(e)}")

        # Refresh indexes
        logger.info("Refreshing indexes...")
        es.indices.refresh(index="agent_skills")
        es.indices.refresh(index="agent_skill_files")

        # Build response
        summary = f"Ingested {len(details.skills_created)} skills, {details.files_indexed} files"
        message = f"Update complete. Skills ingested: {len(details.skills_created)}. Files: {details.files_indexed}."
        if skills_failed:
            message += f" Failed: {len(skills_failed)} - {skills_failed}"

        logger.info("=" * 60)
        logger.info(f"UPDATE-SKILLS - Completed")
        logger.info(f"  Skills ingested: {len(details.skills_created)}")
        logger.info(f"  Skills failed: {len(skills_failed)}")
        logger.info(f"  Files indexed: {details.files_indexed}")
        logger.info("=" * 60)

        return OperationResponse(
            status="completed",
            message=message,
            summary=summary,
            details=details,
        )

    except Exception as e:
        logger.error(f"Update-skills failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update-skills failed: {str(e)}")


@app.post("/api/v1/ingest/folder", response_model=IngestResponse)
async def ingest_folder(request: IngestRequest, _api_key: str = Depends(get_api_key)):
    """
    Load data from a specific production-skills subfolder.
    """
    folder_name = request.folder_name
    target_path = PRODUCTION_SKILLS_DIR / folder_name

    logger.info("=" * 60)
    logger.info(f"INGEST FOLDER - Starting ingestion for '{folder_name}'")
    logger.info("=" * 60)

    # Validate folder exists
    if not target_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Directory '{folder_name}' not found in production-skills.",
        )

    if not target_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_name}' is not a directory.",
        )

    try:
        # Import ingestion functions
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from ingest_skills import (
            create_skill_document,
            index_skill_files,
            parse_skill_metadata,
        )

        es = get_es_client()

        # Parse and index the skill metadata
        metadata = parse_skill_metadata(target_path)
        doc = create_skill_document(metadata)

        target_index = request.target_index or "agent_skills"
        es.index(
            index=target_index,
            id=metadata["skill_id"],
            document=doc,
        )

        # Index all skill files
        files_list = [
            f.name for f in target_path.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]

        files_count = index_skill_files(
            skill_dir=target_path,
            skill_id=metadata["skill_id"],
            es_client=es,
            index_name="agent_skill_files",
        )

        logger.info("=" * 60)
        logger.info(f"INGEST FOLDER - Completed. Documents: 1, Files: {files_count}")
        logger.info("=" * 60)

        return IngestResponse(
            status="success",
            message=f"Ingested '{folder_name}' to '{target_index}'. Files: {files_list}.",
            folder=folder_name,
            documents_indexed=1,
            files_indexed=files_count,
            files_list=files_list,
            errors=0,
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
