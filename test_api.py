"""
Test script for the deployment API.
Run with: python test_api.py
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

# Test configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
SECRET_CODE = os.getenv("SECRET_CODE", "default_secret_change_me")
TEST_EMAIL = "test@example.com"

# Sample test data
def create_test_request_round_1():
    """Create a test request for Round 1."""
    return {
        "email": TEST_EMAIL,
        "secret": SECRET_CODE,
        "task": "test-hello-world",
        "round": 1,
        "nonce": "test-nonce-12345",
        "brief": "Create a simple hello world page with a greeting message and current time display",
        "checks": [
            "Has index.html file",
            "Has README.md file",
            "Has MIT LICENSE",
            "Page displays greeting message",
            "Page shows current time"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }

def create_test_request_round_2():
    """Create a test request for Round 2."""
    return {
        "email": TEST_EMAIL,
        "secret": SECRET_CODE,
        "task": "test-hello-world",
        "round": 2,
        "nonce": "test-nonce-67890",
        "brief": "Add a button that changes the background color when clicked and add a footer",
        "checks": [
            "Button exists",
            "Background color changes on button click",
            "Footer is present with copyright text"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }

def test_health_check():
    """Test the health check endpoint."""
    import requests
    
    print("\n" + "="*60)
    print("Testing Health Check Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_round_1():
    """Test Round 1 deployment."""
    import requests
    
    print("\n" + "="*60)
    print("Testing Round 1 - Initial Deployment")
    print("="*60)
    
    request_data = create_test_request_round_1()
    print(f"\nRequest Data:")
    print(json.dumps(request_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_URL}/deploy",
            json=request_data,
            timeout=120  # 2 minutes timeout for AI generation
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Round 1 deployment successful!")
            print(f"  Repository: {result.get('repo_url')}")
            print(f"  GitHub Pages: {result.get('pages_url')}")
            print(f"  Commit: {result.get('commit_sha')}")
            return True, result
        else:
            print(f"\n✗ Round 1 deployment failed")
            return False, None
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out (this can happen with AI generation)")
        return False, None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False, None

def test_round_2():
    """Test Round 2 update."""
    import requests
    
    print("\n" + "="*60)
    print("Testing Round 2 - Update Deployment")
    print("="*60)
    
    request_data = create_test_request_round_2()
    print(f"\nRequest Data:")
    print(json.dumps(request_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_URL}/deploy",
            json=request_data,
            timeout=120  # 2 minutes timeout for AI generation
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Round 2 update successful!")
            print(f"  Repository: {result.get('repo_url')}")
            print(f"  GitHub Pages: {result.get('pages_url')}")
            print(f"  Commit: {result.get('commit_sha')}")
            return True, result
        else:
            print(f"\n✗ Round 2 update failed")
            return False, None
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out")
        return False, None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False, None

def test_invalid_secret():
    """Test with invalid secret."""
    import requests
    
    print("\n" + "="*60)
    print("Testing Invalid Secret (Should Fail)")
    print("="*60)
    
    request_data = create_test_request_round_1()
    request_data["secret"] = "invalid_secret"
    
    try:
        response = requests.post(
            f"{API_URL}/deploy",
            json=request_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 403:
            print("\n✓ Correctly rejected invalid secret")
            return True
        else:
            print("\n✗ Should have rejected invalid secret")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "#"*60)
    print("# Deployment API Test Suite")
    print("#"*60)
    print(f"API URL: {API_URL}")
    print(f"Secret configured: {'Yes' if SECRET_CODE else 'No'}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Invalid Secret
    results.append(("Invalid Secret", test_invalid_secret()))
    
    # Test 3: Round 1 (this might take a while)
    print("\n⚠️  Round 1 test may take 30-60 seconds due to AI generation...")
    success, result = test_round_1()
    results.append(("Round 1 Deployment", success))
    
    # Test 4: Round 2 (only if Round 1 succeeded)
    if success:
        print("\n⚠️  Round 2 test may take 30-60 seconds...")
        import time
        time.sleep(2)  # Small delay between rounds
        success_r2, _ = test_round_2()
        results.append(("Round 2 Update", success_r2))
    else:
        print("\n⚠️  Skipping Round 2 test (Round 1 failed)")
        results.append(("Round 2 Update", None))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
        else:
            status = "⊘ SKIPPED"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, r in results if r is True)
    total = sum(1 for _, r in results if r is not None)
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Error: 'requests' module not installed")
        print("Install with: pip install requests")
        exit(1)
    
    # Check if dotenv is installed
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Warning: 'python-dotenv' not installed, using default values")
    
    run_all_tests()

