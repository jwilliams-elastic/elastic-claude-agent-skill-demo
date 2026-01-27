"""
Data Operations API Service
RESTful API to expose setup, teardown, and granular ingestion operations.
Supports async background tasks with job polling for long-running operations.
"""

import logging
import os
import sys
import threading
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Security
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
SAMPLE_SKILLS_DIR = PROJECT_ROOT / "sample_skills"
NEW_SKILLS_DIR = PROJECT_ROOT / "new_skills"
CONFIG_DIR = PROJECT_ROOT / "config"

# API Key Security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


# =============================================================================
# Job Tracking System
# =============================================================================

class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OperationDetails(BaseModel):
    indexes_created: List[str] = []
    indexes_deleted: List[str] = []
    mcp_tools_created: List[str] = []
    mcp_tools_deleted: List[str] = []
    skills_created: List[str] = []
    skills_deleted: List[str] = []


class JobInfo(BaseModel):
    job_id: str
    job_type: str
    status: JobStatus
    progress: str = ""
    message: str = ""
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    details: Optional[OperationDetails] = None
    error: Optional[str] = None


# In-memory job storage (use Redis or DB for production)
jobs: Dict[str, JobInfo] = {}
jobs_lock = threading.Lock()


def create_job(job_type: str) -> JobInfo:
    """Create a new job and return its info."""
    job_id = str(uuid.uuid4())[:8]
    now = get_timestamp()
    job = JobInfo(
        job_id=job_id,
        job_type=job_type,
        status=JobStatus.PENDING,
        progress="Job created, waiting to start",
        created_at=now,
        updated_at=now,
    )
    with jobs_lock:
        jobs[job_id] = job
    logger.info(f"Created job {job_id} of type '{job_type}'")
    return job


def update_job(
    job_id: str,
    status: Optional[JobStatus] = None,
    progress: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[OperationDetails] = None,
    error: Optional[str] = None,
):
    """Update job status and progress."""
    with jobs_lock:
        if job_id not in jobs:
            return
        job = jobs[job_id]
        if status:
            job.status = status
        if progress:
            job.progress = progress
        if message:
            job.message = message
        if details:
            job.details = details
        if error:
            job.error = error
        job.updated_at = get_timestamp()
        if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            job.completed_at = get_timestamp()
        logger.info(f"Job {job_id}: {status or job.status} - {progress or job.progress}")


def get_job(job_id: str) -> Optional[JobInfo]:
    """Get job info by ID."""
    with jobs_lock:
        return jobs.get(job_id)


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
    logger.info("Creating Elasticsearch client...")
    es_url = os.getenv("ELASTIC_SEARCH_URL")
    api_key = os.getenv("ELASTIC_API_KEY")

    if not es_url or not api_key:
        logger.error("Missing ELASTIC_SEARCH_URL or ELASTIC_API_KEY environment variables")
        raise Exception("ELASTIC_SEARCH_URL and ELASTIC_API_KEY must be configured")

    client = Elasticsearch(hosts=[es_url], api_key=api_key)
    logger.info(f"Connecting to Elasticsearch at {es_url}")

    if not client.ping():
        logger.error("Failed to connect to Elasticsearch")
        raise Exception("Cannot connect to Elasticsearch")

    logger.info("Successfully connected to Elasticsearch")
    return client


# =============================================================================
# Response Models
# =============================================================================

class JobAcceptedResponse(BaseModel):
    status: str = "accepted"
    job_id: str
    message: str
    poll_url: str


class OperationResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    details: OperationDetails


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


class BatchIngestResponse(BaseModel):
    status: str
    message: str
    skills_ingested: List[str] = []
    skills_failed: List[str] = []
    total_documents: int
    total_files: int
    errors: int


class ErrorResponse(BaseModel):
    status: str
    message: str


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Data Operations API",
    description="API service for data operations including setup, teardown, and granular skill ingestion. Long-running operations use async jobs with polling.",
    version="2.0.0",
)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("Data Operations API Service v2.0 starting...")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Sample skills directory: {SAMPLE_SKILLS_DIR}")
    logger.info(f"New skills directory: {NEW_SKILLS_DIR}")
    logger.info(f"Config directory: {CONFIG_DIR}")
    logger.info("Async job processing enabled")
    logger.info("=" * 60)

    # Ensure new_skills directory exists
    if not NEW_SKILLS_DIR.exists():
        NEW_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created new_skills directory at {NEW_SKILLS_DIR}")


# =============================================================================
# Background Task Functions
# =============================================================================

def run_setup_task(job_id: str):
    """Background task to run the setup process."""
    logger.info("=" * 60)
    logger.info(f"SETUP ENVIRONMENT [Job {job_id}] - Starting full data setup process")
    logger.info("=" * 60)

    details = OperationDetails()

    try:
        update_job(job_id, status=JobStatus.IN_PROGRESS, progress="Importing modules...")

        # Import ingestion modules
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from ingest_skills import (
            Elasticsearch,
            ensure_files_index,
            ensure_index,
            ingest_skills,
        )

        update_job(job_id, progress="Connecting to Elasticsearch...")
        es_url = os.getenv("ELASTIC_SEARCH_URL")
        api_key = os.getenv("ELASTIC_API_KEY")
        es = Elasticsearch(hosts=[es_url], api_key=api_key)

        if not es.ping():
            raise Exception("Cannot connect to Elasticsearch")

        # Create indexes
        update_job(job_id, progress="Creating index 'agent_skills'...")
        index_existed = es.indices.exists(index="agent_skills")
        ensure_index(es, "agent_skills", CONFIG_DIR)
        if not index_existed:
            details.indexes_created.append("agent_skills")
            logger.info("Index 'agent_skills' created")

        update_job(job_id, progress="Creating index 'agent_skill_files'...")
        index_existed = es.indices.exists(index="agent_skill_files")
        ensure_files_index(es, "agent_skill_files", CONFIG_DIR)
        if not index_existed:
            details.indexes_created.append("agent_skill_files")
            logger.info("Index 'agent_skill_files' created")

        # Enumerate skills for tracking
        skill_folders = [
            d.name for d in SAMPLE_SKILLS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        total_skills = len(skill_folders)
        logger.info(f"Found {total_skills} skill folders to ingest")

        # Use bulk ingestion for better performance
        update_job(job_id, progress=f"Bulk ingesting {total_skills} skills...")

        # Call the optimized bulk ingest function
        ingest_skills(SAMPLE_SKILLS_DIR, es, "agent_skills", "agent_skill_files")

        # All skills processed via bulk
        details.skills_created = skill_folders
        logger.info(f"Bulk ingestion complete for {total_skills} skills")

        # Complete
        message = (
            f"Environment setup complete. "
            f"Indexes: {details.indexes_created or 'none (already existed)'}. "
            f"Skills ingested: {len(details.skills_created)}."
        )

        update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress="Setup complete",
            message=message,
            details=details,
        )

        logger.info("=" * 60)
        logger.info(f"SETUP ENVIRONMENT [Job {job_id}] - Completed successfully")
        logger.info(f"  Indexes created: {details.indexes_created}")
        logger.info(f"  Skills created: {len(details.skills_created)} skills")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Setup failed with error: {str(e)}")
        update_job(
            job_id,
            status=JobStatus.FAILED,
            progress="Setup failed",
            error=str(e),
            details=details,
        )


def run_teardown_task(job_id: str):
    """Background task to run the teardown process."""
    logger.info("=" * 60)
    logger.info(f"TEARDOWN ENVIRONMENT [Job {job_id}] - Starting cleanup process")
    logger.info("=" * 60)

    details = OperationDetails()

    try:
        update_job(job_id, status=JobStatus.IN_PROGRESS, progress="Connecting to Elasticsearch...")

        es = get_es_client()

        # Get list of skills before deletion
        update_job(job_id, progress="Enumerating existing skills...")
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
            update_job(job_id, progress=f"Deleting index '{index}'...")
            if es.indices.exists(index=index):
                es.indices.delete(index=index)
                details.indexes_deleted.append(index)
                logger.info(f"Index '{index}' deleted")
            else:
                skipped.append(index)
                logger.info(f"Index '{index}' does not exist, skipping")

        # Complete
        message = (
            f"Environment teardown complete. "
            f"Indexes deleted: {details.indexes_deleted or 'none'}. "
            f"Skills deleted: {len(details.skills_deleted)}."
        )
        if skipped:
            message += f" Skipped (not found): {skipped}."

        update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress="Teardown complete",
            message=message,
            details=details,
        )

        logger.info("=" * 60)
        logger.info(f"TEARDOWN ENVIRONMENT [Job {job_id}] - Completed")
        logger.info(f"  Indexes deleted: {details.indexes_deleted}")
        logger.info(f"  Skills deleted: {len(details.skills_deleted)} skills")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Teardown failed with error: {str(e)}")
        update_job(
            job_id,
            status=JobStatus.FAILED,
            progress="Teardown failed",
            error=str(e),
            details=details,
        )


def run_update_skills_task(job_id: str):
    """Background task to ingest skills from new_skills folder."""
    logger.info("=" * 60)
    logger.info(f"UPDATE SKILLS [Job {job_id}] - Starting ingestion from new_skills folder")
    logger.info("=" * 60)

    details = OperationDetails()

    try:
        update_job(job_id, status=JobStatus.IN_PROGRESS, progress="Checking new_skills folder...")

        # Check if new_skills folder exists
        if not NEW_SKILLS_DIR.exists():
            logger.info(f"Creating new_skills directory at {NEW_SKILLS_DIR}")
            NEW_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

        # Get all subdirectories (each is a skill)
        skill_dirs = [
            d for d in NEW_SKILLS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        if not skill_dirs:
            logger.info("No skills found in new_skills folder")
            update_job(
                job_id,
                status=JobStatus.COMPLETED,
                progress="No skills to ingest",
                message="No skills found in new_skills folder. Add skill directories to new_skills/ to ingest them.",
                details=details,
            )
            return

        total_skills = len(skill_dirs)
        logger.info(f"Found {total_skills} skill(s) to ingest: {[d.name for d in skill_dirs]}")
        update_job(job_id, progress=f"Found {total_skills} skill(s) to ingest...")

        # Import ingestion functions
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from ingest_skills import (
            create_skill_document,
            index_skill_files,
            parse_skill_metadata,
        )

        update_job(job_id, progress="Connecting to Elasticsearch...")
        es = get_es_client()

        skills_failed = []
        total_files = 0

        for i, skill_dir in enumerate(skill_dirs, 1):
            skill_name = skill_dir.name
            update_job(job_id, progress=f"Ingesting skill {i}/{total_skills}: {skill_name}")
            logger.info(f"Processing skill: {skill_name}")

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
                total_files += files_count
                logger.info(f"  Indexed {files_count} files")

                details.skills_created.append(skill_name)
                logger.info(f"  ✓ Successfully ingested: {skill_name}")

            except Exception as e:
                logger.error(f"  ✗ Failed to ingest {skill_name}: {str(e)}")
                skills_failed.append(f"{skill_name}: {str(e)}")

        # Refresh index to make documents searchable
        update_job(job_id, progress="Refreshing indexes...")
        es.indices.refresh(index="agent_skills")
        es.indices.refresh(index="agent_skill_files")

        # Complete
        message = f"Ingested {len(details.skills_created)} skill(s) from new_skills folder. Total files: {total_files}."
        if skills_failed:
            message += f" {len(skills_failed)} skill(s) failed: {skills_failed}"

        update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress="Update complete",
            message=message,
            details=details,
        )

        logger.info("=" * 60)
        logger.info(f"UPDATE SKILLS [Job {job_id}] - Completed")
        logger.info(f"  Skills ingested: {len(details.skills_created)}")
        logger.info(f"  Skills failed: {len(skills_failed)}")
        logger.info(f"  Total files: {total_files}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Update-skills failed with error: {str(e)}")
        update_job(
            job_id,
            status=JobStatus.FAILED,
            progress="Update failed",
            error=str(e),
            details=details,
        )


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": get_timestamp()}


@app.get("/api/v1/jobs", response_model=List[JobInfo])
async def list_jobs(_api_key: str = Depends(get_api_key)):
    """List all jobs."""
    with jobs_lock:
        return list(jobs.values())


@app.get("/api/v1/jobs/{job_id}", response_model=JobInfo)
async def get_job_status(job_id: str, _api_key: str = Depends(get_api_key)):
    """Get status of a specific job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job


@app.post("/api/v1/ops/setup", response_model=JobAcceptedResponse)
async def setup_environment(
    background_tasks: BackgroundTasks,
    _api_key: str = Depends(get_api_key),
):
    """
    Trigger the full data setup process (async).
    Returns immediately with a job ID. Poll /api/v1/jobs/{job_id} for status.
    """
    job = create_job("setup")
    background_tasks.add_task(run_setup_task, job.job_id)

    return JobAcceptedResponse(
        status="accepted",
        job_id=job.job_id,
        message="Setup job started. Poll the job endpoint for status.",
        poll_url=f"/api/v1/jobs/{job.job_id}",
    )


@app.post("/api/v1/ops/teardown", response_model=JobAcceptedResponse)
async def teardown_environment(
    background_tasks: BackgroundTasks,
    _api_key: str = Depends(get_api_key),
):
    """
    Trigger the data cleanup process (async).
    Returns immediately with a job ID. Poll /api/v1/jobs/{job_id} for status.
    """
    job = create_job("teardown")
    background_tasks.add_task(run_teardown_task, job.job_id)

    return JobAcceptedResponse(
        status="accepted",
        job_id=job.job_id,
        message="Teardown job started. Poll the job endpoint for status.",
        poll_url=f"/api/v1/jobs/{job.job_id}",
    )


@app.post("/api/v1/ingest/folder", response_model=IngestResponse)
async def ingest_folder(request: IngestRequest, _api_key: str = Depends(get_api_key)):
    """
    Load data from a specific sample_skills subfolder.
    This is a synchronous operation (single folder is fast enough).
    """
    folder_name = request.folder_name
    target_path = SAMPLE_SKILLS_DIR / folder_name

    logger.info("=" * 60)
    logger.info(f"INGEST FOLDER - Starting ingestion for '{folder_name}'")
    logger.info("=" * 60)

    # Validate folder exists
    logger.info(f"Validating folder path: {target_path}")
    if not target_path.exists():
        logger.error(f"Directory '{folder_name}' not found in sample_skills")
        raise HTTPException(
            status_code=400,
            detail=f"Directory '{folder_name}' not found in sample_skills.",
        )

    if not target_path.is_dir():
        logger.error(f"'{folder_name}' is not a directory")
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_name}' is not a directory.",
        )

    logger.info(f"Folder '{folder_name}' validated successfully")

    try:
        # Import ingestion functions
        logger.info("Importing ingestion functions...")
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from ingest_skills import (
            create_skill_document,
            index_skill_files,
            parse_skill_metadata,
        )
        logger.info("Ingestion functions imported")

        es = get_es_client()

        # Parse and index the skill metadata
        logger.info(f"Parsing skill metadata from {target_path}...")
        metadata = parse_skill_metadata(target_path)
        logger.info(f"Parsed metadata for skill: {metadata.get('skill_id', 'unknown')}")

        logger.info("Creating skill document...")
        doc = create_skill_document(metadata)
        logger.info("Skill document created")

        # Index the skill document
        target_index = request.target_index or "agent_skills"
        logger.info(f"Indexing skill document to '{target_index}' with ID '{metadata['skill_id']}'...")
        es.index(
            index=target_index,
            id=metadata["skill_id"],
            document=doc,
        )
        logger.info("Skill document indexed successfully")

        # Index all skill files and track filenames
        logger.info("Indexing skill files to 'agent_skill_files'...")
        files_list = [
            f.name for f in target_path.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        logger.info(f"Found {len(files_list)} files to index: {files_list}")

        files_count = index_skill_files(
            skill_dir=target_path,
            skill_id=metadata["skill_id"],
            es_client=es,
            index_name="agent_skill_files",
        )
        logger.info(f"Indexed {files_count} skill files")

        logger.info("=" * 60)
        logger.info(f"INGEST FOLDER - Completed. Documents: 1, Files: {files_count}")
        logger.info("=" * 60)

        message = (
            f"Ingestion complete for '{folder_name}'. "
            f"Skill document indexed to '{target_index}'. "
            f"Files indexed: {files_list}."
        )

        return IngestResponse(
            status="success",
            message=message,
            folder=folder_name,
            documents_indexed=1,
            files_indexed=files_count,
            files_list=files_list,
            errors=0,
        )

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/api/v1/ops/update-skills", response_model=JobAcceptedResponse)
async def update_skills(
    background_tasks: BackgroundTasks,
    _api_key: str = Depends(get_api_key),
):
    """
    Ingest all skills from the new_skills folder (async).
    Scans the new_skills directory and ingests any skill folders found.
    Returns immediately with a job ID. Poll /api/v1/jobs/{job_id} for status.
    Use operation="update-skills" in the workflow to invoke this endpoint.
    """
    job = create_job("update-skills")
    background_tasks.add_task(run_update_skills_task, job.job_id)

    return JobAcceptedResponse(
        status="accepted",
        job_id=job.job_id,
        message="Update-skills job started. Poll the job endpoint for status.",
        poll_url=f"/api/v1/jobs/{job.job_id}",
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
