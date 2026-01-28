# Product Requirements Document: Data Operations API Service
---

## 1. Executive Summary

Develop a lightweight RESTful API service that exposes existing data operation scripts (`setup.sh`, `teardown.sh`) and implements new logic for granular data ingestion.

Currently, data operations are handled via command-line scripts. To enable orchestration via **Elastic Workflows**, these operations must be accessible via HTTP endpoints. This transition will allow Elastic Workflows to trigger setup, teardown, and specific subset ingestion tasks programmatically.

## 2. Problem Statement

* **Current State:** Data operations require manual execution of shell/python scripts or SSH access to the host machine.
* **Gap:** Elastic Workflows (and other HTTP-based orchestration tools) cannot directly execute local shell scripts or granularly load specific sub-folders of data.
* **Need:** A web server wrapper that translates HTTP requests into script executions and provides a standardized JSON response.

## 3. Goals & Scope

### In Scope

1. **Wrap Existing Logic:** Create API endpoints to trigger the existing `setup.sh` and `teardown.sh` logic.
2. **New Ingestion Logic:** Develop Python logic to iterate through a specific `sample_skills` subfolder and index the contents into Elasticsearch.
3. **Elastic Workflows Compatibility:** Ensure API responses (status codes, JSON payloads, headers) are parsed easily by Elastic Connector clients or Watcher inputs.

### Out of Scope

* Modification of the underlying business logic within `setup.sh` or `teardown.sh` (unless necessary to run in a web context).
* Building a frontend UI.

---

## 4. Functional Requirements

### 4.1. Full Environment Setup

* **Requirement:** The system must provide an endpoint to initialize the environment.
* **Action:** Execute the logic currently contained in `setup.sh`.
* **Behavior:** Must wait for the script to complete before returning a response (unless async processing is implemented).

### 4.2. Full Environment Teardown

* **Requirement:** The system must provide an endpoint to clear data/indexes.
* **Action:** Execute the logic currently contained in `teardown.sh`.
* **Behavior:** Must return a success flag confirming data cleanup.

### 4.3. Granular Skill Ingestion (New Feature)

* **Requirement:** The system must provide an endpoint to load data from a *single* specific subfolder within the `sample_skills` directory.
* **Input:** The endpoint must accept the name of the subfolder (e.g., `cloud_computing`, `hr_management`) as a parameter.
* **Logic:**
1. Validate the subfolder exists.
2. Iterate through files (JSON/CSV) in that subfolder.
3. Bulk index the data into the target Elasticsearch index.


* **Validation:** Return a 400 error if the folder does not exist.

---

## 5. Technical Requirements

### 5.1. Tech Stack

* **Language:** Python (3.9+) recommended for ease of integration with existing Python scripts.
* **Framework:** FastAPI or Flask (lightweight, native JSON support).
* **Elastic Client:** `elasticsearch-py` (official Python client).

### 5.2. Elastic Workflows Compatibility

To ensure seamless integration with Elastic Workflows:

* **Content-Type:** All responses must be `application/json`.
* **Status Codes:** Must use standard HTTP codes (`200` for success, `500` for script failure, `404` for missing resources).
* **Timeouts:** Since `setup.sh` might take time, the API should ideally spawn a background task (using `BackgroundTasks` in FastAPI) and return a Job ID, **OR** ensure the HTTP timeout configuration in Elastic Workflows is set high enough (e.g., 60s+).

### 5.3. Security

* **Authentication:** Basic Auth or API Key header is required to prevent unauthorized triggering of destructive actions (Teardown).

---

## 6. API Specification

### 6.1. Setup Data

* **Endpoint:** `POST /api/v1/ops/setup`
* **Description:** Triggers the full data setup process.
* **Request Body:** None.
* **Response (200 OK):**
```json
{
  "status": "success",
  "message": "Environment setup complete.",
  "timestamp": "2023-10-27T10:00:00Z"
}

```



### 6.2. Teardown Data

* **Endpoint:** `POST /api/v1/ops/teardown`
* **Description:** Triggers the data cleanup process.
* **Request Body:** None.
* **Response (200 OK):**
```json
{
  "status": "success",
  "message": "Environment teardown complete. All indices deleted.",
  "timestamp": "2023-10-27T10:05:00Z"
}

```



### 6.3. Ingest Specific Folder

* **Endpoint:** `POST /api/v1/ingest/folder`
* **Description:** Loads data from a specific `sample_skills` subfolder.
* **Request Body:**
```json
{
  "folder_name": "engineering_skills",
  "target_index": "skills-index-v1"  // Optional, defaults to config
}

```


* **Response (200 OK):**
```json
{
  "status": "success",
  "folder": "engineering_skills",
  "documents_indexed": 150,
  "errors": 0
}

```


* **Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Directory 'engineering_skills' not found in sample_skills."
}

```



---

## 7. Implementation Guidelines (The "New Logic")

For Requirement #3 (Granular Ingestion), the implementation logic should follow this pseudocode:

```python
def ingest_subfolder(folder_name):
    base_path = "./sample_skills"
    target_path = os.path.join(base_path, folder_name)
    
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Folder {folder_name} does not exist")

    documents = []
    # Loop through files in folder
    for filename in os.listdir(target_path):
        if filename.endswith(".json"):
             # Load file content
             # Append to documents list
    
    # Bulk push to Elastic
    response = es_client.bulk(index="target_index", operations=documents)
    return response.count

```

---

## 8. Acceptance Criteria

1. **Setup Test:** Sending a POST to `/setup` results in a populated Elastic instance as verified by Kibana.
2. **Teardown Test:** Sending a POST to `/teardown` results in an empty Elastic instance.
3. **Folder Test:** Sending a POST to `/ingest/folder` with payload `{"folder_name": "marketing"}` adds *only* marketing documents to the index.
4. **Workflow Test:** An Elastic Workflow configured with an HTTP Action can successfully trigger these endpoints and receive a `200 OK` JSON response.

---