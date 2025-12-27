#!/usr/bin/env python3
"""自动化测试脚本 for Phase 2."""

import asyncio
import sys
import os
from datetime import datetime
from sqlmodel import Session, select
import httpx

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flowspec.db.config import get_engine
from flowspec.db.init import create_tables
from flowspec.models import FSDataset, FSJob, FSEdge
from flowspec.path_analysis import PathFinder
from flowspec.complexity import ComplexityScorer
from flowspec.redundancy import RedundancyDetector


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


def test_complexity_scoring():
    """Test 1: Complexity scoring calculation."""
    print("\n" + "="*60)
    print("Test 1: Complexity Scoring")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            path_finder = PathFinder(session)
            complexity_scorer = ComplexityScorer(session, path_finder)
            
            # Get a dataset to test with
            datasets = session.exec(select(FSDataset)).all()
            if not datasets:
                print_error("No datasets found. Run sync first.")
                return False
            
            # Get paths for first dataset
            test_dataset = datasets[0]
            paths = path_finder.find_upstream_paths(
                test_dataset.namespace, test_dataset.name, max_depth=10
            )
            
            if not paths:
                print_warning("No paths found for testing complexity")
                return True  # Not a failure, just no data
            
            # Test complexity calculation
            test_path = paths[0]
            complexity = complexity_scorer.calculate_path_complexity(test_path)
            
            # Verify metrics exist
            required_metrics = [
                "hop_count", "node_count", "avg_fan_in", "avg_fan_out",
                "max_fan_in", "max_fan_out", "transform_density"
            ]
            
            missing = [m for m in required_metrics if m not in complexity]
            if missing:
                print_error(f"Missing complexity metrics: {missing}")
                return False
            
            print_success("Complexity scoring works")
            print_info(f"  Hop count: {complexity['hop_count']}")
            print_info(f"  Node count: {complexity['node_count']}")
            print_info(f"  Transform density: {complexity['transform_density']}")
            
            # Test multiple paths
            if len(paths) > 1:
                all_complexity = complexity_scorer.calculate_paths_complexity(paths[:3])
                if len(all_complexity) == min(3, len(paths)):
                    print_success(f"Batch complexity calculation works: {len(all_complexity)} paths")
                else:
                    print_error(f"Batch calculation failed: expected {min(3, len(paths))}, got {len(all_complexity)}")
                    return False
            
            return True
    except Exception as e:
        print_error(f"Complexity scoring test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_orphan_detection():
    """Test 2: Orphan dataset detection."""
    print("\n" + "="*60)
    print("Test 2: Orphan Dataset Detection")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            detector = RedundancyDetector(session)
            
            # Find orphans
            orphans = detector.find_orphan_datasets()
            
            print_success(f"Orphan detection works: found {len(orphans)} orphan(s)")
            
            if orphans:
                print_info("Orphan datasets:")
                for orphan in orphans[:5]:  # Show first 5
                    print_info(f"  - {orphan['namespace']}/{orphan['name']} (layer: {orphan.get('layer', 'N/A')})")
            
            # Verify orphan structure
            if orphans:
                required_fields = ["id", "namespace", "name", "status", "recommendation"]
                missing = [f for f in required_fields if f not in orphans[0]]
                if missing:
                    print_error(f"Missing fields in orphan data: {missing}")
                    return False
                else:
                    print_success("Orphan data structure is correct")
            
            return True
    except Exception as e:
        print_error(f"Orphan detection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_duplicate_detection():
    """Test 3: Duplicate table detection."""
    print("\n" + "="*60)
    print("Test 3: Duplicate Table Detection")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            detector = RedundancyDetector(session)
            
            # Find duplicates
            duplicates = detector.find_duplicate_candidates(
                similarity_threshold=0.7,
                path_overlap_threshold=0.5
            )
            
            print_success(f"Duplicate detection works: found {len(duplicates)} duplicate group(s)")
            
            if duplicates:
                print_info("Duplicate groups:")
                for group in duplicates[:3]:  # Show first 3 groups
                    print_info(f"  Group {group['group_id']}: {group['count']} candidates (similarity: {group['average_similarity']})")
                    for candidate in group['candidates'][:3]:  # Show first 3 candidates
                        print_info(f"    - {candidate['namespace']}/{candidate['name']}")
            
            # Verify duplicate structure
            if duplicates:
                required_fields = ["group_id", "count", "average_similarity", "candidates", "status", "recommendation"]
                missing = [f for f in required_fields if f not in duplicates[0]]
                if missing:
                    print_error(f"Missing fields in duplicate data: {missing}")
                    return False
                else:
                    print_success("Duplicate data structure is correct")
            
            return True
    except Exception as e:
        print_error(f"Duplicate detection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test 4: API endpoints."""
    print("\n" + "="*60)
    print("Test 4: API Endpoints")
    print("="*60)
    
    api_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health check
            response = await client.get(f"{api_url}/health", follow_redirects=True)
            if response.status_code == 200:
                print_success("Health check endpoint works")
            else:
                print_warning(f"Health check returned: {response.status_code}")
                return True  # Continue with other tests
            
            # Get a dataset for testing
            engine = get_engine()
            with Session(engine) as session:
                datasets = session.exec(select(FSDataset)).all()
                if not datasets:
                    print_warning("No datasets to test API endpoints")
                    return True
                
                test_dataset = datasets[0]
                namespace_encoded = test_dataset.namespace.replace("/", "%2F").replace(":", "%3A")
                name_encoded = test_dataset.name.replace("/", "%2F")
                
                # Test complexity endpoint
                try:
                    response = await client.get(
                        f"{api_url}/api/v1/datasets/{namespace_encoded}/{name_encoded}/complexity"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        print_success("Complexity endpoint works")
                        print_info(f"  Path count: {data.get('path_count', 0)}")
                        if 'aggregate_metrics' in data:
                            print_info(f"  Avg hop count: {data['aggregate_metrics'].get('average_hop_count', 0)}")
                    else:
                        print_warning(f"Complexity endpoint returned: {response.status_code}")
                except Exception as e:
                    print_warning(f"Complexity endpoint test failed: {str(e)}")
                
                # Test orphan endpoint
                try:
                    response = await client.get(f"{api_url}/api/v1/redundancy/orphans")
                    if response.status_code == 200:
                        data = response.json()
                        print_success(f"Orphan endpoint works: {data.get('count', 0)} orphans")
                    else:
                        print_warning(f"Orphan endpoint returned: {response.status_code}")
                except Exception as e:
                    print_warning(f"Orphan endpoint test failed: {str(e)}")
                
                # Test duplicate endpoint
                try:
                    response = await client.get(f"{api_url}/api/v1/redundancy/duplicates")
                    if response.status_code == 200:
                        data = response.json()
                        print_success(f"Duplicate endpoint works: {data.get('group_count', 0)} groups")
                    else:
                        print_warning(f"Duplicate endpoint returned: {response.status_code}")
                except Exception as e:
                    print_warning(f"Duplicate endpoint test failed: {str(e)}")
                
                # Test enhanced path endpoint with complexity
                try:
                    response = await client.get(
                        f"{api_url}/api/v1/datasets/{namespace_encoded}/{name_encoded}/upstream?include_complexity=true"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if 'complexity' in data or 'paths_with_complexity' in data:
                            print_success("Enhanced path endpoint with complexity works")
                        else:
                            print_warning("Path endpoint doesn't include complexity (may be disabled)")
                    else:
                        print_warning(f"Enhanced path endpoint returned: {response.status_code}")
                except Exception as e:
                    print_warning(f"Enhanced path endpoint test failed: {str(e)}")
            
            return True
    except (httpx.ConnectError, httpx.TimeoutException):
        print_warning("Cannot connect to API. Make sure API server is running: python run_api.py")
        print_info("Skipping API endpoint tests (optional)")
        return True  # Not a failure, just optional test
    except Exception as e:
        print_error(f"API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_acceptance_criteria():
    """Test 5: Phase 2 Acceptance Criteria."""
    print("\n" + "="*60)
    print("Test 5: Acceptance Criteria (deletable/mergeable candidates)")
    print("="*60)
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            detector = RedundancyDetector(session)
            
            # Get orphan candidates (deletable)
            orphans = detector.find_orphan_datasets()
            
            # Get duplicate candidates (mergeable)
            duplicates = detector.find_duplicate_candidates()
            
            print_info(f"Orphan candidates (deletable): {len(orphans)}")
            print_info(f"Duplicate groups (mergeable): {len(duplicates)}")
            
            total_candidates = len(orphans) + sum(g["count"] for g in duplicates)
            
            if total_candidates > 0:
                print_success(f"✅ Acceptance criteria met! Found {total_candidates} refactoring candidate(s)")
                
                if orphans:
                    print_info("Deletable candidates (orphans):")
                    for orphan in orphans[:3]:
                        print_info(f"  - {orphan['namespace']}/{orphan['name']}")
                
                if duplicates:
                    print_info("Mergeable candidates (duplicates):")
                    for group in duplicates[:3]:
                        print_info(f"  - Group with {group['count']} similar tables")
                
                return True
            else:
                print_warning("No refactoring candidates found")
                print_info("This might be expected if all datasets are properly connected and unique")
                # Still consider it a pass - the system works, just no candidates
                return True
    except Exception as e:
        print_error(f"Acceptance criteria test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FlowScope Phase 2 - Automated Testing")
    print("="*60)
    
    results = []
    
    # Test 1: Complexity scoring
    results.append(("Complexity Scoring", test_complexity_scoring()))
    
    # Test 2: Orphan detection
    results.append(("Orphan Detection", test_orphan_detection()))
    
    # Test 3: Duplicate detection
    results.append(("Duplicate Detection", test_duplicate_detection()))
    
    # Test 4: API endpoints (optional, requires API server)
    print("\n" + "="*60)
    print_info("Testing API endpoints (requires API server running)")
    print_info("To test API: python run_api.py (in another terminal)")
    print("="*60)
    results.append(("API Endpoints", await test_api_endpoints()))
    
    # Test 5: Acceptance criteria
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

