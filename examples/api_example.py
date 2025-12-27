#!/usr/bin/env python3
"""
Example API script that emits OpenLineage events to demonstrate data lineage.

This script simulates an API endpoint that:
1. Consumes data from a processed dataset (processed_users)
2. Returns aggregated results

The script emits OpenLineage events to track API usage of data lineage.
"""

import os
import uuid
from datetime import datetime
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.facet import SchemaDatasetFacet, SchemaField


def main():
    # Initialize OpenLineage client
    marquez_url = os.getenv("MARQUEZ_URL", "http://localhost:5002")
    client = OpenLineageClient(url=marquez_url)

    # Define job and run details
    namespace = "flowspec_examples"
    job_name = "user_stats_api"
    run_id = str(uuid.uuid4())

    # Create Job and Run instances
    job = Job(namespace=namespace, name=job_name)
    run = Run(run_id)

    # Define input dataset (consumed by API)
    input_schema = SchemaDatasetFacet(
        fields=[
            SchemaField(name="user_id", type="integer"),
            SchemaField(name="full_name", type="string"),
            SchemaField(name="email_address", type="string"),
            SchemaField(name="registration_date", type="timestamp")
        ]
    )

    input_dataset = Dataset(
        namespace="postgresql://localhost:5432",
        name="processed.users",
        facets={"schema": input_schema}
    )

    # Define output dataset (API response)
    output_schema = SchemaDatasetFacet(
        fields=[
            SchemaField(name="total_users", type="integer"),
            SchemaField(name="avg_registrations_per_day", type="float"),
            SchemaField(name="generated_at", type="timestamp")
        ]
    )

    output_dataset = Dataset(
        namespace="api://localhost:8000",
        name="user_stats",
        facets={"schema": output_schema}
    )

    # Emit START event
    print(f"Starting API job: {job_name} (run_id: {run_id})")
    start_event = RunEvent(
        eventType=RunState.START,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=run,
        job=job,
        inputs=[input_dataset],
        producer="https://github.com/flowspec/api_example"
    )
    client.emit(start_event)
    print("✓ Emitted START event")

    # Simulate API processing
    print("Processing API request...")
    # In a real scenario, this would:
    # 1. Query processed.users
    # 2. Calculate statistics
    # 3. Return JSON response
    import time
    time.sleep(0.5)  # Simulate processing time

    # Emit COMPLETE event
    print(f"Completing API job: {job_name}")
    complete_event = RunEvent(
        eventType=RunState.COMPLETE,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=run,
        job=job,
        inputs=[input_dataset],
        outputs=[output_dataset],
        producer="https://github.com/flowspec/api_example"
    )
    client.emit(complete_event)
    print("✓ Emitted COMPLETE event with inputs and outputs")
    print(f"✓ Lineage chain: {input_dataset.name} → {job_name} → {output_dataset.name}")


if __name__ == "__main__":
    main()
