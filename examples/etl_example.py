#!/usr/bin/env python3
"""
Example ETL script that emits OpenLineage events to demonstrate data lineage.

This script simulates an ETL job that:
1. Reads from a source dataset (raw_users)
2. Transforms the data
3. Writes to a destination dataset (processed_users)

The script emits OpenLineage events to track the complete lineage chain.
"""

import os
import uuid
from datetime import datetime
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.facet import SchemaDatasetFacet, SchemaField


def main():
    # Initialize OpenLineage client
    # Set MARQUEZ_URL environment variable to point to Marquez API
    # Example: export MARQUEZ_URL=http://localhost:5002
    marquez_url = os.getenv("MARQUEZ_URL", "http://localhost:5002")
    client = OpenLineageClient(url=marquez_url)

    # Define job and run details
    namespace = "flowspec_examples"
    job_name = "user_processing_etl"
    run_id = str(uuid.uuid4())

    # Create Job and Run instances
    job = Job(namespace=namespace, name=job_name)
    run = Run(run_id)

    # Define input dataset schema
    input_schema = SchemaDatasetFacet(
        fields=[
            SchemaField(name="id", type="integer"),
            SchemaField(name="name", type="string"),
            SchemaField(name="email", type="string"),
            SchemaField(name="created_at", type="timestamp")
        ]
    )

    # Define input dataset
    input_dataset = Dataset(
        namespace="postgresql://localhost:5432",
        name="raw.users",
        facets={"schema": input_schema}
    )

    # Define output dataset schema
    output_schema = SchemaDatasetFacet(
        fields=[
            SchemaField(name="user_id", type="integer"),
            SchemaField(name="full_name", type="string"),
            SchemaField(name="email_address", type="string"),
            SchemaField(name="registration_date", type="timestamp")
        ]
    )

    # Define output dataset
    output_dataset = Dataset(
        namespace="postgresql://localhost:5432",
        name="processed.users",
        facets={"schema": output_schema}
    )

    # Emit START event
    print(f"Starting ETL job: {job_name} (run_id: {run_id})")
    start_event = RunEvent(
        eventType=RunState.START,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=run,
        job=job,
        inputs=[input_dataset],
        producer="https://github.com/flowspec/etl_example"
    )
    client.emit(start_event)
    print("✓ Emitted START event")

    # Simulate ETL processing
    print("Processing data...")
    # In a real scenario, this would:
    # 1. Read from raw.users
    # 2. Transform the data (rename columns, filter, etc.)
    # 3. Write to processed.users
    import time
    time.sleep(1)  # Simulate processing time

    # Emit COMPLETE event with inputs and outputs
    print(f"Completing ETL job: {job_name}")
    complete_event = RunEvent(
        eventType=RunState.COMPLETE,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=run,
        job=job,
        inputs=[input_dataset],
        outputs=[output_dataset],
        producer="https://github.com/flowspec/etl_example"
    )
    client.emit(complete_event)
    print("✓ Emitted COMPLETE event with inputs and outputs")
    print(f"✓ Lineage chain: {input_dataset.name} → {job_name} → {output_dataset.name}")


if __name__ == "__main__":
    main()
