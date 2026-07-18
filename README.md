# Data Metadata Platform with Flask, PostgreSQL, and OpenLineage

## Project Overview

This project implements a **mini data platform** designed to demonstrate core concepts of modern **data governance and data engineering**. The system provides a metadata catalog, data quality monitoring, and data lineage tracking for datasets processed through a data pipeline.

The platform allows users to:

- Register datasets and schema metadata
- Track column-level statistics
- Execute data quality checks
- Capture data lineage events
- Query dataset metadata through REST APIs

The system is fully containerized using **Docker** and orchestrated using **Docker Compose**.

---

## Architecture

The architecture consists of three major components:

      +---------------------+
      |   Data Pipeline     |
      |  (Python + Pandas)  |
      +----------+----------+
                 |
                 | REST API
                 v
       +--------------------+
       |     Flask API      |
       |  Metadata Catalog  |
       +---------+----------+
                 |
                 |
                 v
          +------------+
          | PostgreSQL |
          | Metadata DB|
          +------------+

         OpenLineage Events
                |
                v
        +----------------+
        | Lineage Graph  |
        +----------------+

---

## Folder Structure

```bash
data-metadata-platform
│
├── api_service
│ ├── routes
│ │ ├── datasets.py
│ │ ├── lineage.py
│ │ └── openlineage.py
│ ├── app.py
│ ├── database.py
│ ├── models.py
│ └── Dockerfile
│
├── pipeline_service
│ ├── run_pipeline.py
│ ├── dq_checks.yml
│ └── Dockerfile
│
├── data
│ └── openfoodfacts_sample.csv
│
├── db_init
│ └── schema.sql
│
├── examples
│ ├── openlineage_start.json
│ └── openlineage_complete.json
│
├── tests
│ └── test_api.py
│
├── docker-compose.yml
├── submission.yml
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd data-metadata-platform
```

---

### 2. Start the Platform

```bash
docker-compose up --build
```

This starts:

- PostgreSQL database
- Flask metadata API
- Pipeline environment

---

### 3. Verify API

Open:


http://localhost:5000/search?q=test


---

## Running the Pipeline

To run the data ingestion pipeline:

```bash
docker-compose run pipeline python run_pipeline.py
```

The pipeline performs the following steps:

1. Loads the dataset
2. Extracts dataset schema
3. Computes column statistics
4. Runs data quality checks
5. Registers dataset metadata in the API
6. Emits OpenLineage events

---

## API Documentation

### Register Dataset


POST /datasets


Registers a dataset and its schema.

Example request:

```json
{
  "name": "openfoodfacts",
  "uri": "file:///data/openfoodfacts_sample.csv",
  "description": "Open Food Facts dataset",
  "schema": [
    {"name": "product_name", "type": "string"},
    {"name": "brand", "type": "string"}
  ]
}
```
#### Get Dataset Metadata
```bash
GET /datasets/<dataset_id>
```
Returns dataset metadata including schema information.

#### Search Datasets
```bash
GET /search?q=<dataset_name>
```
Search datasets by name.

#### Get Dataset Lineage
```bash
GET /datasets/<dataset_id>/lineage
```
Returns upstream and downstream dataset relationships.

#### Ingest OpenLineage Event
```bash
POST /openlineage/events
```
Consumes lineage events emitted by the pipeline.

---

### Data Quality Rules

- The pipeline executes multiple data quality checks to ensure reliability of the dataset:

- Dataset must not be empty

- product_name must not contain null values

- brand must not contain null values

- energy_100g must be greater than or equal to 0

- Duplicate product names are not allowed

These checks help ensure data integrity and reliability.

---

### Lineage Tracking

The pipeline emits OpenLineage events representing the lifecycle of data processing jobs.

#### Event types:

- START – pipeline execution begins

- COMPLETE – pipeline finished successfully

- FAIL – pipeline execution failed

Example event:

{
  "eventType": "START",
  "job": {
    "namespace": "food_pipeline",
    "name": "openfoodfacts_ingestion"
  },
  "inputs": [
    {"name": "openfoodfacts"}
  ],
  "outputs": [
    {"name": "processed_openfoodfacts"}
  ]
}

These events are captured by the API and used to construct the data lineage graph.

---

## Testing the API

Run the automated API tests:
```bash
python tests/test_api.py
```
#### Expected output:

All API tests passed successfully

---

## Technologies Used

- Python

- Flask

- PostgreSQL

- Docker & Docker Compose

- Pandas

- OpenLineage

- REST APIs

---

## Conclusion

This project demonstrates the design and implementation of a data metadata platform capable of managing dataset metadata, monitoring data quality, and tracking data lineage. It simulates core capabilities used in real-world data governance systems such as DataHub, Amundsen, and OpenMetadata.