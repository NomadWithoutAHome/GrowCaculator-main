#!/usr/bin/env python3
"""
Test script to verify Vercel setup works locally.
Run this to test the Vercel-compatible version of the app.
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from api.index import app
        print("✅ Successfully imported Vercel app")
    except ImportError as e:
        print(f"❌ Failed to import Vercel app: {e}")
        return False
    
    try:
        from services.vercel_shared_results_service import vercel_shared_results_service
        print("✅ Successfully imported Vercel shared results service")
    except ImportError as e:
        print(f"❌ Failed to import Vercel shared results service: {e}")
        return False
    
    try:
        from services.calculator_service import calculator_service
        print("✅ Successfully imported calculator service")
    except ImportError as e:
        print(f"❌ Failed to import calculator service: {e}")
        return False
    
    try:
        from models.calculator import CalculationRequest, CalculationResponse
        print("✅ Successfully imported calculator models")
    except ImportError as e:
        print(f"❌ Failed to import calculator models: {e}")
        return False
    
    return True

def test_calculator_service():
    """Test that the calculator service works correctly."""
    print("\nTesting calculator service...")
    
    try:
        from services.calculator_service import calculator_service
        
        # Test getting plants
        plants = calculator_service.get_plants()
        print(f"✅ Found {len(plants)} plants")
        
        # Test getting mutations
        mutations = calculator_service.get_mutations()
        print(f"✅ Found {len(mutations)} mutations")
        
        # Test getting variants
        variants = calculator_service.get_variants()
        print(f"✅ Found {len(variants)} variants")
        
        # Test a simple calculation
        result = calculator_service.calculate_full_value(
            plant_name="Carrot",
            variant="Normal",
            weight=0.275,
            mutations=[],
            plant_amount=1
        )
        print(f"✅ Calculation successful: {result.final_value} Sheckles")
        
        return True
        
    except Exception as e:
        print(f"❌ Calculator service test failed: {e}")
        return False

def test_vercel_service():
    """Test that the Vercel shared results service works."""
    print("\nTesting Vercel shared results service...")
    
    try:
        from services.vercel_shared_results_service import vercel_shared_results_service
        
        # Test creating a shared result
        test_data = {
            'plant': 'Carrot',
            'variant': 'Normal',
            'mutations': ['Tranquil'],
            'weight': 0.275,
            'amount': 1,
            'result_value': '100 Sheckles',
            'final_sheckles': '100',
            'total_value': '100',
            'total_multiplier': '2.0x',
            'mutation_breakdown': 'Tranquil (+1.0)',
            'weight_min': '0.19',
            'weight_max': '0.39'
        }
        
        success = vercel_shared_results_service.create_shared_result(test_data)
        if success:
            print("✅ Successfully created shared result")
        else:
            print("❌ Failed to create shared result")
            return False
        
        # Test retrieving the shared result
        share_id = test_data.get('share_id')
        if share_id:
            result = vercel_shared_results_service.get_shared_result(share_id)
            if result:
                print("✅ Successfully retrieved shared result")
            else:
                print("❌ Failed to retrieve shared result")
                return False
        
        # Test cleanup
        deleted_count = vercel_shared_results_service.cleanup_expired_results()
        print(f"✅ Cleanup successful, deleted {deleted_count} expired results")
        
        return True
        
    except Exception as e:
        print(f"❌ Vercel service test failed: {e}")
        return False

def test_app_routes():
    """Test that the FastAPI app has the expected routes."""
    print("\nTesting FastAPI app routes...")
    
    try:
        from api.index import app
        
        # Check that the app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ App has {len(routes)} routes")
        
        # Check for key routes
        key_routes = ['/', '/mutation-calculator', '/about', '/share/{share_id}']
        for route in key_routes:
            if any(route in r for r in routes):
                print(f"✅ Found route: {route}")
            else:
                print(f"⚠️  Route not found: {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ App routes test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Vercel setup for GrowCalculator\n")
    
    tests = [
        test_imports,
        test_calculator_service,
        test_vercel_service,
        test_app_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Vercel setup is ready for deployment.")
        print("\nNext steps:")
        print("1. Commit your changes to Git")
        print("2. Deploy to Vercel using the dashboard or CLI")
        print("3. Check VERCEL_DEPLOYMENT.md for detailed instructions")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
