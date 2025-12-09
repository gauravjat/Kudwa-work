"""
Simple test script to verify the system is working.
Run this after starting the API server.
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_load_data():
    """Test data loading."""
    print("\nTesting data load...")
    response = requests.post(f"{BASE_URL}/api/v1/data/load")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Data loaded: {data['total_records']} total records")
        print(f"   - QuickBooks: {data['quickbooks_records']}")
        print(f"   - Rootfi: {data['rootfi_records']}")
        return True
    else:
        print(f"❌ Data load failed: {response.text}")
        return False

def test_get_summary():
    """Test summary statistics."""
    print("\nTesting summary statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/data/summary")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Summary retrieved:")
        print(f"   - Total periods: {data['total_periods']}")
        print(f"   - Total revenue: ${data['total_revenue']:,.2f}")
        print(f"   - Total profit: ${data['total_profit']:,.2f}")
        return True
    else:
        print(f"❌ Summary failed: {response.text}")
        return False

def test_natural_language():
    """Test natural language querying."""
    print("\nTesting natural language query...")
    
    question = "What was the total revenue in 2024?"
    response = requests.post(
        f"{BASE_URL}/api/v1/ai/query",
        json={"question": question}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI query successful:")
        print(f"   Question: {question}")
        print(f"   Answer: {data['answer'][:200]}...")
        return True
    else:
        print(f"❌ AI query failed: {response.text}")
        return False

def test_insights():
    """Test insights generation."""
    print("\nTesting AI insights generation...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/ai/insights",
        json={}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Insights generated:")
        print(f"   Analyzing {data['period_count']} periods")
        print(f"   Insights: {data['insights'][:200]}...")
        return True
    else:
        print(f"❌ Insights failed: {response.text}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Financial Data Processing System - Test Suite")
    print("=" * 60)
    
    try:
        test_health()
        
        # Load data first
        if not test_load_data():
            print("\n⚠️  Data loading failed, but continuing tests...")
        
        test_get_summary()
        test_natural_language()
        test_insights()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server.")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


