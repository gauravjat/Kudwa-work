"""
Script to load financial data into database.
Run this after initializing the database.
"""
from app.database import SessionLocal, init_db
from app.services.data_service import DataService


def main():
    """Load data from both sources."""
    print("Initializing database...")
    init_db()
    
    print("Loading financial data...")
    db = SessionLocal()
    
    try:
        data_service = DataService(db)
        result = data_service.load_data_from_sources()
        
        print(f"\n✅ Data loaded successfully!")
        print(f"   - QuickBooks records: {result['quickbooks_records']}")
        print(f"   - Rootfi records: {result['rootfi_records']}")
        print(f"   - Total records: {result['total_records']}")
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


