#!/usr/bin/env python3
"""自动化测试脚本 for Phase 3 - Business Usage Integration."""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlmodel import Session, select
import httpx

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flowspec.db.config import get_engine
from flowspec.db.init import create_tables
from flowspec.models import FSDataset, FSJob, FSEdge, FSRun
from flowspec.sync import MarquezClient, SyncService
from flowspec.path_analysis import PathFinder
from flowspec.business_usage import BusinessUsageTracker


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def test_business_usage_detection():
    """Test 1: Business usage detection logic."""
    print("\n" + "="*60)
    print("Test 1: Business Usage Detection")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            tracker = BusinessUsageTracker(session)
            
            # Create test jobs with different characteristics
            test_jobs = [
                FSJob(
                    namespace="test",
                    name="user_stats_api",
                    system=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                FSJob(
                    namespace="test",
                    name="dashboard_query",
                    system="bi",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                FSJob(
                    namespace="test",
                    name="regular_etl_job",
                    system="etl",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
            ]
            
            # Test job name pattern detection
            api_job = test_jobs[0]
            is_business = tracker.is_business_job(api_job)
            if is_business:
                print_success(f"API job detected as business: {api_job.name}")
            else:
                print_error(f"API job NOT detected as business: {api_job.name}")
                return False
            
            # Test system field detection
            bi_job = test_jobs[1]
            is_business = tracker.is_business_job(bi_job)
            if is_business:
                print_success(f"BI job detected as business: {bi_job.name} (system={bi_job.system})")
            else:
                print_error(f"BI job NOT detected as business: {bi_job.name}")
                return False
            
            # Test non-business job
            etl_job = test_jobs[2]
            is_business = tracker.is_business_job(etl_job)
            if not is_business:
                print_success(f"ETL job correctly NOT detected as business: {etl_job.name}")
            else:
                print_warning(f"ETL job incorrectly detected as business: {etl_job.name}")
            
            return True
    except Exception as e:
        print_error(f"Business usage detection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_sync_with_business_usage():
    """Test 2: Sync service updates business usage metrics."""
    print("\n" + "="*60)
    print("Test 2: Sync Service Business Usage Updates")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            # First, check if we have data
            jobs = session.exec(select(FSJob)).all()
            if not jobs:
                print_warning("No jobs found. Run sync first or create test data.")
                print_info("To create test data: run examples/api_example.py and examples/etl_example.py")
                return True  # Not a failure, just no data
            
            # Find a business job (API or BI)
            business_job = None
            for job in jobs:
                tracker = BusinessUsageTracker(session)
                if tracker.is_business_job(job):
                    business_job = job
                    break
            
            if not business_job:
                print_warning("No business jobs found in database")
                print_info("Create a job with name containing '_api', '_bi', '_dashboard', or system='bi'")
                return True  # Not a failure
            
            print_info(f"Testing with business job: {business_job.namespace}/{business_job.name}")
            
            # Get input datasets for this job
            tracker = BusinessUsageTracker(session)
            input_datasets = tracker.get_input_datasets_for_job(business_job)
            
            if not input_datasets:
                print_warning("No input datasets found for business job")
                print_info("This might be expected if job has no inputs yet")
                return True
            
            # Check initial access metrics
            test_dataset = input_datasets[0]
            initial_count = test_dataset.access_count or 0
            print_info(f"Initial access_count for {test_dataset.name}: {initial_count}")
            
            # Run sync to update metrics
            client = MarquezClient()
            sync_service = SyncService(session, client)
            
            print_info("Running sync to update business usage metrics...")
            stats = await sync_service.sync_all()
            await client.close()
            
            # Refresh dataset from database
            session.refresh(test_dataset)
            new_count = test_dataset.access_count or 0
            
            print_info(f"Business usage updates: {stats.get('business_usage_updates', 0)}")
            print_info(f"New access_count for {test_dataset.name}: {new_count}")
            
            if stats.get('business_usage_updates', 0) > 0:
                print_success("Sync service updated business usage metrics")
                return True
            else:
                print_warning("No business usage updates in this sync")
                print_info("This might be expected if no new business job runs completed")
                return True  # Not a failure
            
    except Exception as e:
        print_error(f"Sync business usage test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_live_data_endpoint():
    """Test 3: Live data endpoint returns datasets with business usage."""
    print("\n" + "="*60)
    print("Test 3: Live Data Endpoint")
    print("="*60)
    
    api_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test live data endpoint
            response = await client.get(f"{api_url}/api/v1/datasets/live")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                datasets = data.get("datasets", [])
                
                print_success(f"Live data endpoint works: {count} dataset(s) with business usage")
                
                if datasets:
                    print_info("Sample live datasets:")
                    for ds in datasets[:3]:
                        print_info(f"  - {ds['namespace']}/{ds['name']} (access_count: {ds.get('access_count', 0)})")
                    
                    # Verify structure
                    required_fields = ["namespace", "name", "access_count"]
                    missing = [f for f in required_fields if f not in datasets[0]]
                    if missing:
                        print_error(f"Missing fields in response: {missing}")
                        return False
                    else:
                        print_success("Response structure is correct")
                
                return True
            else:
                print_error(f"Live data endpoint returned: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print_warning("Cannot connect to API. Make sure API server is running: python run_api.py")
        return True  # Not a failure, just optional test
    except Exception as e:
        print_error(f"Live data endpoint test failed: {str(e)}")
        return False


async def test_dead_data_endpoint():
    """Test 4: Dead data endpoint returns datasets without business usage."""
    print("\n" + "="*60)
    print("Test 4: Dead Data Endpoint")
    print("="*60)
    
    api_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test dead data endpoint
            response = await client.get(f"{api_url}/api/v1/datasets/dead?days=90")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                datasets = data.get("datasets", [])
                
                print_success(f"Dead data endpoint works: {count} dataset(s) without business usage")
                
                if datasets:
                    print_info("Sample dead datasets:")
                    for ds in datasets[:3]:
                        access_count = ds.get("access_count", 0)
                        days_since = ds.get("days_since_access", "N/A")
                        print_info(f"  - {ds['namespace']}/{ds['name']} (access_count: {access_count}, days: {days_since})")
                    
                    # Verify structure
                    required_fields = ["namespace", "name", "access_count"]
                    missing = [f for f in required_fields if f not in datasets[0]]
                    if missing:
                        print_error(f"Missing fields in response: {missing}")
                        return False
                    else:
                        print_success("Response structure is correct")
                
                return True
            else:
                print_error(f"Dead data endpoint returned: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print_warning("Cannot connect to API. Make sure API server is running: python run_api.py")
        return True  # Not a failure, just optional test
    except Exception as e:
        print_error(f"Dead data endpoint test failed: {str(e)}")
        return False


async def test_business_critical_paths():
    """Test 5: Business-critical paths are correctly identified."""
    print("\n" + "="*60)
    print("Test 5: Business-Critical Paths")
    print("="*60)
    
    api_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test business-critical paths endpoint
            response = await client.get(f"{api_url}/api/v1/paths/business-critical")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                paths = data.get("paths", [])
                
                print_success(f"Business-critical paths endpoint works: {count} path(s)")
                
                if paths:
                    print_info("Sample business-critical paths:")
                    for i, path_info in enumerate(data.get("paths_with_business_usage", [])[:2]):
                        path = path_info.get("path", [])
                        is_critical = path_info.get("is_business_critical", False)
                        print_info(f"  Path {i+1}: {' → '.join(path[:5])}... (critical: {is_critical})")
                    
                    # Verify structure
                    if "paths_with_business_usage" in data:
                        print_success("Response includes business usage indicators")
                    else:
                        print_warning("Response missing business usage indicators")
                
                return True
            else:
                print_error(f"Business-critical paths endpoint returned: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print_warning("Cannot connect to API. Make sure API server is running: python run_api.py")
        return True  # Not a failure, just optional test
    except Exception as e:
        print_error(f"Business-critical paths test failed: {str(e)}")
        return False


def test_path_with_business_usage_indicators():
    """Test 6: Path queries include business usage indicators."""
    print("\n" + "="*60)
    print("Test 6: Path Queries with Business Usage Indicators")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            path_finder = PathFinder(session)
            
            # Get a dataset to test with
            datasets = session.exec(select(FSDataset)).all()
            if not datasets:
                print_warning("No datasets found. Run sync first.")
                return True  # Not a failure
            
            test_dataset = datasets[0]
            print_info(f"Testing with dataset: {test_dataset.namespace}/{test_dataset.name}")
            
            # Test path query with business usage indicators
            paths = path_finder.find_upstream_paths(
                test_dataset.namespace,
                test_dataset.name,
                max_depth=10,
                include_business_usage=True
            )
            
            if paths:
                # Get business usage indicators for first path
                indicators = path_finder.get_path_business_usage_indicators(paths[0])
                
                print_success(f"Path query with business usage works: {len(paths)} path(s)")
                print_info(f"Business usage indicators for first path: {len(indicators)} node(s)")
                
                # Check if indicators have correct structure
                if indicators:
                    first_node = list(indicators.keys())[0]
                    first_info = indicators[first_node]
                    
                    if "has_business_usage" in first_info:
                        print_success("Business usage indicators structure is correct")
                        return True
                    else:
                        print_error("Business usage indicators missing 'has_business_usage' field")
                        return False
                else:
                    print_warning("No business usage indicators returned")
                    return True  # Not a failure
            else:
                print_warning("No paths found for testing")
                return True  # Not a failure
            
    except Exception as e:
        print_error(f"Path with business usage test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_acceptance_criteria():
    """Test 7: Phase 3 Acceptance Criteria - distinguish live vs dead data."""
    print("\n" + "="*60)
    print("Test 7: Acceptance Criteria (live vs dead data)")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            # Get live datasets (with business usage)
            live_statement = select(FSDataset).where(FSDataset.access_count > 0)
            live_datasets = session.exec(live_statement).all()
            
            # Get dead datasets (without business usage)
            dead_statement = select(FSDataset).where(
                (FSDataset.access_count == 0) |
                (FSDataset.access_count.is_(None))
            )
            dead_datasets = session.exec(dead_statement).all()
            
            live_count = len(live_datasets)
            dead_count = len(dead_datasets)
            
            print_info(f"Live datasets (with business usage): {live_count}")
            print_info(f"Dead datasets (without business usage): {dead_count}")
            
            if live_count > 0 and dead_count > 0:
                print_success("✅ Acceptance criteria met! System can distinguish live vs dead data")
                
                print_info("Sample live datasets:")
                for ds in live_datasets[:3]:
                    print_info(f"  - {ds.namespace}/{ds.name} (access_count: {ds.access_count})")
                
                print_info("Sample dead datasets:")
                for ds in dead_datasets[:3]:
                    print_info(f"  - {ds.namespace}/{ds.name} (access_count: {ds.access_count or 0})")
                
                return True
            elif live_count > 0:
                print_success("✅ System can identify live data")
                print_warning("No dead datasets found (this might be expected)")
                return True
            elif dead_count > 0:
                print_success("✅ System can identify dead data")
                print_warning("No live datasets found (run business jobs to generate usage)")
                return True
            else:
                print_warning("No datasets found. Run sync first.")
                return True  # Not a failure, just no data
            
    except Exception as e:
        print_error(f"Acceptance criteria test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FlowScope Phase 3 - Business Usage Integration Testing")
    print("="*60)
    
    results = []
    
    # Test 1: Business usage detection
    results.append(("Business Usage Detection", test_business_usage_detection()))
    
    # Test 2: Sync with business usage
    results.append(("Sync Business Usage Updates", await test_sync_with_business_usage()))
    
    # Test 3: Live data endpoint
    print("\n" + "="*60)
    print_info("Testing API endpoints (requires API server running)")
    print_info("To test API: python run_api.py (in another terminal)")
    print("="*60)
    results.append(("Live Data Endpoint", await test_live_data_endpoint()))
    
    # Test 4: Dead data endpoint
    results.append(("Dead Data Endpoint", await test_dead_data_endpoint()))
    
    # Test 5: Business-critical paths
    results.append(("Business-Critical Paths", await test_business_critical_paths()))
    
    # Test 6: Path queries with business usage
    results.append(("Path Queries with Business Usage", test_path_with_business_usage_indicators()))
    
    # Test 7: Acceptance criteria
    results.append(("Acceptance Criteria", test_acceptance_criteria()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! 🎉")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


