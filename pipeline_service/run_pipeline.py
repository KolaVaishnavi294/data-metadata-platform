import pandas as pd
import requests
import uuid
import datetime

from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from openlineage.client.dataset import Dataset as OLDataset

# API URL (Docker service name)
API_URL = "http://api:5000"

# Dataset path
DATASET_PATH = "/data/openfoodfacts_sample.csv"

# Global Run ID
RUN_ID = str(uuid.uuid4())

client = OpenLineageClient(url=API_URL)


def load_dataset():
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded successfully ({len(df)} rows)")
    return df


def extract_schema(df):
    print("Extracting schema...")

    schema = []

    for col in df.columns:
        schema.append({
            "name": col,
            "type": str(df[col].dtype)
        })

    return schema


def compute_statistics(df):
    print("Computing statistics...")

    stats = {}

    for col in df.columns:
        stats[col] = {
            "null_fraction": float(df[col].isnull().mean()),
            "distinct_count": int(df[col].nunique())
        }

    return stats


# ---------------------------------------------------------------------
# Replacement for Soda Core
# ---------------------------------------------------------------------
def run_data_quality_checks(df):

    print("Running Data Quality Checks...")

    dq_results = {}

    # Dataset not empty
    passed = len(df) > 0

    dq_results["dataset_not_empty"] = {
        "success": passed,
        "observed_value": len(df)
    }

    # product_name not null
    if "product_name" in df.columns:
        nulls = int(df["product_name"].isnull().sum())

        dq_results["product_name_not_null"] = {
            "success": nulls == 0,
            "observed_value": nulls
        }

    # brand not null
    if "brand" in df.columns:
        nulls = int(df["brand"].isnull().sum())

        dq_results["brand_not_null"] = {
            "success": nulls == 0,
            "observed_value": nulls
        }

    # energy_100g >= 0
    if "energy_100g" in df.columns:

        invalid = int((df["energy_100g"] < 0).fillna(False).sum())

        dq_results["energy_non_negative"] = {
            "success": invalid == 0,
            "observed_value": invalid
        }

    # Duplicate product names
    if "product_name" in df.columns:

        duplicates = int(df["product_name"].duplicated().sum())

        dq_results["duplicate_product_names"] = {
            "success": duplicates == 0,
            "observed_value": duplicates
        }

    print("\nData Quality Results")

    for k, v in dq_results.items():
        print(f"{k}: {v}")

    return dq_results


def register_dataset(schema):

    print("Registering dataset...")

    payload = {
        "name": "openfoodfacts",
        "uri": "file:///data/openfoodfacts_sample.csv",
        "description": "Open Food Facts dataset",
        "schema": schema
    }

    response = requests.post(
        f"{API_URL}/datasets",
        json=payload
    )

    if response.status_code == 201:

        dataset_id = response.json()["dataset_id"]

        print("Dataset Registered")

        return dataset_id

    print("Registration Failed")
    print(response.text)

    return None


def store_dq_results(dataset_id, dq_results):

    print("Sending DQ results...")

    payload = {
        "dataset_id": dataset_id,
        "dq_results": dq_results
    }

    response = requests.post(
        f"{API_URL}/runs/{RUN_ID}/dq_results",
        json=payload
    )

    print("DQ API Status:", response.status_code)

    if response.text:
        print(response.text)


def emit_lineage_event(
        state,
        dataset_name_in="openfoodfacts",
        dataset_name_out="processed_openfoodfacts"
):

    print(f"Emitting OpenLineage Event : {state}")

    event = RunEvent(
        eventType=state,
        eventTime=datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        run=Run(runId=RUN_ID),
        job=Job(
            namespace="food_pipeline",
            name="openfoodfacts_ingestion"
        ),
        inputs=[
            OLDataset(
                namespace="food_pipeline",
                name=dataset_name_in
            )
        ],
        outputs=[
            OLDataset(
                namespace="food_pipeline",
                name=dataset_name_out
            )
        ],
        producer="openlineage-python"
    )

    client.emit(event)


def main():

    emit_lineage_event(RunState.START)

    try:

        df = load_dataset()

        dq_results = run_data_quality_checks(df)

        schema = extract_schema(df)

        print("\nSchema")
        print(schema)

        stats = compute_statistics(df)

        print("\nStatistics")
        print(stats)

        dataset_id = register_dataset(schema)

        if dataset_id:

            store_dq_results(
                dataset_id,
                dq_results
            )

            emit_lineage_event(RunState.COMPLETE)

            print("\nPipeline Completed Successfully")

        else:

            emit_lineage_event(RunState.FAIL)

            print("\nDataset Registration Failed")

    except Exception as e:

        print("\nPipeline Failed")

        print(e)

        emit_lineage_event(RunState.FAIL)


if __name__ == "__main__":
    main()