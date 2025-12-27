#!/usr/bin/env python3
"""Script to sync data from Marquez to FlowScope."""

import asyncio
from sqlmodel import Session
from flowspec.db.config import get_engine
from flowspec.db.init import create_tables
from flowspec.sync import MarquezClient, SyncService


async def main():
    """Main sync function."""
    print("Starting FlowScope sync from Marquez...")
    
    # Ensure tables exist
    create_tables()
    
    # Create database session
    engine = get_engine()
    with Session(engine) as session:
        # Create sync service
        marquez_client = MarquezClient()
        sync_service = SyncService(session, marquez_client)
        
        try:
            # Perform sync
            stats = await sync_service.sync_all()
            
            print("\n✅ Sync completed!")
            print(f"Namespaces: {stats['namespaces']}")
            print(f"Jobs: {stats['jobs']}")
            print(f"Datasets: {stats['datasets']}")
            print(f"Runs: {stats['runs']}")
            print(f"Edges: {stats['edges']}")
            
            if stats['errors']:
                print(f"\n⚠️  Errors: {len(stats['errors'])}")
                for error in stats['errors']:
                    print(f"  - {error}")
        finally:
            await marquez_client.close()


if __name__ == "__main__":
    asyncio.run(main())









